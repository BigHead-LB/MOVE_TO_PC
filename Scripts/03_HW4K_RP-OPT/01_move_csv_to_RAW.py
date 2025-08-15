import os
import sys
import shutil

def move_csv_files_current_dir(source_dir, target_dir):
    if not os.path.isdir(source_dir):
        print(f"Error: Source path does not exist -> {source_dir}")
        sys.exit(1)

    os.makedirs(target_dir, exist_ok=True)

    for file_name in os.listdir(source_dir):
        if file_name.lower().endswith('.csv'):
            src_path = os.path.join(source_dir, file_name)
            if os.path.isfile(src_path):
                dst_path = os.path.join(target_dir, file_name)
                try:
                    if os.path.exists(dst_path):
                        os.remove(dst_path)  # 强制覆盖
                    shutil.move(src_path, dst_path)
                    print(f"Moved: {src_path} → {dst_path}")
                except Exception as e:
                    print(f"Failed to move {src_path}: {e}")

def move_specific_files(source_dir, filenames, target_dir):
    if not os.path.isdir(source_dir):
        print(f"Error: Source path does not exist -> {source_dir}")
        sys.exit(1)

    os.makedirs(target_dir, exist_ok=True)

    for file_name in filenames:
        src_path = os.path.join(source_dir, file_name)
        if not os.path.isfile(src_path):
            print(f"Warning: File not found -> {src_path}")
            continue
        dst_path = os.path.join(target_dir, file_name)
        try:
            if os.path.exists(dst_path):
                os.remove(dst_path)  # 强制覆盖
            shutil.move(src_path, dst_path)
            print(f"Moved: {src_path} → {dst_path}")
        except Exception as e:
            print(f"Failed to move {src_path}: {e}")

if __name__ == "__main__":
    args = sys.argv

    if len(args) == 3:
        source = args[1]
        target = args[2]
        move_csv_files_current_dir(source, target)

    elif len(args) == 4 and args[2].startswith('[') and args[2].endswith(']'):
        source = args[1]
        file_list_str = args[2][1:-1]
        file_list = [f.strip() for f in file_list_str.split(',') if f.strip()]
        target = args[3]
        move_specific_files(source, file_list, target)

    else:
        print("Usage:")
        print("1) Move all CSV files in folder:")
        print("   python move_csv.py <source_folder_path> <target_folder_path>")
        print("2) Move specific files:")
        print("   python move_csv.py <source_folder_path> <[file1.csv,file2.csv,...]> <target_folder_path>")
