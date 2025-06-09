import os

LOG_FILE = "processed_files.log"

def is_already_processed(file_id):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, "r") as f:
        return file_id in f.read()

def log_processed_file(file_id):
    with open(LOG_FILE, "a") as f:
        f.write(file_id + "\n")
