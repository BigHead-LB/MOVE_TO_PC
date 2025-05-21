#20250506
#Copy文件夹到目标文件，没路会报错
#Copy exe 也是可以，支持任意文件类型
import os
import shutil
import sys

def copy_directory(src, dst):
    # 获取源文件夹名称
    src_basename = os.path.basename(os.path.normpath(src))
    dst_path = os.path.join(dst, src_basename)

    try:
        shutil.copytree(src, dst_path)
        print(f"已成功复制目录 {src} 到 {dst_path}")
    except FileExistsError:
        print(f"目标文件夹 {dst_path} 已存在，复制中止。")
    except Exception as e:
        print(f"目录复制失败: {e}")

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        print(f"已成功复制文件 {src} 到 {dst}")
    except Exception as e:
        print(f"文件复制失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python script.py <源路径（文件夹或文件）> <目标文件夹路径>")
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]

    if not os.path.exists(source):
        print(f"源路径不存在: {source}")
        sys.exit(1)
    if not os.path.isdir(destination):
        print(f"目标路径不存在: {destination}")
        sys.exit(1)

    if os.path.isdir(source):
        copy_directory(source, destination)
    elif os.path.isfile(source):
        copy_file(source, destination)
    else:
        print("仅支持复制文件夹或单个文件")
