# 获取laserWB下面的 lvmax 和ratio数据
# Date Serial lvmax ratio
# 20250122

import os
import pandas as pd
from datetime import datetime

# 文件夹路径和输出文件路径
input_folder = r"C:\Users\Administrator\Desktop\Test"
output_file = r"C:\Users\Administrator\Desktop\Test\Ratio_output.csv"

# 初始化一个空的列表，用于存储结果
output_data = []

def convert_timestamp(ts):
    """
    将各种格式的时间强制转换为标准格式：
    输入例：20250414104044 / 2025/04/14 10:40:44 / 2025-04-14 10:40:44
    输出统一为：2025-04-14 10:40:44
    """
    try:
        # 强制转字符串并清理不必要字符
        ts = str(ts).strip()
        for ch in ["/", "-", " ", ":"]:
            ts = ts.replace(ch, "")

        # 时间戳必须是14位数字
        if len(ts) != 14 or not ts.isdigit():
            return None

        dt = datetime.strptime(ts, "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    except:
        return None


# 遍历文件夹
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file == "laser_wb_log_2D.csv":
            file_path = os.path.join(root, file)
            try:
                # 强制把所有列读取为字符串，避免自动格式化
                data = pd.read_csv(
                    file_path, header=None, on_bad_lines="skip",
                    engine="python", dtype=str
                )

                second_column = data.iloc[:, 1]

                # 提取第 1、3、14、15、16 行
                rows_to_extract = [0, 2, 13, 14, 15]
                extracted_values = [
                    second_column[i] if i < len(second_column) else None
                    for i in rows_to_extract
                ]

                row1_value = extracted_values[0]
                row2_value = convert_timestamp(row1_value)   # ⭐ 新增：强制格式化的 Row2

                # 按指定顺序组合成最终行
                new_row = [
                    row1_value,         # Row1
                    row2_value,         # ⭐ Row2 转换后的时间
                    extracted_values[1], # Row3
                    extracted_values[2], # Row14
                    extracted_values[3], # Row15
                    extracted_values[4]  # Row16
                ]

                output_data.append(new_row)
                print(f"成功处理文件: {file_path}")

            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")


# 保存 CSV
output_df = pd.DataFrame(
    output_data,
    columns=["Row1", "Row2", "Row3", "Row14", "Row15", "Row16"]
)

output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"所有数据已提取并保存到: {output_file}")
