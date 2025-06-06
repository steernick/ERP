import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

drive_scopes = os.getenv("GOOGLE_DRIVE_SCOPES", "").split(",")
gmail_scopes = os.getenv("GMAIL_SCOPES", "").split(",")

SCOPES = [scope.strip() for scope in drive_scopes + gmail_scopes if scope.strip()]


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
