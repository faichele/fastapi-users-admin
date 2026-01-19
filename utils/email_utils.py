"""
E-Mail-Utilities für Benutzerverwaltung.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jinja2 import Template


class EmailUtils:
    """
    Utility-Klasse für E-Mail-Versand.
    """

    def __init__(self, config):
        """
        Initialisiert die E-Mail-Utilities.

        Args:
            config: AdminConfig Instanz mit E-Mail-Einstellungen
        """
        self.config = config

    def send_email(
        self,
        email_to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Sendet eine E-Mail.

        Args:
            email_to: Empfänger-E-Mail-Adresse
            subject: E-Mail-Betreff
            html_content: HTML-Inhalt der E-Mail
            text_content: Optional Text-Inhalt (Fallback)

        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self.config.emails_enabled:
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.emails_from_name} <{self.config.emails_from_email}>"
            msg['To'] = email_to

            # Add text part
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            # Add HTML part
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.smtp_user and self.config.smtp_password:
                    server.starttls()
                    server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            # Log error if logging is enabled
            print(f"Failed to send email: {e}")
            return False

    def send_password_reset_email(self, email_to: str, token: str, base_url: str) -> bool:
        """
        Sendet eine Passwort-Reset-E-Mail.

        Args:
            email_to: Empfänger-E-Mail-Adresse
            token: Reset-Token
            base_url: Basis-URL der Anwendung

        Returns:
            True wenn erfolgreich, sonst False
        """
        reset_link = f"{base_url}/reset-password?token={token}"

        html_template = """
        <html>
        <body>
            <h2>Passwort zurücksetzen</h2>
            <p>Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts gestellt.</p>
            <p>Klicken Sie auf den folgenden Link, um Ihr Passwort zurückzusetzen:</p>
            <p><a href="{{ reset_link }}">Passwort zurücksetzen</a></p>
            <p>Dieser Link ist {{ expire_minutes }} Minuten gültig.</p>
            <p>Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail.</p>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(
            reset_link=reset_link,
            expire_minutes=self.config.password_reset_token_expire_minutes
        )

        return self.send_email(
            email_to=email_to,
            subject="Passwort zurücksetzen",
            html_content=html_content
        )

    def send_new_user_email(self, email_to: str, username: str, temporary_password: str) -> bool:
        """
        Sendet eine Willkommens-E-Mail für neue Benutzer.

        Args:
            email_to: Empfänger-E-Mail-Adresse
            username: Benutzername
            temporary_password: Temporäres Passwort

        Returns:
            True wenn erfolgreich, sonst False
        """
        html_template = """
        <html>
        <body>
            <h2>Willkommen!</h2>
            <p>Ein Benutzerkonto wurde für Sie erstellt.</p>
            <p><strong>Benutzername:</strong> {{ username }}</p>
            <p><strong>Temporäres Passwort:</strong> {{ password }}</p>
            <p>Bitte ändern Sie Ihr Passwort nach der ersten Anmeldung.</p>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(
            username=username,
            password=temporary_password
        )

        return self.send_email(
            email_to=email_to,
            subject="Ihr neues Benutzerkonto",
            html_content=html_content
        )

