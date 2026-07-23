from app.services.email_service import EmailService


class NotificationService:
    @staticmethod
    def notify_user_status_change(user_email: str, complaint_id: int, status: str):
        """
        Triggers a status-change notification to the complaint owner.
        Currently sends an email — can be extended to push/SMS in future.
        """
        EmailService.send_status_update_email(user_email, complaint_id, status)

    @staticmethod
    def notify_new_complaint_received(admin_email: str, complaint_id: int, title: str):
        """
        Placeholder for notifying admins when a new complaint is submitted.
        Currently logs to console; extend with email/Slack as needed.
        """
        print(
            f"[NOTIFY] New complaint #{complaint_id} '{title}' submitted. "
            f"Admin notified at: {admin_email}"
        )