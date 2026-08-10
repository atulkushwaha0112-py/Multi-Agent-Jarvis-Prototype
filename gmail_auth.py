from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

# Ye scope decide karta hai agent kya kya kar sakta hai Gmail mein
# .modify = padhna + bhejna + labels change karna (humein sab chahiye)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    
    # Agar pehle se login ho chuka hai, token.json file mein saved hoga
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Agar login nahi hua ya token expire ho gaya
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Login ke baad token save kar do, taaki dobara login na karna pade
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Gmail service object banao jisse hum actual kaam karenge
    service = build('gmail', 'v1', credentials=creds)
    return service

# Test karne ke liye
if __name__ == '__main__':
    service = get_gmail_service()
    print("Gmail se connect ho gaya! ✅")