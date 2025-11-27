import os
import glob
import pandas as pd
import configparser

# 自动读取脚本同目录的 config.ini
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.ini")

# 允许 ; # 作为注释
cfg = configparser.ConfigParser(inline_comment_prefixes=(';', '#'))
read_files = cfg.read(config_path, encoding="utf-8")
if not read_files:
    print(f"ERROR: config.ini not found at {config_path}")
    exit(1)

# 遍历所有 section
for section in cfg.sections():
    print(f"\nProcessing section: [{section}]")

    # 读取配置
    base_file   = os.path.normpath(cfg[section]["base_file"])
    target_path = os.path.normpath(cfg[section]["target_path"])
    target_file = cfg[section]["target_file"]
    output_dir  = os.path.normpath(cfg[section]["output_dir"])
    start_line  = int(cfg[section]["start_line"])
    end_line    = int(cfg[section]["end_line"])

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, "compare_result.csv")
    output_txt = os.path.join(output_dir, "compare_result.txt")

    # 读取 base 文件
    try:
        with open(base_file, 'r', encoding='utf-8-sig') as f:
            base_lines = f.readlines()[start_line:end_line]
            base_data = [line.strip().replace(',', ' ').split() for line in base_lines]
    except Exception as e:
        print(f"ERROR reading base file for section [{section}]: {e}")
        continue

    results = []

    # 搜索目标文件
    file_list = glob.glob(os.path.join(target_path, "**", target_file), recursive=True)

    if not file_list:
        print(f"WARNING: No target files found for [{section}] in {target_path}")

    for file_path in file_list:
        folder_name = os.path.basename(os.path.dirname(file_path))
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()[start_line:end_line]
                data = [line.strip().replace(',', ' ').split() for line in lines]

            result = "same" if base_data == data else "different"
        except Exception as e:
            result = f"error: {e}"

        results.append({
            "folder": folder_name,
            "range": f"{start_line}-{end_line}",
            "result": result
        })

    # 保存 CSV
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    # 保存 TXT
    with open(output_txt, "w", encoding="utf-8-sig") as f:
        for item in results:
            f.write(f"{item['folder']}\t{item['range']}\t{item['result']}\n")

    print(f"Done section [{section}] - CSV: {output_csv}, TXT: {output_txt}")

print("\nAll sections processed!")
