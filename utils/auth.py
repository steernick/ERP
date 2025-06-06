import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.file'
]

def get_credentials():
    creds = None
    if os.path.exists('credentials/token.json'):
        creds = Credentials.from_authorized_user_file('credentials/token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('credentials/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_gmail_service():
    return build('gmail', 'v1', credentials=get_credentials())

def get_drive_service():
    return build('drive', 'v3', credentials=get_credentials())
