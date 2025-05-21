#20250506
#读取和返回目标文件是多少bit

import os
import sys

def get_file_size_in_bits(file_path):
    if not os.path.isfile(file_path):
        print(f"错误：文件不存在 -> {file_path}")
        sys.exit(1)

    size_bytes = os.path.getsize(file_path)
    size_bits = size_bytes * 8
    print(f"文件大小: {size_bits} bit")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python file_size_bits.py <文件路径>")
        sys.exit(1)

    file_path = sys.argv[1]
    get_file_size_in_bits(file_path)