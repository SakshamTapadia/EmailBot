import os

import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
import logging
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET").encode() if os.environ.get("SESSION_SECRET") else 'dev'.encode()

app.config['MAIL_SERVER'] = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('SMTP_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('SMTP_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('SMTP_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('SMTP_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('SMTP_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('SMTP_FROM_EMAIL')

mail = Mail(app)

scheduler = BackgroundScheduler(timezone=utc)
scheduler.start()

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
ALLOWED_ATTACHMENTS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls','.zip','.rar'}
MAX_CONTENT_LENGTH = 24 * 1024 * 1024  
BATCH_SIZE = 50 
PAUSE_DURATION = 30  
MAX_WORKERS = 3 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_attachment(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_ATTACHMENTS

def validate_email_settings():
    required_settings = ['SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_FROM_EMAIL']
    missing = [setting for setting in required_settings if not os.environ.get(setting)]
    if missing:
        missing_str = ', '.join(missing)
        flash(f'Missing email configuration: {missing_str}', 'error')
        return False
    return True

def send_email_with_attachments(recipient_email, subject, content, attachment_paths=None):
    """Helper function to send a single email with attachments"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=content
        )

        if attachment_paths:
            for filename, filepath in attachment_paths.items():
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        msg.attach(filename, 'application/octet-stream', f.read())

        mail.send(msg)
        logging.debug(f"Successfully sent email to {recipient_email}")
        return True, recipient_email
    except Exception as e:
        logging.error(f"Error sending to {recipient_email}: {str(e)}")
        return False, recipient_email

def send_emails_in_batches(subject, content, recipients, attachment_paths=None):
    """Send emails in batches with pauses"""
    sent_count = 0
    failed_count = 0
    total_recipients = len(recipients)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for i in range(0, total_recipients, BATCH_SIZE):
            batch = recipients[i:i + BATCH_SIZE]
            
            send_func = partial(
                send_email_with_attachments,
                subject=subject,
                content=content,
                attachment_paths=attachment_paths
            )
            
            futures = [executor.submit(send_func, recipient) for recipient in batch]
            
            for future in futures:
                success, recipient = future.result()
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
            
            progress = min((i + BATCH_SIZE), total_recipients)
            logging.info(f"Progress: {progress}/{total_recipients} emails processed")
            
            if progress < total_recipients:
                logging.info(f"Pausing for {PAUSE_DURATION} seconds")
                time.sleep(PAUSE_DURATION)

    return sent_count, failed_count

def send_scheduled_email(subject, content, recipients, attachment_paths=None):
    with app.app_context():
        try:
            logging.info(f"Starting scheduled email campaign at {datetime.now()}")
            logging.info(f"Recipients: {len(recipients)}, Attachments: {len(attachment_paths or {})}")
            
            if attachment_paths:
                missing_attachments = []
                for filename, filepath in attachment_paths.items():
                    if not os.path.exists(filepath):
                        missing_attachments.append(filename)
                        logging.error(f"Attachment missing at schedule time: {filepath}")
                
                if missing_attachments:
                    raise Exception(f"Missing attachments: {', '.join(missing_attachments)}")

            sent_count, failed_count = send_emails_in_batches(
                subject, content, recipients, attachment_paths
            )
            
            # Cleanup attachments
            if attachment_paths:
                for filepath in attachment_paths.values():
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            logging.debug(f"Cleaned up scheduled attachment: {filepath}")
                    except Exception as e:
                        logging.error(f"Error cleaning up scheduled attachment: {str(e)}")

            logging.info(f"Scheduled campaign completed at {datetime.now()}")
            logging.info(f"Results: {sent_count} sent, {failed_count} failed")

            # Store results
            scheduled_results = {
                'timestamp': datetime.now().isoformat(),
                'sent_count': sent_count,
                'failed_count': failed_count,
                'total_recipients': len(recipients)
            }
            
            return scheduled_results

        except Exception as e:
            logging.error(f"Critical error in scheduled email: {str(e)}")
            raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload CSV or Excel file.', 'error')
        return redirect(url_for('index'))

    try:
        temp_dir = tempfile.gettempdir()
        filename = secure_filename(file.filename)
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)

        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath, engine='openpyxl')

            if 'email' not in df.columns:
                if len(df.columns) == 1:
                    df.columns = ['email']
                else:
                    flash('File must contain an "email" column or a single column of email addresses', 'error')
                    return redirect(url_for('index'))

            session['recipients'] = df['email'].dropna().tolist()
            flash(f'Successfully loaded {len(df)} recipients', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            logging.error(f"Error reading file: {str(e)}")
            flash('Error reading file. Please ensure it contains valid email addresses.', 'error')
            return redirect(url_for('index'))

    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        flash('Error processing file', 'error')
        return redirect(url_for('index'))

    finally:
        if 'filepath' in locals():
            os.remove(filepath)

@app.route('/preview', methods=['POST'])
def preview():
    if not validate_email_settings():
        return redirect(url_for('index'))

    subject = request.form.get('subject', '')
    content = request.form.get('content', '')
    recipients = session.get('recipients', [])
    attachments = []

    send_option = request.form.get('send_option', 'now')
    schedule_date = request.form.get('schedule_date')
    schedule_time = request.form.get('schedule_time')

    if send_option == 'scheduled' and (not schedule_date or not schedule_time):
        flash('Please select both date and time for scheduled sending', 'error')
        return redirect(url_for('index'))

    if 'attachments' in request.files:
        files = request.files.getlist('attachments')
        logging.debug(f"Processing {len(files)} attachments")

        if 'attachment_paths' not in session:
            session['attachment_paths'] = {}

        for file in files:
            if file.filename and allowed_attachment(file.filename):
                filename = secure_filename(file.filename)
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, filename)
                file.save(filepath)
                attachments.append(filename)
                session['attachment_paths'][filename] = filepath
                logging.debug(f"Saved attachment at: {filepath}")

    if not recipients:
        flash('Please upload recipients first', 'error')
        return redirect(url_for('index'))

    if send_option == 'scheduled':
        try:
            schedule_dt = datetime.strptime(f"{schedule_date} {schedule_time}", '%Y-%m-%d %H:%M')
            if schedule_dt <= datetime.now():
                flash('Please select a future date and time', 'error')
                return redirect(url_for('index'))
            session['schedule_datetime'] = f"{schedule_date} {schedule_time}"
        except ValueError as e:
            logging.error(f"Error parsing schedule datetime: {str(e)}")
            flash('Invalid date or time format', 'error')
            return redirect(url_for('index'))
    else:
        session.pop('schedule_datetime', None)

    return render_template('preview.html', 
                         subject=subject, 
                         content=content, 
                         recipient_count=len(recipients),
                         attachments=attachments,
                         scheduled_time=session.get('schedule_datetime'))

@app.route('/send', methods=['POST'])
def send_emails():
    if not validate_email_settings():
        return redirect(url_for('index'))

    subject = request.form.get('subject', '')
    content = request.form.get('content', '')
    recipients = session.get('recipients', [])
    attachment_paths = session.get('attachment_paths', {})
    scheduled_time = session.get('schedule_datetime')

    if not all([subject, content, recipients]):
        flash('Missing required information', 'error')
        return redirect(url_for('index'))

    try:
        if scheduled_time:
            try:
                schedule_dt = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M')
                current_dt = datetime.now()

                if schedule_dt <= current_dt:
                    flash('Scheduled time must be in the future', 'error')
                    return redirect(url_for('index'))

                delay = (schedule_dt - current_dt).total_seconds()
                if delay > 30 * 24 * 60 * 60:  
                    flash('Schedule time cannot be more than 30 days in the future', 'error')
                    return redirect(url_for('index'))

                campaign_id = f"email_campaign_{datetime.now().timestamp()}"
                campaign_details = {
                    'id': campaign_id,
                    'schedule_time': scheduled_time,
                    'recipient_count': len(recipients),
                    'subject': subject,
                    'attachment_count': len(attachment_paths),
                    'status': 'scheduled'
                }
                
                if 'scheduled_campaigns' not in session:
                    session['scheduled_campaigns'] = {}
                session['scheduled_campaigns'][campaign_id] = campaign_details

                scheduler.add_job(
                    send_scheduled_email,
                    'date',
                    run_date=schedule_dt,
                    args=[subject, content, recipients, attachment_paths],
                    id=campaign_id,
                    name=f"Email Campaign - {subject}",
                    misfire_grace_time=3600
                )

                flash(f'Email campaign scheduled for {scheduled_time}', 'success')
                return redirect(url_for('status'))

            except ValueError as e:
                logging.error(f"Error scheduling email: {str(e)}")
                flash('Invalid schedule format. Please use correct date and time.', 'error')
                return redirect(url_for('index'))

        else:
            sent_count, failed_count = send_emails_in_batches(
                subject, content, recipients, attachment_paths
            )

            for filepath in attachment_paths.values():
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as cleanup_error:
                    logging.error(f"Error cleaning up file: {str(cleanup_error)}")

            session.pop('attachment_paths', None)
            session.pop('schedule_datetime', None)

            flash(f'Sent {sent_count} emails, {failed_count} failed', 
                  'success' if failed_count == 0 else 'warning')
            return redirect(url_for('status'))

    except Exception as e:
        logging.error(f"Error in send_emails: {str(e)}")
        flash('Error sending emails', 'error')
        return redirect(url_for('index'))

@app.route('/status')
def status():
    recipients = session.get('recipients', [])
    scheduled_time = session.get('schedule_datetime')
    scheduled_campaigns = session.get('scheduled_campaigns', {})
    
    active_jobs = scheduler.get_jobs()
    active_job_ids = [job.id for job in active_jobs]
    
    for campaign_id, campaign in scheduled_campaigns.items():
        if campaign_id not in active_job_ids and campaign['status'] == 'scheduled':
            campaign['status'] = 'completed'
    
    return render_template('status.html', 
                         recipient_count=len(recipients) if recipients else 0,
                         scheduled_time=scheduled_time,
                         scheduled_campaigns=scheduled_campaigns)

if __name__ == '__main__':
    app.run()