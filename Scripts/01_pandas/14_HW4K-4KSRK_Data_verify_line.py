import os
import glob
import pandas as pd
import configparser

# 自动读取脚本同目录的 config.ini
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.ini")

cfg = configparser.ConfigParser(inline_comment_prefixes=(';', '#'))
read_files = cfg.read(config_path, encoding="utf-8")
if not read_files:
    print(f"ERROR: config.ini not found at {config_path}")
    exit(1)

# 用来统计所有比较结果
global_results = []

# 可选文件
optional_files = ["LensZoom", "LensShift"]

# 获取默认 target_path，如果 DEFAULT 没有定义，则 None
default_target_path = cfg["DEFAULT"].get("target_path", None)

# 遍历所有 section
for section in cfg.sections():
    print(f"\nProcessing section: [{section}]")

    base_file   = os.path.normpath(cfg[section]["base_file"])
    # 优先使用 section 的 target_path，否则使用 DEFAULT 的
    target_path = os.path.normpath(cfg[section].get("target_path", default_target_path))
    target_file = cfg[section]["target_file"]
    output_dir  = os.path.normpath(cfg[section]["output_dir"])
    start_line  = int(cfg[section]["start_line"])
    end_line    = int(cfg[section]["end_line"])

    if not target_path:
        print(f"ERROR: target_path not defined for section [{section}]")
        continue

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
        if section in optional_files:
            print(f"WARNING: Optional file [{section}] not found, ignored.")
            continue
        else:
            print(f"ERROR: Target file for [{section}] not found!")
            global_results.append({
                "section": section,
                "folder": "N/A",
                "result": "missing"
            })
            continue

    for file_path in file_list:
        folder_name = os.path.basename(os.path.dirname(file_path))

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()[start_line:end_line]
                data = [line.strip().replace(',', ' ').split() for line in lines]

            result = "same" if base_data == data else "different"

            # 如果不同，打印第一条差异行
            if result == "different":
                for idx, (b, t) in enumerate(zip(base_data, data)):
                    if b != t:
                        human_line = start_line + idx + 1
                        print(f"  DIFFER @ [{section}] folder={folder_name}, line={human_line}")
                        print(f"    base: {b}")
                        print(f"    file: {t}")
                        break
                else:
                    if len(base_data) != len(data):
                        print(f"  DIFFER length @ [{section}] folder={folder_name}: "
                              f"base {len(base_data)} vs file {len(data)}")

        except Exception as e:
            result = f"error: {e}"

        human_range = f"{start_line + 1}-{end_line}"

        results.append({
            "folder": folder_name,
            "range": human_range,
            "result": result
        })

        global_results.append({
            "section": section,
            "folder": folder_name,
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

# ---------------------------------------------------
# ★★★ 最终总结 ★★★
# ---------------------------------------------------
final_status = "OK"

for r in global_results:
    if r["result"] == "same":
        final_status = "NG"
        break

print(f"FINAL RESULT: {final_status}")

summary_file = os.path.join(script_dir, "final_summary.txt")
with open(summary_file, "w", encoding="utf-8-sig") as f:
    f.write(f"FINAL RESULT: {final_status}\n")

print("All sections processed!")
