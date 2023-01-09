import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate


def send_tls(host: str, port:int, from_: str, to: str, subject: str, text: str, auth_user: str, auth_password: str):
    mime = MIMEText(text, "plain")
    mime["Subject"] = subject
    mime["From"] = from_
    mime["To"] = to
    mime["Date"] = formatdate()

    smtp = smtplib.SMTP(host, port)
    smtp.starttls()
    smtp.login(auth_user, auth_password)
    send_errs = smtp.send_message(mime)
    smtp.close()

    return send_errs
