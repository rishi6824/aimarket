"""
Twilio Client — SMS & WhatsApp outreach
"""
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
FROM_PHONE = os.getenv("TWILIO_PHONE", "+1234567890")

_client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(ACCOUNT_SID, AUTH_TOKEN)
    return _client


def send_sms(to: str, body: str) -> dict:
    """Send an SMS message."""
    try:
        client = _get_client()
        message = client.messages.create(
            body=body,
            from_=FROM_PHONE,
            to=to,
        )
        return {"sid": message.sid, "status": message.status, "channel": "sms"}
    except Exception as e:
        return {"error": str(e), "channel": "sms"}


def send_whatsapp(to: str, body: str) -> dict:
    """Send a WhatsApp message (Twilio sandbox or approved number)."""
    try:
        client = _get_client()
        whatsapp_from = f"whatsapp:{FROM_PHONE}"
        whatsapp_to = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
        message = client.messages.create(
            body=body,
            from_=whatsapp_from,
            to=whatsapp_to,
        )
        return {"sid": message.sid, "status": message.status, "channel": "whatsapp"}
    except Exception as e:
        return {"error": str(e), "channel": "whatsapp"}


def health_check() -> bool:
    return bool(ACCOUNT_SID and AUTH_TOKEN and ACCOUNT_SID != AUTH_TOKEN)
