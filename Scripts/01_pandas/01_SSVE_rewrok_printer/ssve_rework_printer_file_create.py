# 对于 单独尾号升级，或者是序列号升级时候，打印机的检测文件
# 用法， 将需要的之番号和序列号弄到 target_file.xlsx 第二行至结束， 对生成一个文件夹和文件

import pandas as pd
import os

# 1. 设置文件路径
input_file = 'Target_file.xlsx'  # 替换成你的文件名
output_folder = 'result'

import pandas as pd
import os

# 2. 如果文件夹不存在则创建
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 3. 读取 Excel (默认 header=0，即从第二行开始是数据)
df = pd.read_excel(input_file)

# 4. 遍历每一行进行处理
for index, row in df.iterrows():
    # 假设 A 列是第一列 (0)，B 列是第二列 (1)
    # 使用 astype(str) 确保拼接的是字符串
    file_name = str(row.iloc[0]) + str(row.iloc[1]) + ".txt"
    file_path = os.path.join(output_folder, file_name)

    # 5. 写入内容 1
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('1')

print(f"处理完成，文件已保存在 {output_folder} 目录下。")