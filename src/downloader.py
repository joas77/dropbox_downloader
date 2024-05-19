#!/usr/bin/env python3

import argparse
import asyncio
import concurrent.futures
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
        for chunk in dropbox_data.iter_content(chunk_size=4096):
            f.write(chunk)

def download_file(dbx, dropbox_path, local_path):
    """
    Download a file from Dropbox to the local filesystem.

    :param dbx: Dropbox API client
    :param dropbox_path: Path to the file on Dropbox
    :param local_path: Path to save the file locally
    """
    try:
        metadata, res = dbx.files_download(path=dropbox_path)
        write_file(res, local_path)
        print(f"Downloaded {dropbox_path} to {local_path}")
    except dropbox.exceptions.ApiError as e:
        print(f"Failed to download {dropbox_path}: {e}")

async def download_all_files(dbx, folder_path, base_folder, loop):
    """
    Download all files in the specified Dropbox folder asynchronously.

    :param dbx: Dropbox API client
    :param folder_path: Path to the folder on Dropbox
    :param base_folder: Base local folder to save downloaded files
    :param loop: The asyncio event loop
    """
    try:
        result = dbx.files_list_folder(folder_path)
        tasks = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for entry in result.entries:
                if isinstance(entry, FileMetadata):
                    local_path = base_folder / entry.path_display.strip('/')
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    tasks.append(loop.run_in_executor(executor, download_file, dbx, entry.path_lower, local_path))
                elif isinstance(entry, FolderMetadata):
                    local_subfolder = base_folder / entry.path_display.strip('/')
                    local_subfolder.mkdir(parents=True, exist_ok=True)
                    tasks.append(download_all_files(dbx, entry.path_lower, base_folder, loop))

            async with asyncio.Semaphore(10):
                await asyncio.gather(*tasks)
    except dropbox.exceptions.ApiError as e:
        print(f"API Error: {e}")

async def main():
    args = parse_arguments()

    # Create a Dropbox client
    dbx = dropbox.Dropbox(args.access_token)

    # Base local folder to save downloaded files
    base_folder = Path(args.path_local)
    
    # Get the current event loop
    loop = asyncio.get_running_loop()

    # Download all files in the specified Dropbox folder
    await download_all_files(dbx, args.dropbox_path, base_folder, loop)

if __name__ == "__main__":
    asyncio.run(main())
