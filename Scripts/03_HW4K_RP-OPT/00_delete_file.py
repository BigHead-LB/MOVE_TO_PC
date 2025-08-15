# 20250704 delete file
# Method 1: delete specific files
#   python delete_files.py E:\TestFolder A.csv,B.txt,C.log

# Method 2: delete all files/folders
#   python delete_files.py E:\TestFolder

import os
import shutil
import sys
import stat
import io

# Fix encoding issues for special characters in Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def handle_remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def is_drive_root(path):
    path = os.path.abspath(path.rstrip("\\/"))
    drive, tail = os.path.splitdrive(path)
    return tail == ''

def delete_files_and_folders(path):
    path = os.path.abspath(path)
    is_root = is_drive_root(path)
    print(f"Deleting {'root directory contents' if is_root else 'entire directory'}: {path}")

    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Failed to delete file: {file_path} ({type(e).__name__}: {e})")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                shutil.rmtree(dir_path, onerror=handle_remove_readonly)
                print(f"Deleted folder: {dir_path}")
            except Exception as e:
                print(f"Failed to delete folder: {dir_path} ({type(e).__name__}: {e})")

    if not is_root:
        try:
            shutil.rmtree(path, onerror=handle_remove_readonly)
            print(f"Deleted root directory: {path}")
        except Exception as e:
            print(f"Failed to delete root directory: {path} ({type(e).__name__}: {e})")
    else:
        print(f"Cleared contents of root directory (directory itself kept): {path}")

def delete_specific_files(path, file_list):
    path = os.path.abspath(path)
    for file_name in file_list:
        file_path = os.path.join(path, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted specific file: {file_path}")
            except Exception as e:
                print(f"Failed to delete file: {file_path} ({type(e).__name__}: {e})")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_files.py <directory_path> [file1,file2,...]")
    else:
        folder_path = sys.argv[1]
        if not os.path.exists(folder_path):
            print(f"Error: Path does not exist: {folder_path}")
        elif len(sys.argv) == 3:
            # Delete specific files
            file_names = sys.argv[2].split(',')
            delete_specific_files(folder_path, file_names)
        else:
            # Delete all contents in the directory
            delete_files_and_folders(folder_path)
