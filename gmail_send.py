"""
gmail_send.py — send an email via the Gmail API (OAuth, no SMTP/hardcoded creds).

Importing this module is always safe — no side effects at import time.
Run directly only to test:
    python gmail_send.py
"""

import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def send_email(to: str, subject: str, body: str, html: bool = False) -> dict:
    """
    Send an email via the authenticated Gmail API service.

    Parameters
    ----------
    to      : str  — recipient email address
    subject : str  — email subject line
    body    : str  — plain text (or HTML if html=True) body
    html    : bool — if True, body is treated as HTML

    Returns
    -------
    dict — {"status": "sent", "id": <message_id>} on success,
           {"status": "error", "error": <str>} on failure.
    """
    try:
        from gmail_auth import get_gmail_service

        service = get_gmail_service()

        # Resolve the real sender address from the API (avoids invalid "me" header)
        sender_email = os.getenv("GMAIL_USER", "").strip()
        if not sender_email or sender_email.lower() == "me":
            profile = service.users().getProfile(userId="me").execute()
            sender_email = profile.get("emailAddress", "me")

        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = to
        msg["Subject"] = subject

        mime_type = "html" if html else "plain"
        msg.attach(MIMEText(body, mime_type))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        result = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )
        return {"status": "sent", "id": result.get("id"), "from": sender_email, "to": to}

    except Exception as exc:
        import traceback
        print(f"[gmail_send] ERROR: {traceback.format_exc()}")
        return {"status": "error", "error": str(exc)}


if __name__ == "__main__":
    # Quick manual test — set TEST_TO in env or edit here
    test_to = os.getenv("TEST_EMAIL_TO", "atulkushwaha0112@gmail.com")
    result = send_email(
        to=test_to,
        subject="JARVIS test email",
        body="<h2>Hello from JARVIS! Gmail API send works ✅</h2>",
        html=True,
    )
    print(result)
