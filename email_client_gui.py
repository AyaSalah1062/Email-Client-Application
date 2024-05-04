import tkinter as tk
from tkinter import messagebox
import smtplib
import imaplib
import email
from plyer import notification  # Import Plyer for push notifications

class EmailClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Email Client")

        # Load email credentials from file
        credentials = self.load_credentials("email_credentials.txt")
        if credentials:
            self.sender_email = credentials.get("SenderEmail", "")
            self.sender_password = credentials.get("SenderPassword", "")
            self.recipient_email = credentials.get("ReceiverEmail", "")
            self.receiver_password = credentials.get("ReceiverPassword", "")
        else:
            messagebox.showerror("Error", "Failed to load email credentials.")
            self.destroy()
            return

        # Initialize GUI components
        self.init_gui()

    def init_gui(self):
        # GUI components for entering email details
        tk.Label(self, text="Sender Email:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=5)
        self.sender_email_entry = tk.Entry(self, width=40)
        self.sender_email_entry.insert(tk.END, self.sender_email)  # Insert loaded sender email
        self.sender_email_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Sender Password:", font=("Helvetica", 12, "bold")).grid(row=1, column=0, padx=10, pady=5)
        self.sender_password_entry = tk.Entry(self, width=40, show="*")
        self.sender_password_entry.insert(tk.END, self.sender_password)  # Insert loaded password
        self.sender_password_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="Recipient Email:", font=("Helvetica", 12, "bold")).grid(row=2, column=0, padx=10, pady=5)
        self.recipient_email_entry = tk.Entry(self, width=40)
        self.recipient_email_entry.insert(tk.END, self.recipient_email)  # Insert loaded recipient email
        self.recipient_email_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="Recipient Password:", font=("Helvetica", 12, "bold")).grid(row=3, column=0, padx=10, pady=5)
        self.receiver_password_entry = tk.Entry(self, width=40, show="*")
        self.receiver_password_entry.insert(tk.END, self.receiver_password)  # Insert loaded receiver password
        self.receiver_password_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self, text="Subject:", font=("Helvetica", 12, "bold")).grid(row=4, column=0, padx=10, pady=5)
        self.subject_entry = tk.Entry(self, width=40)
        self.subject_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self, text="Body:", font=("Helvetica", 12, "bold")).grid(row=5, column=0, padx=10, pady=5)
        self.body_entry = tk.Text(self, width=40, height=5)
        self.body_entry.grid(row=5, column=1, padx=10, pady=5)

        # Send and Receive buttons
        send_button = tk.Button(self, text="Send Email", command=self.send_email, font=("Helvetica", 12, "bold"), bg="#0077CC", fg="white")
        send_button.grid(row=6, column=0, columnspan=2, pady=20, padx=10, sticky="ew")

        receive_button = tk.Button(self, text="Receive Email", command=self.receive_email, font=("Helvetica", 12, "bold"), bg="#0077CC", fg="white")
        receive_button.grid(row=7, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        # Initialize notification flag to track new email notifications
        self.new_email_flag = False

    def load_credentials(self, filename):
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
                credentials = {}
                for line in lines:
                    key, value = line.strip().split(": ")
                    credentials[key] = value
                return credentials
        except Exception as e:
            print(f"Error loading credentials: {str(e)}")
            return None

    def send_email(self):
        # Retrieve email details from GUI entries
        sender_email = self.sender_email_entry.get().strip()
        sender_password = self.sender_password_entry.get().strip()
        recipient_email = self.recipient_email_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_entry.get("1.0", tk.END).strip()

        # Check if any required fields are empty
        if not sender_email or not sender_password or not recipient_email or not subject or not body:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            self.send_email_with_credentials(sender_email, sender_password, recipient_email, subject, body)
            messagebox.showinfo("Email Sent", "Email sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")

    def receive_email(self):
        # Retrieve email details from GUI entries
        recipient_email = self.recipient_email_entry.get().strip()
        receiver_password = self.receiver_password_entry.get().strip()

        try:
            email_body = self.receive_email_with_credentials(recipient_email, receiver_password)
            if email_body:
                messagebox.showinfo("Latest Email Body", f"Latest Email Body:\n{email_body}")
                self.new_email_flag = True  # Set flag to trigger push notification
            else:
                messagebox.showwarning("No Email", "No new emails found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to receive email: {str(e)}")

    def send_email_with_credentials(self, sender_email, sender_password, recipient_email, subject, body):
        # Function to send email using provided sender credentials
        message = f"Subject: {subject}\n\n{body}"
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message)

    def receive_email_with_credentials(self, recipient_email, receiver_password):
        # Function to receive latest email using provided receiver credentials
        try:
            with imaplib.IMAP4_SSL('imap.gmail.com') as server:
                server.login(recipient_email, receiver_password)
                server.select('INBOX')

                status, data = server.search(None, 'ALL')
                latest_email_id = data[0].split()[-1]

                status, email_data = server.fetch(latest_email_id, '(RFC822)')
                raw_email = email_data[0][1]

                message = email.message_from_bytes(raw_email)
                if message.is_multipart():
                    for part in message.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain' or content_type == 'text/html':
                            email_body = part.get_payload(decode=True).decode()
                            self.show_notification("New Email Alert", "You have a new email in your mailbox!")
                            return email_body
                else:
                    email_body = message.get_payload(decode=True).decode()
                    self.show_notification("New Email Alert", "You have a new email in your mailbox!")
                    return email_body
        except Exception as e:
            print(f"Error receiving email: {str(e)}")
            return None

    def show_notification(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,  # Add custom app icon if desired
                timeout=10  # Notification duration in seconds
            )
        except Exception as e:
            print(f"Error displaying notification: {str(e)}")

    def check_new_email(self):
        # Function to check for new email and display push notification
        try:
            email_body = self.receive_email_with_credentials(self.recipient_email, self.receiver_password)
            if email_body:
                self.new_email_flag = True  # Set flag to trigger push notification
            else:
                messagebox.showwarning("No Email", "No new emails found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to receive email: {str(e)}")

        # Schedule next check for new email after 10 seconds (adjust as needed)
        self.after(10000, self.check_new_email)

if __name__ == "__main__":
    app = EmailClientApp()
    app.after(10000, app.check_new_email)  # Check for new email every 10 seconds
    app.mainloop()