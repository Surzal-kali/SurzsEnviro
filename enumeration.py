
import subprocess
import os
import json
import shutil
import sys
import time
import threading
import platform
from pathlib import Path
from time import sleep
from importlib.metadata  import files, version
from computerspeak import ComputerSpeak as cs
import psutil


class FileCrawler:
    """ Handles the enumeration of files on the user's system based on their consent preferences."""
    def __init__(self,):
        """Initialize the FileCrawler class with user-defined out-of-scope items. The out_of_scope parameter is expected to be a list of strings representing data types or categories that the user does not want to be collected during enumeration. The class will use this information to filter out any data that falls under these categories when crawling the file system."""
        csi = cs()
    def _build_payload(self, file_path: str):
        """Build a payload dictionary with file metadata and a content preview. This includes the file path, name, extension, size in bytes, and a preview of the first 300 characters of the file content (with non-text files handled gracefully). takes file_path as a parameter and returns a dictionary with the collected data. Needs to also take file size, type, and metadta from details if possible. #yeth
        """
        selected = Path(file_path)
        size_bytes = selected.stat().st_size
        preview = ""
        try:
            if selected.is_file():
                with open(selected, 'r', errors='ignore') as f:
                    preview = f.read(300)
        except Exception as e:
            preview = f"Could not read file content: {type(e).__name__}: {str(e)}"
        try: 
            folderstep = {
                "enumeration_folder_path": str(selected),
                "enumeration_folder_name": selected.name,
                "enumeration_folder_size_bytes": size_bytes,
                "enumeration_preview": preview,
                "enumeration_details": {},  
            }
            return folderstep
        except Exception as e:        
            folderstep = {
                "File skipped due to error": f"{type(e).__name__}: {str(e)}"
            }
            return folderstep
    def _pick_folder(self):
        """Prompt the user to select a folder for enumeration. This function allows the user to input a folder path directly or opens a folder selection dialog if no input is provided. It validates the selected folder path and returns it for further processing in the crabwalk method. If the user provides an invalid path or an error occurs during selection, it handles the exception gracefully and returns None."""

        folder = None
        try:
            folder = input("Enter the path of the folder to crawl (or press Enter to open a folder selection dialog): ").strip()
            if not os.path.isdir(folder):
                raise ValueError(f"Invalid folder path: {folder}")
            else: 
                return folder
        except Exception as e: #scratchy plz
            print(f"Error selecting folder: {e}")
            return None

    def crabwalk(self):
        """Crawl through the user's file system based on user consent preferences. This method prompts the user to select a folder for enumeration, then recursively traverses the selected folder and its subfolders (up to a reasonable depth) to collect metadata and content previews of files while respecting any out-of-scope settings specified by the user. The collected file information is returned as a list of dictionaries, which can then be used for further analysis in the digestion process and summarized in the report card."""

        #（づ￣3￣）づ╭❤️～ approved
        selected_folder = self._pick_folder()
        if not selected_folder:
            print("No folder selected. Cannot crawl file system.")
            return []
        collected_data = []
        for root, dirs, files in os.walk(selected_folder):
            for name in files:
                file_path = os.path.join(root, name)
                filestep = self._build_payload(file_path)
                collected_data.append(filestep)
        print(f"Collected metadata and previews for {len(collected_data)} files from {selected_folder}.")
        return collected_data
MAX_COPY_DEPTH = 2


def filecopy(source_dir, target_bin):
    """Copy a folder into target_bin up to MAX_COPY_DEPTH levels deep. This function takes a source directory and a target binary directory as parameters. It checks if the source directory is valid and then recursively copies its contents to the target directory, maintaining the directory structure up to a specified maximum depth. The function handles errors gracefully and provides feedback on the copying process."""
    if not source_dir:
        print("[filecopy] No source directory provided.")

        return
    source = Path(source_dir)
    if not source.is_dir():
        print(f"[filecopy] Source is not a directory: {source_dir}")


        return
    target = Path(target_bin) / source.name
    try:
        for item in source.rglob("*"):
            depth = len(item.relative_to(source).parts)
            if depth > MAX_COPY_DEPTH:
                continue
            dest = target / item.relative_to(source)
            if item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:

                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
    except Exception as e:

        print(f"[filecopy] Error copying {source_dir} to {target_bin}: {e}")



