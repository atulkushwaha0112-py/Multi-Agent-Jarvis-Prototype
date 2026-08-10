"""
tools/whatsapp_tools.py — WhatsApp automation tools for LangGraph.

All tools:
  - Wrap calls in try/except and return structured dicts (never rely on print).
  - send_whatsapp_tool requires the agent to confirm before firing.
  - schedule_whatsapp_tool runs the wait+send logic in a background thread.
"""

import threading
import datetime
from langchain_core.tools import tool
from whatsapp_send import send_whatsapp_desktop
from whatsapp_read import get_whatsapp_messages
from check_new_msg_status import (
    open_whatsapp,
    click_unread_filter,
    clear_search,
    capture_image_base64,
    click_all_filter,
    close_whatsapp,
    analyze_with_gemma,
)


@tool
def send_whatsapp_tool(name: str, message: str) -> dict:
    """
    Send a WhatsApp message to a contact via desktop automation.
    Use ONLY when user explicitly says 'send', 'message', 'tell', 'say to'.
    NEVER call read_whatsapp_tool before or after this — just send directly.
    IMPORTANT: Only call after user has confirmed (said yes/send it/go ahead).
    name: contact name as it appears in WhatsApp (e.g. 'Arnav').
    message: the message text to send.
    Returns {"status": "sent", "to": name} or {"status": "error", "error": ...}.
    """
    try:
        send_whatsapp_desktop(name, message)
        return {"status": "sent", "to": name}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@tool
def read_whatsapp_tool(name: str) -> dict:
    """
    Open WhatsApp and copy recent messages from a contact's chat.
    Use ONLY when user explicitly says 'read', 'check messages', 'show messages', 'what did X say'.
    NEVER call this when user says 'send' — use send_whatsapp_tool instead.
    name: contact name to open (e.g. 'Arnav').
    Returns {"status": "ok", "messages": "..."} or {"status": "error", ...}.
    """
    try:
        messages = get_whatsapp_messages(name)
        return {"status": "ok", "messages": messages}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _schedule_and_send(name: str, message: str, send_time: str):
    """Background thread: wait until send_time (HH:MM), then send."""
    print(f"[whatsapp scheduler] Waiting to send to {name} at {send_time}...")
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now == send_time:
            print(f"[whatsapp scheduler] Time reached — sending to {name}")
            try:
                send_whatsapp_desktop(name, message)
                print(f"[whatsapp scheduler] Sent to {name} ✅")
            except Exception as e:
                print(f"[whatsapp scheduler] Failed: {e}")
            break
        import time
        time.sleep(10)


@tool
def schedule_whatsapp_tool(name: str, message: str, send_time: str) -> dict:
    """
    Schedule a WhatsApp message to be sent at a specific time today.
    Runs the wait-and-send logic in a background thread — does not block.
    Use when the user says 'send X to Y at Z time'.
    name: contact name in WhatsApp.
    message: message text.
    send_time: 24-hour HH:MM time string (e.g. '14:30').
    Returns {"status": "scheduled", "at": send_time}.
    """
    try:
        t = threading.Thread(
            target=_schedule_and_send,
            args=(name, message, send_time),
            daemon=True,
        )
        t.start()
        return {"status": "scheduled", "to": name, "at": send_time}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@tool
def check_unread_whatsapp_tool() -> dict:
    """
    Take a screenshot of the WhatsApp unread-chat list and use vision AI to
    identify which contacts have unread messages.
    Use when the user asks 'do I have unread WhatsApp messages?' or similar.
    No arguments needed.
    Returns {"status": "ok", "contacts": "..."} or {"status": "error", ...}.
    """
    try:
        open_whatsapp()
        click_unread_filter()
        clear_search()
        img_b64 = capture_image_base64()
        click_all_filter()
        close_whatsapp()
        result = analyze_with_gemma(img_b64)
        return {"status": "ok", "contacts": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}
