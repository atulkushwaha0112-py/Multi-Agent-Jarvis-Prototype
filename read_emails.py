from gmail_auth import get_gmail_service
from memory import index_email, setup_email_collection
import base64

def get_recent_emails(max_results=5):
    """
    Ye function Gmail se recent emails uthata hai
    max_results = kitne emails chahiye (default 5)
    """
    setup_email_collection()
    service = get_gmail_service()
    
    # Inbox se message IDs ki list mangwao
    results = service.users().messages().list(
        userId='me',
        maxResults=max_results,
        labelIds=['INBOX']
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("Koi email nahi mila")
        return []
    
    email_list = []
    
    # Har message ID ke liye, uska pura content mangwao
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()
        
        # Headers mein se From, Subject, Date nikaalo
        headers = msg_data['payload']['headers']
        email_info = {
            'id': msg['id'],
            'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown'),
            'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject'),
            'date': next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown'),
            'snippet': msg_data.get('snippet', '')  # Chhota preview text
        }
        email_list.append(email_info)
        index_email(email_info) 
        
    return email_list

# Test karne ke liye
if __name__ == '__main__':
    emails = get_recent_emails(5)
    
    print(f"\n{len(emails)} emails mile:\n")
    for i, email in enumerate(emails, 1):
        print(f"{i}. From: {email['from']}")
        print(f"   Subject: {email['subject']}")
        print(f"   Preview: {email['snippet'][:80]}...")
        print()