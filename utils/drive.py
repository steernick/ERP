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
