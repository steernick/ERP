# from gmail.invoice_downloader import fetch_attachments_and_process
# from invoice_parser.parser import  run_invoice_parser
from gmail.invoice_downloader import fetch_attachments_and_process, SPREADSHEET_ID
from utils.sheets import list_sheet_names
from utils.auth import get_sheets_service


if __name__ == "__main__":
    # list_sheet_names(get_sheets_service(), SPREADSHEET_ID)
    fetch_attachments_and_process()
    # run_invoice_parser()
    # process_invoices()
    # service = get_gmail_service()  # Twoja funkcja zwracająca obiekt Gmail API
    # print_labels(service)