import os
import base64
from datetime import datetime
from utils.auth import get_gmail_service, get_drive_service, get_sheets_service
from utils.drive import get_or_create_drive_folder, upload_file_to_drive
from utils.gmail import get_or_create_label, add_label_to_message
from utils.sheets import initialize_sheet_with_headers, add_invoice_data_to_sheets
from dotenv import load_dotenv
from deepseek_extractor import extract_invoice_data_from_bytes


load_dotenv()

LABEL_ID = os.getenv("GMAIL_LABEL")
PARENT_FOLDER_ID = os.getenv("PARENT_FOLDER_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


def fetch_attachments_and_process():
    gmail = get_gmail_service()
    drive = get_drive_service()
    sheets = get_sheets_service()

    processed_label_id = get_or_create_label(gmail, 'Przetworzone')

    results = gmail.users().messages().list(userId='me', labelIds=[LABEL_ID], maxResults=100).execute()
    messages = results.get('messages', [])

    print(f"Pobrano {len(messages)} wiadomości z etykietą {LABEL_ID}")

    for msg in messages:
        msg_id = msg['id']
        msg_data = gmail.users().messages().get(userId='me', id=msg_id, format='full').execute()

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
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')

            if not attachment_id or not filename or not filename.lower().endswith('.pdf'):
                continue

            attachment = gmail.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=attachment_id
            ).execute()

            file_data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))

            # 1. Wyciągnij dane z faktury przez Gemini AI
            invoice_data = extract_invoice_data_from_bytes(file_data)

            if not invoice_data:
                print(f"⚠️ Nie udało się wyciągnąć danych z faktury: {filename}")
                continue

            new_filename = f"{invoice_data.get('sprzedawca', 'unknown')}-{invoice_data.get('numer faktury', 'unknown')}.pdf"

            # 3. Foldery na Drive
            year_folder_name = str(email_date.year)
            month_folder_name = email_date.strftime("%m-%Y")

            year_folder_id = get_or_create_drive_folder(drive, year_folder_name, PARENT_FOLDER_ID)
            target_folder_id = get_or_create_drive_folder(drive, month_folder_name, year_folder_id)

            # 4. Upload pliku z nową nazwą
            upload_file_to_drive(drive, file_data, new_filename, target_folder_id)

            # 5. Dodanie nagłówków w pliku
            initialize_sheet_with_headers(sheets, SPREADSHEET_ID)

            # 6. Zapis danych do Google Sheets
            add_invoice_data_to_sheets(sheets, SPREADSHEET_ID, invoice_data)

        # Po przetworzeniu wiadomości oznacz jako „Przetworzone”
        add_label_to_message(gmail, msg_id, processed_label_id)