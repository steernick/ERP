from gmail.invoice_downloader import fetch_attachments_and_upload
# from invoice_parser.parser import process_invoices

def print_labels(service):
    response = service.users().labels().list(userId='me').execute()
    labels = response.get('labels', [])
    for label in labels:
        print(f"Name: {label['name']}, ID: {label['id']}")


if __name__ == "__main__":
    fetch_attachments_and_upload()
    # process_invoices()
    # service = get_gmail_service()  # Twoja funkcja zwracająca obiekt Gmail API
    # print_labels(service)