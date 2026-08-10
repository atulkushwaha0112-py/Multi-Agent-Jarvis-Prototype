"""
gmail_auth.py — Gmail OAuth2 service builder.

Key design: the entire OAuth browser flow runs in a SUBPROCESS so that
run_local_server() can never corrupt the parent process's file descriptors.
After the subprocess saves token.json, the parent loads it normally.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import sys
import subprocess

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

_HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(_HERE, 'token.json')
CREDS_PATH = os.path.join(_HERE, 'credentials.json')

# Inline script run in subprocess to perform OAuth and save token
_OAUTH_SCRIPT = """
import sys
sys.path.insert(0, {here!r})
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file({creds!r}, {scopes!r})
creds = flow.run_local_server(port=0)
with open({token!r}, 'w', encoding='utf-8') as f:
    f.write(creds.to_json())
print("token_saved")
"""


def _run_oauth_in_subprocess() -> None:
    """
    Run the OAuth browser flow in a fresh Python process.
    This completely isolates the FD-corrupting run_local_server() from
    the parent process, so token.json can be written without issues.
    """
    script = _OAUTH_SCRIPT.format(
        here=_HERE,
        creds=CREDS_PATH,
        token=TOKEN_PATH,
        scopes=SCOPES,
    )
    result = subprocess.run(
        [sys.executable, '-c', script],
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError("OAuth subprocess failed — check the browser window and try again.")


def _write_token_subprocess(json_str: str) -> None:
    """Write token JSON via a fresh subprocess to protect parent process FDs."""
    subprocess.run(
        [sys.executable, '-c',
         f'import sys; open(r"{TOKEN_PATH}", "w", encoding="utf-8").write(sys.stdin.read())'],
        input=json_str,
        text=True,
        check=True,
    )


def get_gmail_service():
    """
    Return an authenticated Gmail API service object.
    - If token.json exists and is valid → use it directly (no browser).
    - If expired but refresh_token present → refresh silently (no browser).
    - Otherwise → run OAuth in a subprocess (browser opens once, then saved).
    """
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Silent refresh — no browser needed
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            # Save via subprocess to protect parent FDs
            _write_token_subprocess(creds.to_json())
        else:
            # Full OAuth — run entirely in subprocess to protect this process's FDs
            _run_oauth_in_subprocess()
            # Load the token that the subprocess just saved
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    return build('gmail', 'v1', credentials=creds)


if __name__ == '__main__':
    svc = get_gmail_service()
    print("Gmail connected ✅")
    profile = svc.users().getProfile(userId='me').execute()
    print("Logged in as:", profile.get('emailAddress'))