# Email Campaign Manager

## Overview
This project is a Flask-based web application that allows users to create and manage email campaigns efficiently. It supports bulk email sending, scheduling, attachment uploads, and real-time status tracking.

## Features
- **Upload Recipients:** Accepts CSV or Excel files containing email addresses.
- **Compose Emails:** Users can enter email subject and content.
- **Attachments:** Supports multiple file types including PDF, DOCX, TXT, and images.
- **Scheduling:** Allows users to send emails immediately or schedule them for later.
- **Batch Processing:** Emails are sent in batches to prevent overload.
- **Progress Tracking:** Displays real-time progress and success/failure rates.
- **Flask-Mail Integration:** Uses SMTP settings for secure email delivery.
- **Error Handling & Logging:** Logs email delivery status and errors.

## Technologies Used
- **Backend:** Flask, Flask-Mail, APScheduler
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Bootstrap, Custom CSS
- **Storage:** Session-based recipient management
- **Concurrency:** ThreadPoolExecutor for batch email processing

## Installation & Setup
### Prerequisites
Ensure you have Python installed and set up the following dependencies:

```sh
pip install -r requirements.txt
```

### Environment Variables
Set up SMTP credentials in a `.env` file or environment variables:
```sh
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

### Running the Application
```sh
python app.py
```
The application runs on `http://127.0.0.1:5000/` by default.

## Usage
1. **Upload Recipients:** Upload a CSV or Excel file with an `email` column.
2. **Compose Email:** Fill in the subject and content.
3. **Attach Files:** (Optional) Add documents or images.
4. **Schedule or Send:** Choose immediate sending or schedule for later.
5. **Monitor Progress:** Track status in the dashboard.

## File Structure
```
|-- app.py           # Backend logic & email scheduling
|-- requirements.txt # Dependencies
|-- LICENSE          # License file
|-- README.md        # Project documentation
|-- templates/       # HTML templates
|   |-- index.html   # Frontend UI
|-- static/          # Static files
|   |-- css/         # CSS stylesheets
|   |   |-- style.css # Styling and responsiveness
|   |-- js/          # JavaScript files
|   |   |-- main.js  # Form validation & interactivity
```

## License
This project is open-source under the MIT License.

