from twilio.rest import Client
from app.core.config import get_settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def send_sms(to_phone: str, body: str) -> dict:
    """
    Send SMS via Twilio. Returns status dict.
    In demo mode (no credentials) it logs the message and returns a mock success.
    """
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.warning("[Twilio DEMO] Would send to %s: %s", to_phone, body)
        return {
            "status": "demo_sent",
            "sid": "DEMO_SID",
            "to": to_phone,
            "body": body,
            "message": "Twilio credentials not configured – message logged only.",
        }

    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        message = client.messages.create(
            body=body,
            from_=settings.twilio_phone_number,
            to=to_phone,
        )
        return {
            "status": "sent",
            "sid": message.sid,
            "to": to_phone,
            "body": body,
        }
    except Exception as e:
        logger.error("Twilio error: %s", e)
        return {
            "status": "failed",
            "error": str(e),
            "to": to_phone,
            "body": body,
        }


def build_alert_message(location: str, risk_label: str, trend: str = "stable") -> str:
    return (
        f"FLOOD ALERT - {risk_label.upper()} RISK: {location}. "
        f"Risk is expected to remain {risk_label.upper()} for the next 48 hours. "
        f"Trend: {trend}. "
        f"Monitor official channels. - FRPEWS"
    )
