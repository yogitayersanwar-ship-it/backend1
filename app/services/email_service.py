import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from app.config import settings
    MAIL_CONFIGURED = bool(
        getattr(settings, "MAIL_USERNAME", None) and
        getattr(settings, "MAIL_PASSWORD", None)
    )
except Exception:
    MAIL_CONFIGURED = False


class EmailService:
    @staticmethod
    def send_status_update_email(user_email: str, complaint_id: int, new_status: str):
        """
        Send an email notification when a complaint status changes.
        Uses SMTP if MAIL_USERNAME & MAIL_PASSWORD are configured in .env,
        otherwise falls back to a console mock (safe for development).
        """
        subject = f"Grievance #{complaint_id} Status Update"
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background: #f4f6f9; padding: 30px;">
            <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px;
                        padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
              <h2 style="color: #1a3d7c;">Grievance Management System</h2>
              <p>Dear Citizen,</p>
              <p>Your complaint <strong>#{complaint_id}</strong> has been updated.</p>
              <table style="width:100%; margin: 20px 0; border-collapse: collapse;">
                <tr>
                  <td style="padding: 10px; background: #f0f4ff; font-weight: bold;">New Status</td>
                  <td style="padding: 10px; text-transform: uppercase;
                             color: {'#1a7c3e' if new_status == 'resolved' else '#c0392b' if new_status == 'rejected' else '#1a3d7c'}">
                    {new_status.replace('_', ' ').title()}
                  </td>
                </tr>
              </table>
              <p>You can log in to the Grievance Portal to view the full details.</p>
              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
              <p style="color: #888; font-size: 12px;">
                This is an automated message from the Grievance Management System.
                Please do not reply to this email.
              </p>
            </div>
          </body>
        </html>
        """

        if MAIL_CONFIGURED:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = settings.MAIL_FROM
                msg["To"] = user_email
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
                    server.starttls()
                    server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                    server.sendmail(settings.MAIL_FROM, user_email, msg.as_string())

                print(f"[EMAIL] Sent to {user_email} for complaint #{complaint_id} → {new_status}")
            except Exception as e:
                print(f"[EMAIL ERROR] Failed to send email: {e}")
        else:
            # Development fallback — print to console
            print(f"[MOCK EMAIL] To: {user_email} | Complaint #{complaint_id} → Status: '{new_status}'")