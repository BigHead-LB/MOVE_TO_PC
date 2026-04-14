import os
import pandas as pd

# 需要合并的 CSV 文件夹路径
folder = r"C:\Users\Administrator\Desktop\test\Raptor9Point_202512\9PointRP-202504"

# 合并后的输出文件
output_file = r"C:\Users\Administrator\Desktop\test\Raptor9Point_202512\9PointRP-202504\merged.csv"

# 存放每个CSV的DataFrame
dfs = []

for file in os.listdir(folder):
    if file.endswith(".csv"):
        file_path = os.path.join(folder, file)
        print("读取:", file_path)
        df = pd.read_csv(file_path)
        dfs.append(df)

# 合并
merged_df = pd.concat(dfs, ignore_index=True)

# 保存
merged_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("合并完成! 输出文件:", output_file)
