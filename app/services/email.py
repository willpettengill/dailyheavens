import os
from typing import Optional
import emails
from emails.template import JinjaTemplate
from pathlib import Path

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password]):
            raise ValueError("Missing required email configuration")

    def send_chart_email(
        self,
        email_to: str,
        subject: str,
        chart_data: dict,
        template_path: Optional[str] = None,
        pdf_attachment: Optional[Path] = None
    ) -> bool:
        """Send an email with chart information and optional PDF attachment."""
        
        # Use default template if none provided
        if template_path is None:
            template_str = """
            Dear {{ name }},

            Here is your astrological chart reading:

            Sun Sign: {{ chart.planets.sun.sign }}
            Moon Sign: {{ chart.planets.moon.sign }}
            Ascendant: {{ chart.angles.ascendant.sign }}

            {{ interpretation }}

            Best regards,
            Your Astrological Service
            """
        else:
            with open(template_path) as f:
                template_str = f.read()

        # Create message
        message = emails.Message(
            subject=subject,
            html=JinjaTemplate(template_str),
            mail_from=(self.smtp_user, "Astrological Service")
        )

        # Add PDF attachment if provided
        if pdf_attachment and pdf_attachment.exists():
            message.attach(
                filename=pdf_attachment.name,
                content_disposition="attachment",
                data=pdf_attachment.read_bytes()
            )

        # Send email
        response = message.send(
            to=email_to,
            render={
                "name": chart_data.get("name", "Valued Client"),
                "chart": chart_data,
                "interpretation": chart_data.get("interpretation", "")
            },
            smtp={
                "host": self.smtp_host,
                "port": self.smtp_port,
                "user": self.smtp_user,
                "password": self.smtp_password,
                "tls": True,
            }
        )

        return response.status_code == 250
