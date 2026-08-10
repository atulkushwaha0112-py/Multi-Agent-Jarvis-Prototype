"""tools/email_tools.py — Gmail inbox tools for LangGraph."""

from langchain_core.tools import tool
from read_emails import get_recent_emails
from memory import search_emails
from gmail_send import send_email



@tool
def check_inbox_tool(count: int = 5) -> list:
    """
    Fetch the most recent emails from Gmail inbox.
    Returns a list of dicts with keys: id, from, subject, date, snippet.
    Use this when the user asks to check, read, or see their emails.
    count: number of emails to fetch (default 5, max 20).
    """
    try:
        count = min(int(count), 20)
        return get_recent_emails(count)
    except Exception as e:
        return [{"error": str(e)}]


@tool
def search_emails_tool(query: str) -> list:
    """
    Search past emails by topic or content using semantic similarity.
    Returns up to 3 matching emails with from, subject, snippet, date, score.
    Use this when the user asks to find a specific email or topic.
    query: topic or keywords to search for (e.g. 'payment invoice').
    """
    try:
        return search_emails(query)
    except Exception as e:
        return [{"error": str(e)}]

@tool
def send_email_tool(to: str, subject: str, body: str) -> dict:
    """
    Send an email via Gmail after the user has confirmed.

    Rules:
    - Supports name mapping (e.g., "atul")
    - Supports raw email (example@gmail.com)
    - Cleans markdown/mailto formats
    - Rejects fake emails like example.com
    """

    import re

    # 🔥 Your contact book
    CONTACTS = {
        "atul": "atulkushwaha0112@gmail.com",
        "me": "atulkushwaha0112@gmail.com",
        "test": "inut34558@gmail.com"
    }

    def resolve_email(input_str: str) -> str:
        input_str = input_str.lower().strip()

        # 1️⃣ Direct name match
        if input_str in CONTACTS:
            return CONTACTS[input_str]

        # 2️⃣ Name inside sentence (e.g., "send to atul")
        for name, email in CONTACTS.items():
            if name in input_str:
                return email

        # 3️⃣ Extract real email
        match = re.search(r'[\w\.-]+@[\w\.-]+', input_str)
        if match:
            extracted = match.group(0)

            # ❌ Block fake domains
            if "example.com" in extracted:
                return ""

            return extracted

        return ""

    try:
        clean_to = resolve_email(to)

        # 🚨 STRICT VALIDATION
        if not clean_to or "@" not in clean_to:
            return {
                "status": "error",
                "error": f"Invalid or unresolved email from: {to}"
            }

        result = send_email(to=clean_to, subject=subject, body=body)

        # ✅ Return actual recipient for clarity
        result["resolved_to"] = clean_to
        return result

    except Exception as e:
        return {"status": "error", "error": str(e)}