from googleapiclient.http import MediaIoBaseDownload
from .auth import get_drive_service
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO, FileIO

def list_monthly_folders(parent_folder_id):
    service = get_drive_service()
    results = service.files().list(
        q=f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    return results.get('files', [])

def list_pdf_files_in_folder(folder_id):
    service = get_drive_service()
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/pdf'",
        fields="files(id, name)"
    ).execute()
    return results.get('files', [])

def download_file(file_id, filename):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return filename

def rename_drive_file(file_id, new_name):
    service = get_drive_service()
    return service.files().update(fileId=file_id, body={"name": new_name}).execute()

def get_or_create_drive_folder(drive, folder_name: str, parent_id: str = None) -> str:
    """
    Tworzy folder na Google Drive lub zwraca ID istniejącego folderu o tej samej nazwie w danym folderze nadrzędnym.

    :param drive: obiekt drive z googleapiclient.discovery.build('drive', 'v3', ...)
    :param folder_name: nazwa folderu do utworzenia lub odnalezienia
    :param parent_id: ID folderu nadrzędnego (opcjonalne)
    :return: ID folderu
    """
    query_parts = [
        f"name='{folder_name}'",
        "mimeType='application/vnd.google-apps.folder'",
        "trashed=false"
    ]
    if parent_id:
        query_parts.append(f"'{parent_id}' in parents")
    query = " and ".join(query_parts)

    results = drive.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']  # folder już istnieje

    # Tworzymy nowy folder
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_id:
        metadata['parents'] = [parent_id]

    folder = drive.files().create(body=metadata, fields='id').execute()
    return folder.get('id')

def upload_file_to_drive(drive, file_content, filename, parent_folder_id):

    media = MediaIoBaseUpload(BytesIO(file_content), mimetype='application/pdf')

    file_metadata = {
        'name': filename,
        'parents': [parent_folder_id],
    }

    uploaded_file = drive.files().create(
        body=file_metadata, media_body=media, fields='id'
    ).execute()

    print(f"✅ Zapisano plik: {filename} ({uploaded_file['id']})")
    return uploaded_file['id']