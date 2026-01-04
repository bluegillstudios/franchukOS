# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import customtkinter as ctk
import smtplib
import imaplib
import email
import email.mime.base
import email.mime.multipart
import email.mime.text
from email import encoders
from tkinter import messagebox, scrolledtext, filedialog
import json
import os
import threading

try:
    import keyring
except Exception:
    keyring = None

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_SERVER = "imap.gmail.com"

ctk.set_appearance_mode("System")  # Light or Dark Mode
ctk.set_default_color_theme("blue")  # Color Theme

class Franmail(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Franmail v1.7.0")
        self.geometry("900x700")
        self.attachments = []
        self.auto_login_done = False
        self.show_pass = False
        self.create_login_frame()

    # -------------------- LOGIN --------------------
    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self, corner_radius=10)
        self.login_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.login_frame, text="Email Login", font=("Helvetica", 20, "bold")).pack(pady=20)

        self.email_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Email")
        self.email_entry.pack(pady=10, ipady=5, fill="x", padx=40)

        self.pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
        self.pass_entry.pack(pady=10, ipady=5, fill="x", padx=40)

        # Show Password Button
        self.show_pass_btn = ctk.CTkButton(self.login_frame, text="Show Password", command=self.toggle_password)
        self.show_pass_btn.pack(pady=5)

        self.login_btn = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_btn.pack(pady=10)
        ctk.CTkButton(self.login_frame, text="Use App Password", command=self.use_app_password).pack(pady=5)
        ctk.CTkButton(self.login_frame, text="Clear Saved Credentials", command=self.clear_credentials).pack(pady=5)

        # Auto-login if keyring has credentials
        if keyring and not self.auto_login_done:
            self.auto_login_done = True
            stored = keyring.get_password('franmail', None)
            if stored:
                self.email_entry.insert(0, stored)
                self.pass_entry.insert(0, stored)
                self.login()

    def toggle_password(self):
        self.show_pass = not self.show_pass
        self.pass_entry.configure(show="" if self.show_pass else "*")
        self.show_pass_btn.configure(text="Hide Password" if self.show_pass else "Show Password")

    def login(self):
        self.email_address = self.email_entry.get()
        self.password = self.pass_entry.get()
        if keyring and not self.password:
            stored = keyring.get_password('franmail', self.email_address)
            if stored:
                try:
                    data = json.loads(stored)
                except Exception:
                    self.password = stored
        try:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER)
            self.imap.login(self.email_address, self.password)
            if keyring and self.password:
                keyring.set_password('franmail', self.email_address, self.password)
            self.login_frame.destroy()
            self.create_main_frame()
            threading.Thread(target=self.background_inbox_sync, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Login Failed", f"Error: {e}")

    def use_app_password(self):
        self.email_address = self.email_entry.get()
        self.password = self.pass_entry.get()
        if not self.email_address or not self.password:
            messagebox.showwarning("Missing", "Please enter email and app password first.")
            return
        if keyring:
            keyring.set_password('franmail', self.email_address, self.password)
        self.login()

    def clear_credentials(self):
        if keyring:
            keyring.delete_password('franmail', self.email_entry.get())
            messagebox.showinfo("Cleared", "Saved credentials cleared.")

    def oauth_login(self):
        messagebox.showinfo("Disabled", "OAuth2 sign-in is disabled. Please use an App Password or IMAP credentials.")

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # UI Controls
        theme_frame = ctk.CTkFrame(self.main_frame)
        theme_frame.pack(fill="x", pady=5)
        ctk.CTkButton(theme_frame, text="Toggle Dark/Light", command=self.toggle_mode).pack(side="left", padx=10)
        ctk.CTkButton(theme_frame, text="Refresh Inbox", command=self.load_inbox).pack(side="left", padx=10)

        # Send Email Section
        send_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        send_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(send_frame, text="Compose Email", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.to_entry = ctk.CTkEntry(send_frame, placeholder_text="To")
        self.to_entry.pack(pady=5, fill="x", padx=20)

        self.subject_entry = ctk.CTkEntry(send_frame, placeholder_text="Subject")
        self.subject_entry.pack(pady=5, fill="x", padx=20)

        self.message_text = scrolledtext.ScrolledText(send_frame, height=8)
        self.message_text.pack(pady=10, padx=20, fill="x")

        attach_frame = ctk.CTkFrame(send_frame)
        attach_frame.pack(fill="x", padx=20)
        ctk.CTkButton(attach_frame, text="Add Attachment", command=self.add_attachment).pack(side="left", pady=5)
        self.attach_label = ctk.CTkLabel(attach_frame, text="No attachments")
        self.attach_label.pack(side="left", padx=10)

        button_frame = ctk.CTkFrame(send_frame)
        button_frame.pack(pady=5)
        ctk.CTkButton(button_frame, text="Send", command=self.send_email).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Reply", command=lambda: self.reply_forward("reply")).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Forward", command=lambda: self.reply_forward("forward")).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Delete", command=self.delete_email).pack(side="left", padx=5)

        # Inbox Section
        inbox_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        inbox_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(inbox_frame, text="Inbox", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.inbox_list = ctk.CTkTextbox(inbox_frame, width=300, height=200)
        self.inbox_list.pack(side="left", fill="y", padx=10, pady=10)
        self.inbox_list.configure(state="disabled")
        self.inbox_list.bind("<ButtonRelease-1>", self.select_email)

        self.email_body = scrolledtext.ScrolledText(inbox_frame)
        self.email_body.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.load_inbox()

    def add_attachment(self):
        files = filedialog.askopenfilenames()
        if files:
            self.attachments.extend(files)
            self.attach_label.configure(text=", ".join(os.path.basename(f) for f in self.attachments))

    def send_email(self):
        try:
            msg = email.mime.multipart.MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.to_entry.get()
            msg['Subject'] = self.subject_entry.get()
            msg.attach(email.mime.text.MIMEText(self.message_text.get("1.0", "end"), 'plain'))

            for f in self.attachments:
                part = email.mime.base.MIMEBase('application', 'octet-stream')
                with open(f, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(f)}')
                msg.attach(part)

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(self.email_address, self.password)
            server.send_message(msg)
            server.quit()

            messagebox.showinfo("Success", "Email Sent Successfully!")
            self.message_text.delete("1.0", "end")
            self.attachments.clear()
            self.attach_label.configure(text="No attachments")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email:\n{e}")

    def load_inbox(self):
        try:
            if not getattr(self, 'imap', None):
                self.inbox_list.configure(state="normal")
                self.inbox_list.delete("1.0", "end")
                self.inbox_list.insert("end", "Not connected to IMAP. Inbox will appear here after login.\n")
                self.inbox_list.configure(state="disabled")
                return
            self.imap.select("inbox")
            status, messages = self.imap.search(None, "ALL")
            self.email_ids = messages[0].split()

            self.inbox_list.configure(state="normal")
            self.inbox_list.delete("1.0", "end")
            for eid in reversed(self.email_ids[-50:]):
                status, msg_data = self.imap.fetch(eid, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                subject = msg.get("subject", "(No Subject)")
                sender = msg.get("from", "(Unknown)")
                date = msg.get("date", "")
                self.inbox_list.insert("end", f"{eid.decode()} | {sender} | {subject} | {date}\n")
            self.inbox_list.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inbox:\n{e}")

    def select_email(self, event=None):
        try:
            index = self.inbox_list.index("@%s,%s" % (event.x, event.y))
            line = self.inbox_list.get(index + " linestart", index + " lineend")
            if not line.strip():
                return
            eid = line.split("|")[0].strip().encode()
            status, msg_data = self.imap.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()
            self.email_body.delete("1.0", "end")
            self.email_body.insert("end", body)
            self.selected_email_id = eid
        except Exception as e:
            print("Email selection error:", e)

    def reply_forward(self, mode):
        try:
            original = self.email_body.get("1.0", "end")
            if mode == "reply":
                self.to_entry.delete(0, "end")
                line = self.inbox_list.get("insert linestart", "insert lineend")
                sender = line.split("|")[1].strip()
                self.to_entry.insert(0, sender)
                self.subject_entry.delete(0, "end")
                self.subject_entry.insert(0, "Re: " + line.split("|")[2].strip())
                self.message_text.delete("1.0", "end")
                self.message_text.insert("end", "\n\n--- Original Message ---\n" + original)
            elif mode == "forward":
                self.to_entry.delete(0, "end")
                self.subject_entry.delete(0, "end")
                self.subject_entry.insert(0, "Fwd: " + self.subject_entry.get())
                self.message_text.insert("end", "\n\n--- Forwarded Message ---\n" + original)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot {mode} email: {e}")

    def delete_email(self):
        try:
            if hasattr(self, 'selected_email_id'):
                self.imap.store(self.selected_email_id, '+FLAGS', '\\Deleted')
                self.imap.expunge()
                messagebox.showinfo("Deleted", "Email deleted successfully.")
                self.load_inbox()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete email: {e}")

    def toggle_mode(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if current == "Dark" else "Dark")

    def background_inbox_sync(self):
        import time
        last_count = 0
        while True:
            if getattr(self, 'imap', None):
                self.imap.select("inbox")
                status, messages = self.imap.search(None, "ALL")
                email_ids = messages[0].split()
                if len(email_ids) > last_count:
                    messagebox.showinfo("New Email", "You have new messages!")
                    last_count = len(email_ids)
            time.sleep(60)  # check every minute


if __name__ == "__main__":
    app = Franmail()
    app.mainloop()