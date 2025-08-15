# 20250704
# Copy directory, single file, or selected files from a folder
# python script.py E:\MyProject D:\Backup
# python script.py E:\Tools\tool.exe D:\Backup
# python script.py E:\Data [A.csv,B.log,C.exe] D:\Backup

import os
import shutil
import sys
import io

# Prevent encoding errors on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def copy_file(src_path, dst_path):
    try:
        if os.path.exists(dst_path):
            os.remove(dst_path)  # 强制覆盖
        shutil.copy2(src_path, dst_path)
        print(f"Copied file: {src_path} → {dst_path}")
    except Exception as e:
        print(f"Failed to copy file: {src_path} → {dst_path} ({e})")

def copy_directory(src, dst):
    src_basename = os.path.basename(os.path.normpath(src))
    dst_path = os.path.join(dst, src_basename)

    if os.path.exists(dst_path):
        print(f"Target directory {dst_path} exists, removing it before copy...")
        try:
            shutil.rmtree(dst_path)
        except Exception as e:
            print(f"Failed to remove existing directory {dst_path}: {e}")
            return
    try:
        shutil.copytree(src, dst_path)
        print(f"Copied directory: {src} → {dst_path}")
    except Exception as e:
        print(f"Failed to copy directory: {e}")

def copy_selected_files(src_folder, filenames, dst_folder):
    for fname in filenames:
        src_path = os.path.join(src_folder, fname)
        dst_path = os.path.join(dst_folder, fname)
        if not os.path.exists(src_path):
            print(f"Source file does not exist: {src_path}")
        else:
            copy_file(src_path, dst_path)

if __name__ == "__main__":
    args = sys.argv

    if len(args) == 4 and args[2].startswith('[') and args[2].endswith(']'):
        # Copy specific files from source folder
        source_dir = args[1]
        file_list_str = args[2][1:-1]
        file_list = [f.strip() for f in file_list_str.split(',') if f.strip()]
        dest_dir = args[3]

        if not os.path.isdir(source_dir):
            print(f"Source folder does not exist: {source_dir}")
            sys.exit(1)

        if not os.path.exists(dest_dir):
            print(f"Destination folder does not exist: {dest_dir}, creating it.")
            os.makedirs(dest_dir)

        copy_selected_files(source_dir, file_list, dest_dir)

    elif len(args) == 3:
        # Copy entire directory or single file
        source = args[1]
        destination = args[2]

        if not os.path.exists(source):
            print(f"Source path does not exist: {source}")
            sys.exit(1)

        if not os.path.exists(destination):
            print(f"Destination path does not exist: {destination}, creating it.")
            os.makedirs(destination)

        if os.path.isdir(source):
            copy_directory(source, destination)
        elif os.path.isfile(source):
            dst_file_path = os.path.join(destination, os.path.basename(source))
            copy_file(source, dst_file_path)
        else:
            print("Only directories or files are supported.")
    else:
        print("Usage:")
        print("1) Copy directory or single file:")
        print("   python script.py <source_path> <destination_path>")
        print("2) Copy selected files from folder:")
        print("   python script.py <source_folder> [file1,file2,...] <destination_folder>")
