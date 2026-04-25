import shutil
import os
import computerspeak as cs
from pathlib import Path


class FileShuttle:
    def __init__(self):
        pass
    
    def unzip_file(self, zip_path: str, extract_to: str):
        """Unzip a file from zip_path to extract_to directory. This function takes the path of a zip file and the target directory where the contents should be extracted. It uses the shutil library to perform the extraction and includes error handling to catch and report any issues that may arise during the unzipping process. The function provides feedback on whether the file was successfully unzipped or if an error occurred."""
        try:
            shutil.unpack_archive(zip_path, extract_to)
            print(f"File unzipped from {zip_path} to {extract_to}")
        except Exception as e:
            print(f"Error unzipping file: {e}")
    def upload_file(self, local_path: str, remote_path: str):
        """Upload a file from local_path to remote_path. This function takes the path of a local file and the target path where the file should be uploaded. It uses the shutil library to perform the file copy and includes error handling to catch and report any issues that may arise during the upload process. The function provides feedback on whether the file was successfully uploaded or if an error occurred."""
        try:
            shutil.copy(local_path, remote_path)
            print(f"File uploaded from {local_path} to {remote_path}")
        except Exception as e:
            print(f"Error uploading file: {e}")
    def copy_file(self, source: str, destination: str):
        """Copy a file from source to destination. This function takes the path of the source file and the destination path where the file should be copied. It uses the shutil library to perform the file copy and includes error handling to catch and report any issues that may arise during the copying process. The function provides feedback on whether the file was successfully copied or if an error occurred."""

        try:
            shutil.copy(source, destination)
            print(f"File copied from {source} to {destination}")
        except Exception as e:
            print(f"Error copying file: {e}")
    def create_file(self, file_path: str, content: str):
        """Create a file at the specified file path with the given content. This function takes a file path and a content string as input and attempts to create a new file at the specified location with the provided content. It includes error handling to catch and report any issues that may arise during the file creation process, and it provides feedback on whether the file was successfully created or if an error occurred."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"File created: {file_path}")
        except Exception as e:
            print(f"Error creating file: {e}") #i can't believe i forgot this. it's so basic. :D
    def move_file(self, source: str, destination: str):
        """Move a file from source to destination. This function takes the path of the source file and the destination path where the file should be moved. It uses the shutil library to perform the file move and includes error handling to catch and report any issues that may arise during the moving process. The function provides feedback on whether the file was successfully moved or if an error occurred."""
        try:
            shutil.move(source, destination)
            print(f"File moved from {source} to {destination}")
        except Exception as e:
            print(f"Error moving file: {e}")
    
    def delete_file(self, file_path: str):
        """Delete a file at the specified file path. This function takes a file path as input and attempts to delete the file at the specified location. It includes error handling to catch and report any issues that may arise during the file deletion process, and it provides feedback on whether the file was successfully deleted or if an error occurred."""
        try:
            os.remove(file_path)
            print(f"File deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {e}")
    def list_directory(self, directory: str):
        """List all files in the specified directory."""
        try:
            files = os.listdir(directory)
            print(f"Files in directory {directory}:")
            for file in files:
                print(file)
            return files
        except Exception as e:
            print(f"Error listing directory: {e}")
    def create_directory(self, directory: str):
        """Create a directory at the specified path. This function takes a directory path as input and attempts to create a new directory at the specified location. It includes error handling to catch and report any issues that may arise during the directory creation process, and it provides feedback on whether the directory was successfully created or if an error occurred."""
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Directory created: {directory}")
        except Exception as e:
            print(f"Error creating directory: {e}")
    def delete_directory(self, directory: str):
        """Delete a directory at the specified path."""
        try:
            shutil.rmtree(directory)
            print(f"Directory deleted: {directory}")
        except Exception as e:
            print(f"Error deleting directory: {e}")
    def file_read(self, file_path: str, stop_event=None):
        """Read a file line by line, optionally stopping if a stop event is set."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if stop_event is not None and stop_event.is_set():
                        break
                    print(line.rstrip("\n"))
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    def directory_zip(self, directory: str, zip_path: str):
        """Zip a directory to the specified zip path. This function takes a directory path and a target zip file path as input and attempts to create a zip archive of the specified directory at the target location. It uses the shutil library to perform the zipping and includes error handling to catch and report any issues that may arise during the zipping process. The function provides feedback on whether the directory was successfully zipped or if an error occurred."""
        try:
            shutil.make_archive(zip_path, 'zip', directory)
            print(f"Directory {directory} zipped to {zip_path}.zip")
        except Exception as e:
            print(f"Error zipping directory: {e}")#:D we can use this to zip up the surzsenviro folder at the end and move it to the new host. :D or establish multiple hosts!!! so many options.
    #forgot we can just cs.execute_command to serve files :D




if __name__ == "__main__":
    fs_i = FileShuttle()
