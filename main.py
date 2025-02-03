import smtplib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import formatdate
import os

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Sender")
        self.root.geometry("900x600")
        self.pdf_file_path = ""
        self.image_file_path = ""
        self.create_widgets()

    def create_widgets(self):
        # Email Address
        ttk.Label(self.root, text="Email Address:").grid(row=0, column=0, sticky="w")
        self.email_entry = ttk.Entry(self.root, width=40)
        self.email_entry.grid(row=0, column=1, padx=10, pady=5)

        # Password
        ttk.Label(self.root, text="Password:").grid(row=1, column=0, sticky="w")
        self.password_entry = ttk.Entry(self.root, show="*", width=40)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        # SMTP Server
        ttk.Label(self.root, text="SMTP Server:").grid(row=2, column=0, sticky="w")
        self.smtp_entry = ttk.Entry(self.root, width=40)
        self.smtp_entry.grid(row=2, column=1, padx=10, pady=5)

        # SMTP Port
        ttk.Label(self.root, text="SMTP Port:").grid(row=3, column=0, sticky="w")
        self.port_entry = ttk.Entry(self.root, width=40)
        self.port_entry.grid(row=3, column=1, padx=10, pady=5)

        # Recipients
        ttk.Label(self.root, text="Recipients (comma-separated):").grid(row=4, column=0, sticky="w")
        self.recipients_entry = ttk.Entry(self.root, width=40)
        self.recipients_entry.grid(row=4, column=1, padx=10, pady=5)

        # Subject
        ttk.Label(self.root, text="Subject:").grid(row=5, column=0, sticky="w")
        self.subject_entry = ttk.Entry(self.root, width=40)
        self.subject_entry.grid(row=5, column=1, padx=10, pady=5)

        # Message
        ttk.Label(self.root, text="Message:").grid(row=6, column=0, sticky="w")
        self.message_text = tk.Text(self.root, height=10, width=60)
        self.message_text.grid(row=6, column=1, padx=10, pady=5)

        # PDF Attachment
        ttk.Button(self.root, text="Browse PDF", command=self.browse_pdf).grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.pdf_label = ttk.Label(self.root, text="", width=40)
        self.pdf_label.grid(row=7, column=1, padx=10, pady=5)

        # Image Attachment
        ttk.Button(self.root, text="Browse Image", command=self.browse_image).grid(row=8, column=0, sticky="w", padx=10, pady=5)
        self.image_label = ttk.Label(self.root, text="", width=40)
        self.image_label.grid(row=8, column=1, padx=10, pady=5)

        # Send Button
        ttk.Button(self.root, text="Send Email", command=self.send_email, width=40).grid(row=9, column=0, columnspan=2, pady=10)

        # Status Label
        self.status_label = ttk.Label(self.root, text="", width=40)
        self.status_label.grid(row=10, column=0, columnspan=2, pady=10)

        # Made by Label
        ttk.Label(self.root, text="Made by Saksham", font=("Helvetica", 12)).grid(row=11, column=0, columnspan=2, pady=10)

    def browse_pdf(self):
        self.pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.pdf_label.config(text=os.path.basename(self.pdf_file_path))

    def browse_image(self):
        self.image_file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        self.image_label.config(text=os.path.basename(self.image_file_path))

    def send_email(self):
        email_address = self.email_entry.get()
        email_password = self.password_entry.get()
        smtp_server = self.smtp_entry.get()
        smtp_port = self.port_entry.get()
        recipients = self.recipients_entry.get().split(',')
        subject = self.subject_entry.get()
        message = self.message_text.get("1.0", "end-1c")

        if not all([email_address, email_password, smtp_server, smtp_port, recipients, subject, message]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            smtp_port = int(smtp_port)
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_address, email_password)

            for recipient in recipients:
                msg = MIMEMultipart()
                msg['From'] = email_address
                msg['To'] = recipient
                msg['Subject'] = subject
                msg['Date'] = formatdate(localtime=True)

                msg.attach(MIMEText(message, 'html'))

                if self.pdf_file_path:
                    with open(self.pdf_file_path, "rb") as pdf_file:
                        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
                        pdf_attachment.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=os.path.basename(self.pdf_file_path)
                        )
                        msg.attach(pdf_attachment)

                if self.image_file_path:
                    with open(self.image_file_path, "rb") as image_file:
                        image_attachment = MIMEImage(image_file.read())
                        image_attachment.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=os.path.basename(self.image_file_path)
                        )
                        msg.attach(image_attachment)

                server.sendmail(email_address, recipient, msg.as_string())
                self.status_label.config(text=f"Email sent to {recipient}")

            server.quit()
            self.status_label.config(text="All emails sent successfully")
            messagebox.showinfo("Success", "All emails sent successfully!")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailSenderApp(root)
    root.mainloop()
