#提取等号右边的数据

import pandas as pd
import re

# 读取 Excel 文件
file_path = "C:/Users/Administrator/Desktop/UF_AUTO LOG/Xlsx_2/test.xlsx"  # 替换为您的文件路径
df = pd.read_excel(file_path, header=None)  # 假设没有标题行

# 定义一个函数，用正则提取等号右边的数据
def extract_values(cell):
    if isinstance(cell, str):  # 确保单元格内容是字符串
        return re.findall(r'=\s*([\d.]+)', cell)  # 提取所有等号右边的值
    return []

# 遍历整个 DataFrame，提取数据
result = df.applymap(extract_values)

# 将结果整理为一维列表（按需）
flat_result = [float(val) for sublist in result.values.flatten() if sublist for val in sublist]

# 打印结果
#print(flat_result)

# 保存提取后的结果为新的 Excel 文件（可选）
pd.DataFrame(flat_result, columns=["Extracted Values"]).to_excel("C:/Users/Administrator/Desktop/UF_AUTO LOG/xlsx/output.xlsx", index=False)
