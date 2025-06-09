from gmail.invoice_downloader import fetch_attachments_and_upload
from invoice_parser.parser import  run_invoice_parser

if __name__ == "__main__":
    # fetch_attachments_and_upload()
    run_invoice_parser()
    # process_invoices()
    # service = get_gmail_service()  # Twoja funkcja zwracająca obiekt Gmail API
    # print_labels(service)