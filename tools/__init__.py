"""tools/__init__.py — exposes ALL_TOOLS list for graph.py."""

# Ensure project root is on sys.path so tool modules can import
# read_emails, memory, gmail_send, etc. regardless of CWD.
import sys, os as _os
_PROJECT_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tools.email_tools import check_inbox_tool, search_emails_tool, send_email_tool
from tools.memory_tools import save_memory_tool, search_memory_tool
from tools.music_tools import play_music_tool, stop_music_tool
from tools.whatsapp_tools import (
    send_whatsapp_tool,
    read_whatsapp_tool,
    schedule_whatsapp_tool,
    check_unread_whatsapp_tool,
)
from tools.todo_tools import add_todo_tool, view_todos_tool, complete_todo_tool, delete_todo_tool

ALL_TOOLS = [
    check_inbox_tool,
    search_emails_tool,
    send_email_tool,
    save_memory_tool,
    search_memory_tool,
    play_music_tool,
    stop_music_tool,
    send_whatsapp_tool,
    read_whatsapp_tool,
    schedule_whatsapp_tool,
    check_unread_whatsapp_tool,
    add_todo_tool,
    view_todos_tool,
    complete_todo_tool,
    delete_todo_tool,
]
