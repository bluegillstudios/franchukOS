# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import customtkinter as ctk
import smtplib
import imaplib
import email
from tkinter import messagebox, scrolledtext

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_SERVER = "imap.gmail.com"

ctk.set_appearance_mode("System")  # Light or Dark Mode
ctk.set_default_color_theme("blue")  # Color Theme

class ModernEmailApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Franmail v1.0.0")
        self.geometry("800x700")
        
        self.create_login_frame()

    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self, corner_radius=10)
        self.login_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.login_frame, text="Email Login", font=("Helvetica", 20, "bold")).pack(pady=20)

        self.email_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Email")
        self.email_entry.pack(pady=10, ipady=5, fill="x", padx=40)

        self.pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
        self.pass_entry.pack(pady=10, ipady=5, fill="x", padx=40)

        self.login_btn = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_btn.pack(pady=20)

    def login(self):
        self.email_address = self.email_entry.get()
        self.password = self.pass_entry.get()
        try:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER)
            self.imap.login(self.email_address, self.password)
            self.login_frame.destroy()
            self.create_main_frame()
        except Exception as e:
            messagebox.showerror("Login Failed", f"Error: {e}")

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Send Email Section
        send_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        send_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(send_frame, text="Send Email", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.to_entry = ctk.CTkEntry(send_frame, placeholder_text="To")
        self.to_entry.pack(pady=5, fill="x", padx=20)

        self.subject_entry = ctk.CTkEntry(send_frame, placeholder_text="Subject")
        self.subject_entry.pack(pady=5, fill="x", padx=20)

        self.message_text = scrolledtext.ScrolledText(send_frame, height=8)
        self.message_text.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(send_frame, text="Send", command=self.send_email).pack(pady=10)

        # Inbox Section
        inbox_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        inbox_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(inbox_frame, text="Inbox", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.inbox_list = ctk.CTkTextbox(inbox_frame, width=300, height=200)
        self.inbox_list.pack(side="left", fill="y", padx=10, pady=10)
        self.inbox_list.configure(state="disabled")

        self.email_body = scrolledtext.ScrolledText(inbox_frame)
        self.email_body.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.load_inbox()

    def send_email(self):
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(self.email_address, self.password)

            to_addr = self.to_entry.get()
            subject = self.subject_entry.get()
            body = self.message_text.get("1.0", "end")

            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_address, to_addr, message)
            server.quit()

            messagebox.showinfo("Success", "Email Sent Successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email:\n{e}")

    def load_inbox(self):
        try:
            self.imap.select("inbox")
            status, messages = self.imap.search(None, "ALL")
            self.email_ids = messages[0].split()

            self.inbox_list.configure(state="normal")
            self.inbox_list.delete("1.0", "end")
            for eid in reversed(self.email_ids[-20:]):
                status, msg_data = self.imap.fetch(eid, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                subject = msg["subject"]
                sender = msg["from"]
                self.inbox_list.insert("end", f"{sender} - {subject}\n")
            self.inbox_list.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inbox:\n{e}")


if __name__ == "__main__":
    app = ModernEmailApp()
    app.mainloop()
