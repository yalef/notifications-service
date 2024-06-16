import smtplib
import contextlib
from email.message import EmailMessage


class MessageSender:
    def __init__(self, smtp_addr: str, port: int):
        self._smtp = smtplib.SMTP(smtp_addr, port)

    def send(
        self,
        message: str,
        from_addr: str,
        to_addr: str,
        subject: str,
    ) -> None:
        msg = EmailMessage()
        msg.set_content(message)
        msg["To"] = to_addr
        msg["From"] = from_addr
        msg["Subject"] = subject

        with contextlib.suppress(smtplib.SMTPException):
            self._smtp.send_message(msg)
