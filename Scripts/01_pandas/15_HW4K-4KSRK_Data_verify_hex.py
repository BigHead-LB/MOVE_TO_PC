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


def load_hex_dump(path):
    """Load memory dump CSV. Return dict {row_address: [16 bytes]}."""
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    data = {}
    for line in lines[4:]:  # skip first 4 header lines
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        row_addr = int(parts[0], 16)
        bytes_16 = [int(x, 16) for x in parts[1:17]]
        data[row_addr] = bytes_16
    return data


def get_byte(data, addr):
    """Return the byte at absolute address."""
    row = addr & 0xFFFFFFF0
    col = addr & 0x0F
    if row in data:
        return data[row][col]
    return None


def compare_range(base_data, target_data, start_addr, end_addr):
    """Compare two memory dumps in the given address range (inclusive)."""
    for addr in range(start_addr, end_addr + 1):
        b = get_byte(base_data, addr)
        t = get_byte(target_data, addr)
        if b != t:
            return "different"
    return "same"


# ======================
# 遍历所有 section
# ======================
global_results = []
final_status = "OK"
same_folders = []  # 记录出现 same 的文件夹

for section in cfg.sections():
    print(f"\nProcessing section: [{section}]")
    try:
        base_file = os.path.normpath(cfg[section]["base_file"])
        target_file = cfg[section]["target_file"]
        output_dir = os.path.normpath(cfg[section]["output_dir"])
        target_path = os.path.normpath(cfg[section].get("target_path", cfg["DEFAULT"]["target_path"]))
        addr_start = int(cfg[section]["start_line"], 16)
        addr_end = int(cfg[section]["end_line"], 16)
    except Exception as e:
        print(f"ERROR reading config for section [{section}]: {e}")
        final_status = "NG"
        continue

    os.makedirs(output_dir, exist_ok=True)
    csv_output = os.path.join(output_dir, "compare_result.csv")
    txt_output = os.path.join(output_dir, "compare_result.txt")

    # 读取 base 文件
    try:
        base_data = load_hex_dump(base_file)
    except Exception as e:
        print(f"ERROR reading base file for [{section}]: {e}")
        final_status = "NG"
        continue

    results = []

    # 搜索目标文件
    file_list = glob.glob(os.path.join(target_path, "**", target_file), recursive=True)
    if not file_list:
        print(f"ERROR: Target file for [{section}] not found!")
        final_status = "NG"
        continue

    for file_path in file_list:
        folder_name = os.path.basename(os.path.dirname(file_path))
        try:
            target_data = load_hex_dump(file_path)
            result = compare_range(base_data, target_data, addr_start, addr_end)
        except Exception as e:
            result = f"error: {e}"
            final_status = "NG"

        results.append({
            "folder": folder_name,
            "addr_range": f"{hex(addr_start)} - {hex(addr_end)}",
            "result": result
        })

        # 如果出现 same → NG，并记录文件夹
        if result == "same":
            final_status = "NG"
            same_folders.append(f"[{section}] {folder_name}")

        global_results.append({
            "section": section,
            "folder": folder_name,
            "result": result
        })

    # 保存 CSV
    pd.DataFrame(results).to_csv(csv_output, index=False, encoding="utf-8-sig")

    # 保存 TXT
    with open(txt_output, "w", encoding="utf-8-sig") as f:
        for r in results:
            f.write(f"{r['folder']} | {r['addr_range']} | {r['result']}\n")

    print(f"Done section [{section}] - CSV: {csv_output}, TXT: {txt_output}")


# ======================
# 最终汇总
# ======================
final_summary_file = os.path.join(script_dir, "final_summary.txt")
with open(final_summary_file, "w", encoding="utf-8-sig") as f:
    f.write(f"FINAL RESULT: {final_status}\n")
    if same_folders:
        f.write("Folders with SAME result:\n")
        for sf in same_folders:
            f.write(f"{sf}\n")

print(f"\nFINAL RESULT: {final_status}")
if same_folders:
    print("Folders with SAME result:")
    for sf in same_folders:
        print(sf)

print("All sections processed!")
