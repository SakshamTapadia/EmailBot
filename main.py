import smtplib
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage


def send_email():
    email_address = email_entry.get()
    email_password = password_entry.get()
    smtp_server = smtp_entry.get()
    smtp_port = int(port_entry.get())
    recipients = recipients_entry.get().split(',')
    subject = subject_entry.get()
    message = message_text.get("1.0", "end-1c")
    attachment_pdf_path = pdf_file_path
    attachment_image_path = image_file_path

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)

        for recipient in recipients:
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['Subject'] = subject
            msg['To'] = recipient

            msg.attach(MIMEText(message, 'html'))

            with open(attachment_pdf_path, "rb") as pdf_attachment_file:
                pdf_attachment = MIMEApplication(pdf_attachment_file.read(), _subtype="pdf")
                pdf_attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename="File.pdf"
                )
                msg.attach(pdf_attachment)

            with open(attachment_image_path, "rb") as image_attachment_file:
                image_attachment = MIMEImage(image_attachment_file.read(), _subtype="jpg")
                image_attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename="File.jpg"
                )
                msg.attach(image_attachment)

            server.sendmail(email_address, recipient, msg.as_string())
            status_label.config(text=f"Email sent to {recipient}")

        server.quit()
        status_label.config(text="All emails sent successfully")

    except Exception as e:
        status_label.config(text=f"Error: {str(e)}")


def browse_pdf():
    global pdf_file_path
    pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    pdf_label.config(text=pdf_file_path)


def browse_image():
    global image_file_path
    image_file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
    image_label.config(text=image_file_path)


# Create the main window
window = tk.Tk()
window.title("Email Sender")
window.geometry("900x600")

# Create and arrange widgets
email_label = ttk.Label(window, text="Email Address:")
email_label.grid(row=0, column=0)
email_entry = ttk.Entry(window, width=40)  # Increased width
email_entry.grid(row=0, column=1)

password_label = ttk.Label(window, text="Password:")
password_label.grid(row=1, column=0)
password_entry = ttk.Entry(window, show="*", width=40)  # Increased width
password_entry.grid(row=1, column=1)

smtp_label = ttk.Label(window, text="SMTP Server:")
smtp_label.grid(row=2, column=0)
smtp_entry = ttk.Entry(window, width=40)  # Increased width
smtp_entry.grid(row=2, column=1)

port_label = ttk.Label(window, text="SMTP Port:")
port_label.grid(row=3, column=0)
port_entry = ttk.Entry(window, width=40)  # Increased width
port_entry.grid(row=3, column=1)

recipients_label = ttk.Label(window, text="Recipients (comma-separated):")
recipients_label.grid(row=4, column=0)
recipients_entry = ttk.Entry(window, width=40)  # Increased width
recipients_entry.grid(row=4, column=1)

subject_label = ttk.Label(window, text="Subject:")
subject_label.grid(row=5, column=0)
subject_entry = ttk.Entry(window, width=40)  # Increased width
subject_entry.grid(row=5, column=1)

message_label = ttk.Label(window, text="Message:")
message_label.grid(row=6, column=0)
message_text = tk.Text(window, height=10, width=60)  # Increased height and width
message_text.grid(row=6, column=1)

pdf_button = ttk.Button(window, text="Browse PDF", command=browse_pdf)
pdf_button.grid(row=7, column=0)
pdf_label = ttk.Label(window, text="", width=40)  # Increased width
pdf_label.grid(row=7, column=1)

image_button = ttk.Button(window, text="Browse Image", command=browse_image)
image_button.grid(row=8, column=0)
image_label = ttk.Label(window, text="", width=40)  # Increased width
image_label.grid(row=8, column=1)

send_button = ttk.Button(window, text="Send Email", command=send_email, width=40)  # Increased width
send_button.grid(row=9, columnspan=2)

status_label = ttk.Label(window, text="", width=40)  # Increased width
status_label.grid(row=10, columnspan=2)

made_by_label = ttk.Label(window, text="Made by Saksham", font=("Helvetica", 12))
for i in range(13):  # Adjust as needed based on the number of widgets
    window.grid_rowconfigure(i, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)

# Start the GUI main loop
window.mainloop()
