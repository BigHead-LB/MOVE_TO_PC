#20250506
#delete file

import os
import shutil
import sys


def delete_files_and_folders(path):
    # 检查路径是否存在
    if not os.path.exists(path):
        print(f"错误: 路径 {path} 不存在！")
        return

    # 遍历目录中的所有内容
    for root, dirs, files in os.walk(path, topdown=False):
        # 删除所有文件
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                print(f"已删除文件: {file_path}")
            except Exception as e:
                print(f"删除文件 {file_path} 失败: {e}")

        # 删除所有子目录
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                shutil.rmtree(dir_path)
                print(f"已删除文件夹: {dir_path}")
            except Exception as e:
                print(f"删除文件夹 {dir_path} 失败: {e}")

    # 最后删除指定的根目录（如果需要）
    try:
        shutil.rmtree(path)
        print(f"已删除根目录: {path}")
    except Exception as e:
        print(f"删除根目录 {path} 失败: {e}")


# 主函数：从命令行获取路径参数
if __name__ == "__main__":
    # 检查是否提供了路径参数
    if len(sys.argv) != 2:
        print("用法: python delete_files.py <目录路径>")
    else:
        folder_path = sys.argv[1]  # 获取命令行传入的路径
        delete_files_and_folders(folder_path)
