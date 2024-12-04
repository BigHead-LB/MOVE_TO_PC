import pandas as pd

# 读取 CSV 文件
csv_file = "C:/Users/Administrator/Desktop/UF_AUTO LOG/P&S_Number_log.csv"
df = pd.read_csv(csv_file)

# 保存为 Excel 文件
excel_file = "C:/Users/Administrator/Desktop/UF_AUTO LOG/Xlsx_2/P&S_Number_log.xlsx"
df.to_excel(excel_file, index=False, engine='openpyxl')

print(f"CSV 文件已成功转换为 Excel 文件：{excel_file}")
