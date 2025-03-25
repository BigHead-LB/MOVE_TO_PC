#获取 Raptor LaserWB 中的 时间，序列号，和最后一行的Luminance	Y_IREF	B_IREF	R_IREF	X	Y	Z

import os
import csv

#读取laser_wb log的第一行，第3行，最后一行 #20241217
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

#读取Raptor laserWB 调整色度的最后一行的一些信息和序列号和时间 20241224
#将04处理完的内容数据转换成一行处理
def transform_second_column(input_file, output_file):
    """
    将 CSV 文件第二列中的数据，每 3 个一组变成一行存储。

    :param input_file: 输入 CSV 文件路径
    :param output_file: 输出 CSV 文件路径
    """
    with open(input_file, 'r', encoding='utf-8') as in_file:
        reader = csv.reader(in_file)
        # 跳过表头
        header = next(reader, None)

        # 提取第二列数据
        second_column_data = [row[1] for row in reader if len(row) > 1]

    # 将数据每 3 个分为一组
    grouped_data = [second_column_data[i:i+3] for i in range(0, len(second_column_data), 3)]

    # 写入到新的 CSV 文件中
    with open(output_file, 'w', encoding='utf-8', newline='') as out_file:
        writer = csv.writer(out_file)
        for group in grouped_data:
            writer.writerow(group)

#将数据都提取出来
def clean_and_split_csv(input_file, output_file):
    """
    读取 CSV 文件，去除 `\"`，并清理数据格式
    """
    cleaned_data = []

    with open(input_file, 'r', encoding='utf-8') as in_file:
        reader = csv.reader(in_file, delimiter='\t')  # 读取时用制表符分割

        for row in reader:
            flat_list = []
            for item in row:
                # 去掉 `\"` 和其他特殊字符
                item = item.replace("[", "").replace("]", "").replace("'", "").replace(":", "").replace("\"", "").strip()
                flat_list.extend(item.split(","))  # 处理可能的逗号分隔
            cleaned_data.append(flat_list)

    # **正确写入 CSV，避免 `\"`**
    with open(output_file, 'w', encoding='utf-8', newline='') as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)  # 仅在必要时加引号
        writer.writerows(cleaned_data)

    print(f"✅ 处理完成！清理后的数据保存在: {output_file}")

# 使用示例 1
base_folder = "C:/Users/Administrator/Desktop/test"  # 根文件夹路径
target_file_name = "laser_wb_log_2D.csv"  # 需要提取的同名CSV文件
temp_output_file1 = "temp_output1.csv"  # 输出的汇总CSV文件

extract_csv_data(base_folder, target_file_name, temp_output_file1)

print(f"处理完成！结果保存在: {temp_output_file1}")

# 示例使用 2
input_file = temp_output_file1  # 输入文件路径
temp_output_file2 = "temp_output2.csv"  # 输出文件路径
transform_second_column(input_file, temp_output_file2)

print(f"处理完成！结果保存在: {temp_output_file2}")


# 示例使用 3
input_file = temp_output_file2  # 你的原始 CSV 文件
target_output_file = "target_output.csv"  # 处理后的 CSV 文件

clean_and_split_csv(input_file, target_output_file)



