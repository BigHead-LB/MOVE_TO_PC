import pandas as pd
import os

def normalize_with_index(df):
    """生成 (行内容 tuple, 行号) 列表"""
    df = df.fillna('')
    row_list = []
    for i, row in df.iterrows():
        row_list.append((tuple(row), i + 2))  # Excel 行号从2开始（包含表头）
    return row_list

def compare_excel_sheets(file1, file2):
    xl1 = pd.ExcelFile(file1)
    xl2 = pd.ExcelFile(file2)

    common_sheets = set(xl1.sheet_names) & set(xl2.sheet_names)
    if not common_sheets:
        print("❌ 两个文件没有共同的工作表。")
        return

    base1 = os.path.splitext(os.path.basename(file1))[0]
    base2 = os.path.splitext(os.path.basename(file2))[0]

    output_dir = "comparison_output"
    os.makedirs(output_dir, exist_ok=True)
    log_rows = []

    for i, sheet in enumerate(xl1.sheet_names):
        if sheet not in common_sheets:
            continue

        df1 = xl1.parse(sheet).iloc[:, :3]  # 只取前3列
        df2 = xl2.parse(sheet).iloc[:, :3]

        list1 = normalize_with_index(df1)
        list2 = normalize_with_index(df2)

        set1 = set(row for row, _ in list1)
        set2 = set(row for row, _ in list2)

        only_in_file1 = set1 - set2
        only_in_file2 = set2 - set1

        row_index_map1 = {row: idx for row, idx in list1 if row in only_in_file1}
        row_index_map2 = {row: idx for row, idx in list2 if row in only_in_file2}

        for row in only_in_file1:
            log_rows.append({
                "Sheet 名": sheet,
                "来源": base1,
                "原始行号": row_index_map1[row],
                "行内容": ', '.join(map(str, row))
            })
        for row in only_in_file2:
            log_rows.append({
                "Sheet 名": sheet,
                "来源": base2,
                "原始行号": row_index_map2[row],
                "行内容": ', '.join(map(str, row))
            })

    if log_rows:
        log_df = pd.DataFrame(log_rows)
        log_path = os.path.join(output_dir, "compare_log.xlsx")
        log_df.to_excel(log_path, index=False)
        print(f"📄 差异已保存到：{log_path}")
    else:
        print("✅ 所有 sheet 完全一致，无差异。")

# 示例调用
compare_excel_sheets(
    r"C:\Users\Administrator\Desktop\register\HW4K\register\3_soft1&protect_aging_insp&insp2&exfactory\ID_Jav_20250709_V003.xlsx",
    r"C:\Users\Administrator\Desktop\register\HW4K\register\exfactory\ID_Jav_202008xx.xlsx"
)
