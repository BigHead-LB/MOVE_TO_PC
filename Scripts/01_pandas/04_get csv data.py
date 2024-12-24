#读取laser_wb log的第一行，第3行，最后一行 #20241217


import os
import csv

def extract_csv_data(base_folder, target_file_name, output_file):
    """
    提取所有子文件夹中同名CSV文件的第一行、第三行和最后一行数据，写入到一个新的CSV中。

    输出格式为三列：
    - 第一列：Row Type（First Row, Third Row, Last Row）
    - 第二列：Data
    - 第三列：文件路径 (Folder Path + File Name)
    """
    with open(output_file, 'w', encoding='utf-8', newline='') as out_file:
        writer = csv.writer(out_file)
        # 写入表头
        writer.writerow(["Row Type", "Data", "File Path"])

        # 遍历所有子文件夹和文件
        for root, _, files in os.walk(base_folder):
            for file_name in files:
                # 检查文件是否为目标文件
                if file_name == target_file_name:
                    file_path = os.path.join(root, file_name)

                    # 读取当前CSV文件
                    with open(file_path, 'r', encoding='utf-8') as in_file:
                        reader = csv.reader(in_file)
                        rows = list(reader)

                        # 如果文件为空，跳过
                        if not rows:
                            continue

                        # 获取第一行、第三行和最后一行
                        first_row = rows[0] if len(rows) > 0 else None
                        third_row = rows[2] if len(rows) > 2 else None
                        last_row = rows[-1] if len(rows) > 0 else None

                        # 将结果写入输出文件
                        if first_row:
                            writer.writerow(["First Row", first_row, file_path])
                        if third_row:
                            writer.writerow(["Third Row", third_row, file_path])
                        if last_row:
                            writer.writerow(["Last Row", last_row, file_path])


# 使用示例
base_folder = "C:/Users/Administrator/Desktop/test"  # 根文件夹路径
target_file_name = "laser_wb_log_2D.csv"  # 需要提取的同名CSV文件
output_file = "temp_output.csv"  # 输出的汇总CSV文件

extract_csv_data(base_folder, target_file_name, output_file)

print(f"处理完成！结果保存在: {output_file}")
