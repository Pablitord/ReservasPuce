import smtplib
import threading
from email.message import EmailMessage
from app.config import Config


class EmailService:
    """Servicio simple de envío de correos vía SMTP."""

    def __init__(self):
        self.host = Config.SMTP_HOST
        self.port = Config.SMTP_PORT
        self.username = Config.SMTP_USER
        self.password = Config.SMTP_PASSWORD
        self.sender = Config.SMTP_FROM
        self.use_tls = Config.SMTP_USE_TLS
        self.use_ssl = Config.SMTP_USE_SSL
        self.last_error = None

    def is_configured(self) -> bool:
        return bool(self.host and self.sender)

    def send_email(self, to_email: str, subject: str, body: str, subtype: str = "plain") -> bool:
        self.last_error = None
        if not self.is_configured():
            self.last_error = "SMTP no configurado. Revisa SMTP_HOST y SMTP_FROM."
            print(f"EmailService: {self.last_error}")
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = to_email
        # Permitir cuerpo en HTML (multilinea)
        message.set_content(body, subtype=subtype)

        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=15)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=15)
            with server:
                if self.use_tls and not self.use_ssl:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(message)
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"EmailService: error enviando correo: {e}")
            return False

    def send_email_async(self, to_email: str, subject: str, body: str, subtype: str = "plain"):
        """Dispara el envío en un hilo para no bloquear la petición."""
        threading.Thread(
            target=self.send_email,
            args=(to_email, subject, body, subtype),
            daemon=True,
        ).start()
