#获取gamma文件下面的2D_120HZ_Normal下面的gamma数据
#最终获得 Date Time SerialNumber LV	Xr	Yr	Zr	Xg	Yg	Zg	Xb	Yb	Zb
#20250122

import os
import csv


# 设置根目录路径
root_directory = r"C:\Users\Administrator\Desktop\Test"

# 设置输出 CSV 文件路径
output_file = 'output.csv'

# 打开输出 CSV 文件进行写入
with open(output_file, mode='w', newline='') as output_csv:
    writer = csv.writer(output_csv)

    # 写入 CSV 文件头
    writer.writerow(['DATE', 'TIME', 'SERIAL NUMBER', '72nd Row After Sub Mode'])

    # 遍历文件夹中的所有 CSV 文件
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)

                # 打开每个 CSV 文件
                with open(file_path, mode='r', newline='', encoding='utf-8') as input_csv:
                    reader = csv.reader(input_csv)
                    rows = list(reader)

                    date_content = None
                    time_content = None
                    serial_number_content = None
                    sub_mode_found = False
                    sub_mode_row = None

                    # 遍历每一行以查找所需数据
                    for i in range(len(rows)):
                        # 提取 DATE, TIME, SERIAL NUMBER 下一行的内容
                        if rows[i] and rows[i][0] == 'DATE' and i + 1 < len(rows):
                            date_content = rows[i + 1][0]
                        if rows[i] and rows[i][0] == 'TIME' and i + 1 < len(rows):
                            time_content = rows[i + 1][0]
                        if rows[i] and rows[i][0] == 'SERIAL NUMBER' and i + 1 < len(rows):
                            serial_number_content = rows[i + 1][0]

                        # 查找 SUB MODE 和 2D_Normal_120Hz
                        if i + 1 < len(rows) and rows[i] and rows[i+1] and rows[i][0] == 'SUB MODE' and rows[i+1][0] == '2D_Normal_120Hz':
                            sub_mode_found = True
                            sub_mode_row = i + 75  # 获取第72行后的行号

                    # 如果找到 SUB MODE 和 2D_Normal_120Hz，并且有第 72 行
                    if sub_mode_found and sub_mode_row < len(rows):
                        target_row = rows[sub_mode_row]
                        new_row = [date_content, time_content, serial_number_content, target_row]
                        writer.writerow(new_row)
