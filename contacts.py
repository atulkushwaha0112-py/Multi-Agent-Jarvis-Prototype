"""
contacts.py — name shortcuts → email / WhatsApp contact mapping.

Say "send mail to atul" instead of spelling out the full email address.
Add your own entries to EMAIL_CONTACTS and WHATSAPP_CONTACTS below.
"""

# name (lowercase) → email address
EMAIL_CONTACTS = {
    "atul": "atulkushwaha0112@gmail.com",
    "myself": "atulkushwaha0112@gmail.com",
    "me": "atulkushwaha0112@gmail.com",
    # add more: "priya": "priya@example.com",
}

# name (lowercase) → WhatsApp display name (as it appears in the app)
WHATSAPP_CONTACTS = {
    "arnav": "arnav singh",
    # add more: "mummy": "Mummy",
}


def resolve_email(name: str) -> str:
    """
    Resolve a contact name/alias to an email address.
    Returns the original string if it already contains '@' or is not in the dict.
    """
    if "@" in name:
        return name
    return EMAIL_CONTACTS.get(name.strip().lower(), name)


def resolve_whatsapp(name: str) -> str:
    """
    Resolve a contact alias to its WhatsApp display name.
    Returns original string if not found.
    """
    return WHATSAPP_CONTACTS.get(name.strip().lower(), name)
