#读取Raptor laserWB 调整色度的最后一行的一些信息和序列号和时间 20241224

#将04处理完的内容数据转换成一行处理
import csv

def transform_second_column(input_file, output_file):
    """
    将 CSV 文件第二列中的数据，每 3 个一组变成一行存储。

    :param input_file: 输入 CSV 文件路径
    :param output_file: 输出 CSV 文件路径
    """
    with open(input_file, 'r', encoding='utf-8') as in_file:
        reader = csv.reader(in_file)
        # 跳过表头
        header = next(reader, None)

        # 提取第二列数据
        second_column_data = [row[1] for row in reader if len(row) > 1]

    # 将数据每 3 个分为一组
    grouped_data = [second_column_data[i:i+3] for i in range(0, len(second_column_data), 3)]

    # 写入到新的 CSV 文件中
    with open(output_file, 'w', encoding='utf-8', newline='') as out_file:
        writer = csv.writer(out_file)
        for group in grouped_data:
            writer.writerow(group)

# 示例使用
input_file = "temp_output.csv"  # 输入文件路径
output_file = "output.csv"  # 输出文件路径
transform_second_column(input_file, output_file)

print(f"处理完成！结果保存在: {output_file}")


#"C:/Users/Administrator/Desktop/test"
