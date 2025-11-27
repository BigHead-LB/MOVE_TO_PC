import pandas as pd

file1 = r"C:\Users\Administrator\Desktop\XW5000_initial\pd_gamma.csv"
file2 = r"C:\Phoenix\Log\AdjData\92227100\3000276\pd_gamma.csv"

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# 比较差异
diff = df1.compare(df2)

print("差异内容：")
print(diff)

# 如果想输出到文件
diff.to_csv("diff_output.csv")
print("\n差异已输出到 diff_output.csv")
