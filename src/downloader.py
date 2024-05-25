#!/usr/bin/env python3

import argparse
import traceback
from pathlib import Path
import dropbox
from dropbox.files import FileMetadata, FolderMetadata

def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Download all files from a Dropbox folder asynchronously.')
    parser.add_argument('access_token', type=str, help='Dropbox access token')
    parser.add_argument('-p', '--path_local', type=str, default='.', help='Local path where downloaded files are going to be saved')
    parser.add_argument('-d', '--dropbox_path', type=str, default='', help='Path to the folder on Dropbox')
    return parser.parse_args()

def write_file(dropbox_data, file_path):
    with open(file_path, "wb") as f:
        # f.write(dropbox_data.content)
        for chunk in dropbox_data.iter_content(chunk_size=4096):
            f.write(chunk)

def download_file(dbx, dropbox_path, local_path):
    """
    Download a file from Dropbox to the local filesystem.

    :param dbx: Dropbox API client
    :param dropbox_path: Path to the file on Dropbox
    :param local_path: Path to save the file locally
    """
    print(f"Downloading {dropbox_path} to {local_path}...")
    try:
        _, res = dbx.files_download(path=dropbox_path)
        write_file(res, local_path)
        
    except dropbox.exceptions.ApiError as e:
        print(f"Failed to download {dropbox_path}: {e}")

def download_all_files(dbx, folder_path:str, base_folder:Path):
    """
    Download all files in the specified Dropbox folder synchronously.

    :param dbx: Dropbox API client
    :param folder_path: Path to the folder on Dropbox
    :param base_folder: Base local folder to save downloaded files
    """
    result = dbx.files_list_folder(folder_path)
    
    for entry in result.entries:
        if isinstance(entry, FileMetadata):
            local_path = base_folder / entry.path_display.strip('/')
            local_path.parent.mkdir(parents=True, exist_ok=True)
            # download file only if it does not exists
            if local_path.exists() and local_path.stat().st_size == entry.size:
                print(f"file {local_path} exists, download skipped")
            else:
                download_file(dbx, entry.path_lower, local_path)
        
        elif isinstance(entry, FolderMetadata):
            local_subfolder = base_folder / entry.path_display.strip('/')
            local_subfolder.mkdir(parents=True, exist_ok=True)
            download_all_files(dbx, entry.path_lower, base_folder)


def main():
    args = parse_arguments()

    # Create a Dropbox client
    dbx = dropbox.Dropbox(args.access_token)

    # Base local folder to save downloaded files
    base_folder = Path(args.path_local)
    
    # Download all files in the specified Dropbox folder
    download_all_files(dbx, args.dropbox_path, base_folder)

if __name__ == "__main__":
    main()
