import os
import glob
import pandas as pd

base_file = r"C:\Users\Administrator\Desktop\XW5000_initial\pd_gamma.csv"
root_dir = r"E:\7000"

# 保存结果的文件夹
output_dir = r"C:\Users\Administrator\Desktop\Gamma_compare"
os.makedirs(output_dir, exist_ok=True)  # 如果目录不存在就创建

output_file = os.path.join(output_dir, "compare_result_60P.xlsx")

# 手动读取基准文件
with open(base_file, 'r', encoding='utf-8-sig') as f:
    base_lines = f.readlines()[4:387]  # 5-387行
    # 拆分每行
    base_data = [line.strip().replace(',', ' ').split() for line in base_lines]

results = []

file_list = glob.glob(os.path.join(root_dir, "**", "pd_gamma.csv"), recursive=True)


for file_path in file_list:
    folder_name = os.path.basename(os.path.dirname(file_path))
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()[4:387]
            data = [line.strip().replace(',', ' ').split() for line in lines]

        # 比较数据
        is_same = base_data == data
        result = "same" if is_same else "different"

    except Exception as e:
        result = f"error: {e}"

    results.append({
        "folder": folder_name,
        "range": "5-387",
        "result": result
    })

pd.DataFrame(results).to_excel(output_file, index=False)
print(f"完成！比较结果已保存到：{output_file}")
