def list_sheet_names(sheets_service, spreadsheet_id):
    try:
        response = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_titles = [sheet['properties']['title'] for sheet in response['sheets']]
        print("📄 Dostępne arkusze w pliku:")
        for title in sheet_titles:
            print(f"- {title}")
        return sheet_titles
    except Exception as e:
        print(f"❌ Błąd podczas pobierania nazw arkuszy: {e}")
        return []


def create_google_sheet(service, title):
    """
    Tworzy nowy arkusz Google Sheets o podanym tytule.

    Args:
        service: klient Google Sheets API (z get_sheets_service())
        title: str, nazwa nowego arkusza

    Returns:
        str: ID utworzonego arkusza
    """
    spreadsheet_body = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
    sheet_id = spreadsheet.get('spreadsheetId')
    print(f"Utworzono arkusz: {title} (ID: {sheet_id})")
    return sheet_id


def initialize_sheet_with_headers(sheets_service, spreadsheet_id, sheet_name="Faktury"):
    """
    Dodaje nagłówki do arkusza w Google Sheets, jeśli arkusz jest pusty.

    :param sheets_service: klient Google Sheets API (z autoryzacją)
    :param spreadsheet_id: ID arkusza Google Sheets
    :param sheet_name: nazwa arkusza w pliku (domyślnie "Arkusz1")
    """
    headers = [
        [
            "numer faktury",
            "sprzedawca",
            "nabywca",
            "data wystawienia",
            "data sprzedaży",
            "kwota brutto",
            "kwota netto",
            "kwota VAT",
            "konto bankowe"
        ]
    ]

    # Sprawdź czy w arkuszu jest już zawartość
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1:I1"
    ).execute()

    values = result.get("values", [])

    if not values:
        # Jeśli pusta, dodaj nagłówki
        body = {
            "values": headers
        }
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1:I1",
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"✅ Dodano nagłówki do arkusza '{sheet_name}' w pliku {spreadsheet_id}")
    else:
        print(f"ℹ️ Arkusz '{sheet_name}' już zawiera nagłówki lub dane.")


def add_invoice_data_to_sheets(sheets_service, spreadsheet_id, invoice_data, sheet_name="Faktury"):
    values = [[
        invoice_data.get("numer faktury", ""),
        invoice_data.get("sprzedawca", ""),
        invoice_data.get("nabywca", ""),
        invoice_data.get("data wystawienia", ""),
        invoice_data.get("data sprzedaży", ""),
        invoice_data.get("kwota brutto", ""),
        invoice_data.get("kwota netto", ""),
        invoice_data.get("kwota VAT", ""),
        invoice_data.get("konto bankowe", ""),
    ]]

    body = {'values': values}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:I",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    print("✅ Dodano dane faktury do arkusza")