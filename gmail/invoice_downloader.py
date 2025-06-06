import os
import base64
from datetime import datetime
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from utils.auth import get_gmail_service, get_drive_service
from utils.drive import get_or_create_drive_folder
from utils.gmail import get_or_create_label, add_label_to_message
from dotenv import load_dotenv


load_dotenv()

LABEL_ID = os.getenv("GMAIL_LABEL")
PARENT_FOLDER_ID = os.getenv("PARENT_FOLDER_ID")

def fetch_attachments_and_upload():
    gmail = get_gmail_service()
    drive = get_drive_service()

    processed_label_id = get_or_create_label(gmail, 'Przetworzone')

    results = gmail.users().messages().list(userId='me', labelIds=[LABEL_ID], maxResults=100).execute()
    messages = results.get('messages', [])

    print(f"Pobrano {len(messages)} wiadomości z etykietą {LABEL_ID}")

    for msg in messages:
        msg_id = msg['id']
        msg_data = gmail.users().messages().get(userId='me', id=msg_id, format='full').execute()

        # Pomijamy wiadomości, które mają już etykietę "Przetworzone"
        if processed_label_id in msg_data.get('labelIds', []):
            print(f"⏭️ Pomijam wiadomość {msg_id} – już oznaczona jako 'Przetworzone'")
            continue

        internal_ts = int(msg_data.get('internalDate')) // 1000
        email_date = datetime.fromtimestamp(internal_ts)

        payload = msg_data.get('payload', {})
        parts = payload.get('parts', [])

        print(f"- Przetwarzam wiadomość ID: {msg_id}")

        for i, part in enumerate(parts):
            filename = part.get('filename', '')
            mime_type = part.get('mimeType')
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')

            print(f"  Część {i}: mimeType={mime_type}, filename={filename}, body keys={body.keys()}")

            if not attachment_id or not filename:
                continue

            attachment = gmail.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=attachment_id
            ).execute()

            file_data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))
            media = MediaIoBaseUpload(BytesIO(file_data), mimetype=mime_type)

            year_folder_name = str(email_date.year)
            month_folder_name = email_date.strftime("%m-%Y")

            year_folder_id = get_or_create_drive_folder(drive, year_folder_name, PARENT_FOLDER_ID)
            target_folder_id = get_or_create_drive_folder(drive, month_folder_name, year_folder_id)

            file_metadata = {
                'name': filename,
                'parents': [target_folder_id],
            }

            uploaded_file = drive.files().create(
                body=file_metadata, media_body=media, fields='id'
            ).execute()

            print(f"✅ Zapisano plik: {filename} ➝ {month_folder_name} ({uploaded_file['id']})")

        # Po przetworzeniu wiadomości ➝ oznacz jako „Przetworzone”
        add_label_to_message(gmail, msg_id, processed_label_id)
