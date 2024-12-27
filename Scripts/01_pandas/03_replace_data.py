

import pandas as pd
import re

# 读取 Excel 文件
file_path = "C:/Users/Administrator/Desktop/UF_AUTO LOG/Xlsx_2/xlsx_rdeltdata.xlsx"  # 替换为您的文件路径
df = pd.read_excel(file_path, header=None)  # 假设没有标题行

# 定义一个函数，提取等号右边的值
def replace_with_value(cell):
    if isinstance(cell, str):  # 确保单元格内容是字符串
        match = re.search(r'=\s*([\d.]+)', cell)  # 找到等号右边的值
        if match:
            return float(match.group(1))  # 提取值并返回
    return cell  # 如果没有匹配，保持原样

# 应用替换到整个 DataFrame
df_replaced = df.applymap(replace_with_value)

# 将替换后的数据保存回原位置（覆盖原 Excel 文件）
df_replaced.to_excel(file_path, index=False, header=False)

print("替换完成！")


