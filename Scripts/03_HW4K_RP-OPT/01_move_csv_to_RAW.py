#20250506
#剪切读取的数据到Raw文件，如果文件下面不是全是csv就报错
import os
import sys
import shutil

def move_csv_files(source_dir, target_dir):
    # 检查源目录是否存在
    if not os.path.isdir(source_dir):
        print(f"错误：源路径不存在 -> {source_dir}")
        sys.exit(1)

    # 检查源目录是否包含非csv文件
    for file_name in os.listdir(source_dir):
        full_path = os.path.join(source_dir, file_name)
        if os.path.isfile(full_path) and not file_name.lower().endswith('.csv'):
            print(f"错误：发现非CSV文件 -> {file_name}")
            sys.exit(1)

    # 创建目标目录（如果不存在）
    os.makedirs(target_dir, exist_ok=True)

    # 移动CSV文件
    for file_name in os.listdir(source_dir):
        full_path = os.path.join(source_dir, file_name)
        if os.path.isfile(full_path):
            shutil.move(full_path, os.path.join(target_dir, file_name))
            print(f"已移动：{file_name}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python move_csv.py <源文件夹路径> <目标文件夹路径>")
        sys.exit(1)

    source = sys.argv[1]
    target = sys.argv[2]
    move_csv_files(source, target)
