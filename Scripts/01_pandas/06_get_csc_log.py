#读取Raptor 中间，测量的RGB OPT初始亮度和色度 20241224


import os
import csv

def extract_and_append_data(base_folder, output_file):
    """
    从多个CSV文件中提取第二列是'RED'、'GREEN'或'BLUE'的行，提取前5个单元格，并将当前文件中A2、A5、A8分别添加到6、7、8单元格。
    最终结果写入新的CSV文件。

    :param base_folder: 包含多个CSV文件的文件夹路径
    :param output_file: 输出CSV文件路径
    """
    target_colors = {"RED", "GREEN", "BLUE"}  # 目标颜色
    extracted_data = []

    # 遍历文件夹中的所有CSV文件
    for root, _, files in os.walk(base_folder):
        for file_name in files:
            if file_name.endswith('.csv'):  # 只处理CSV文件
                file_path = os.path.join(root, file_name)

                # 读取A2、A5、A8的内容
                with open(file_path, 'r', encoding='utf-8') as in_file:
                    reader = list(csv.reader(in_file))
                    if len(reader) > 8:  # 确保文件至少有A2、A5、A8
                        a2 = reader[1][0] if len(reader[1]) > 0 else ""
                        a5 = reader[4][0] if len(reader[4]) > 0 else ""
                        a8 = reader[7][0] if len(reader[7]) > 0 else ""
                    else:
                        a2, a5, a8 = "", "", ""  # 如果没有A2、A5、A8，设置为空字符串

                # 提取第二列符合条件的行，并拼接A2、A5、A8
                with open(file_path, 'r', encoding='utf-8') as in_file:
                    reader = csv.reader(in_file)
                    next(reader, None)  # 跳过标题行

                    for row in reader:
                        # 检查第二列是否为目标颜色
                        if len(row) > 1 and row[1] in target_colors:
                            # 提取前5个单元格并拼接A2、A5、A8
                            new_row = row[:5] + [a2, a5, a8]
                            extracted_data.append(new_row)

    # 将提取的数据写入新的CSV文件
    with open(output_file, 'w', encoding='utf-8', newline='') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(['Col1', 'Col2', 'Col3', 'Col4', 'Col5', 'A2', 'A5', 'A8'])  # 写入表头
        writer.writerows(extracted_data)

# 使用示例
base_folder = "C:/Users/Administrator/Desktop/test"  # 替换为CSV文件所在的目录路径
output_file = "output.csv"      # 输出文件路径

extract_and_append_data(base_folder, output_file)

print(f"处理完成！提取的数据已保存至: {output_file}")
