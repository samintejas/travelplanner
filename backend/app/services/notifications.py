import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NotificationService:
    _notifications: list[Dict[str, Any]] = []

    @classmethod
    def notify_admin(cls, booking_data: Dict[str, Any]):
        notification = {
            "type": "new_booking",
            "booking_id": booking_data.get("id"),
            "user_name": booking_data.get("user_name"),
            "user_email": booking_data.get("user_email"),
            "destination": booking_data.get("destination"),
            "message": f"New booking confirmed for {booking_data.get('user_name')} to {booking_data.get('destination')}",
        }
        cls._notifications.append(notification)
        logger.info(f"Admin notification: {notification['message']}")
        return notification

    @classmethod
    def get_notifications(cls) -> list[Dict[str, Any]]:
        return cls._notifications

    @classmethod
    def clear_notifications(cls):
        cls._notifications = []
