#获取laserWB 下面的 lvmax 和ratio数据
#Date Serial lvmax ratio
#20250122

import os
import pandas as pd

# 文件夹路径和输出文件路径
input_folder = r"C:\Users\Administrator\Desktop\Test"  # 修改为你的文件夹路径
output_file = r"C:\Users\Administrator\Desktop\Test\output.csv"  # 输出文件路径

# 初始化一个空的 DataFrame，用于存储结果
output_data = []

# 遍历目标文件夹及其子文件夹
for root, dirs, files in os.walk(input_folder):
    for file in files:
        # 筛选文件名为 "laser_wb_log_2D.csv"
        if file == "laser_wb_log_2D.csv":
            file_path = os.path.join(root, file)
            try:
                # 尝试读取文件并提取第二列
                data = pd.read_csv(file_path, header=None, on_bad_lines="skip", engine="python")  # 跳过问题行
                second_column = data.iloc[:, 1]  # 提取第二列

                # 获取第1、3、14、15、16行数据（索引为0、2、13、14、15）
                rows_to_extract = [0, 2, 13, 14, 15]
                extracted_values = [second_column[i] if i < len(second_column) else None for i in rows_to_extract]

                # 将提取的结果追加到列表中
                output_data.append(extracted_values)

                print(f"成功处理文件: {file_path}")
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")

# 将结果保存到新的 CSV 文件
output_df = pd.DataFrame(output_data, columns=["Row1", "Row3", "Row14", "Row15", "Row16"])
output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"所有数据已提取并保存到: {output_file}")
