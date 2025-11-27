import os
import glob
import pandas as pd
import configparser
import traceback
import sys

# =======================
# 全局异常处理
# =======================
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

error_log_file = os.path.join(script_dir, "error_log.txt")

def log_error(msg):
    """记录错误到文件，同时在控制台打印"""
    print(msg)
    with open(error_log_file, "a", encoding="utf-8-sig") as ef:
        ef.write(msg + "\n")

def global_exception_hook(exctype, value, tb):
    with open(error_log_file, "a", encoding="utf-8-sig") as f:
        f.write("=== Unhandled Exception ===\n")
        traceback.print_exception(exctype, value, tb, file=f)
    print(f"ERROR! See {error_log_file} for details.")
    traceback.print_exception(exctype, value, tb)

sys.excepthook = global_exception_hook

# =======================
# 读取配置
# =======================
config_path = os.path.join(script_dir, "config.ini")
cfg = configparser.ConfigParser(inline_comment_prefixes=(';', '#'))
read_files = cfg.read(config_path, encoding="utf-8")
if not read_files:
    raise FileNotFoundError(f"config.ini not found at {config_path}")

default_target_path = cfg["DEFAULT"].get("target_path", None)

# =======================
# 全局结果
# =======================
global_results = []

# =======================
# 遍历 config.ini 中 sections
# =======================
for section in cfg.sections():
    print(f"\nProcessing section: [{section}]")
    try:
        base_file   = os.path.normpath(cfg[section]["base_file"])
        target_file = cfg[section]["target_file"]
        output_dir  = os.path.normpath(cfg[section]["output_dir"])
        target_path = os.path.normpath(cfg[section].get("target_path", default_target_path))
        addr_start  = int(cfg[section]["start_line"], 16)
        addr_end    = int(cfg[section]["end_line"], 16)
    except Exception as e:
        log_error(f"ERROR reading config for section [{section}]: {e}")
        global_results.append({"section": section, "folder": "N/A", "result": "config_error"})
        continue

    os.makedirs(output_dir, exist_ok=True)
    csv_output = os.path.join(output_dir, "compare_result.csv")
    txt_output = os.path.join(output_dir, "compare_result.txt")

    # =======================
    # 读取 base 文件
    # =======================
    try:
        with open(base_file, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
        base_data = {}
        for line in lines[4:]:
            line = line.strip()
            if not line or not line[0].isalnum():  # 跳过非地址行
                continue
            parts = line.split(",")
            try:
                row_addr = int(parts[0], 16)
            except ValueError:
                continue
            bytes_16 = [int(x, 16) for x in parts[1:17]]
            base_data[row_addr] = bytes_16
    except Exception as e:
        log_error(f"ERROR reading base file for [{section}]: {e}\n{traceback.format_exc()}")
        global_results.append({"section": section, "folder": "N/A", "result": "base_read_error"})
        continue

    # =======================
    # 处理目标文件
    # =======================
    target_file_path = os.path.join(target_path, target_file)
    if not os.path.exists(target_file_path):
        log_error(f"ERROR: Target file for [{section}] not found: {target_file_path}")
        global_results.append({"section": section, "folder": "N/A", "result": "missing"})
        continue

    folder_name = os.path.basename(os.path.dirname(target_file_path))
    results = []

    try:
        with open(target_file_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
        target_data = {}
        for line in lines[4:]:
            line = line.strip()
            if not line or not line[0].isalnum():
                continue
            parts = line.split(",")
            try:
                row_addr = int(parts[0], 16)
            except ValueError:
                continue
            bytes_16 = [int(x, 16) for x in parts[1:17]]
            target_data[row_addr] = bytes_16

        # 比较函数
        def get_byte(data, addr):
            row = addr & 0xFFFFFFF0
            col = addr & 0x0F
            if row in data:
                return data[row][col]
            return None

        def compare_range(base_data, target_data, start_addr, end_addr):
            for addr in range(start_addr, end_addr + 1):
                b = get_byte(base_data, addr)
                t = get_byte(target_data, addr)
                if b != t:
                    return "different"
            return "same"

        result = compare_range(base_data, target_data, addr_start, addr_end)
        if result == "same":
            same_flag = True
        else:
            same_flag = False

        results.append({
            "folder": folder_name,
            "addr_range": f"{hex(addr_start)} - {hex(addr_end)}",
            "result": result
        })

        global_results.append({
            "section": section,
            "folder": folder_name,
            "result": result
        })

    except Exception as e:
        log_error(f"ERROR processing target file {target_file_path} for section [{section}]: {e}\n{traceback.format_exc()}")
        global_results.append({"section": section, "folder": folder_name, "result": f"error: {e}"})

    # =======================
    # 保存 CSV 和 TXT
    # =======================
    try:
        pd.DataFrame(results).to_csv(csv_output, index=False, encoding="utf-8-sig")
    except Exception as e:
        log_error(f"ERROR writing CSV for section [{section}]: {e}\n{traceback.format_exc()}")

    try:
        with open(txt_output, "w", encoding="utf-8-sig") as f:
            for r in results:
                f.write(f"{r['folder']} | {r['addr_range']} | {r['result']}\n")
    except Exception as e:
        log_error(f"ERROR writing TXT for section [{section}]: {e}\n{traceback.format_exc()}")

    print(f"Done section [{section}] - CSV: {csv_output}, TXT: {txt_output}")

# =======================
# 最终汇总
# =======================
final_status = "OK"
same_folders = []

for r in global_results:
    if r["result"] == "same":
        final_status = "NG"
        same_folders.append(f"{r['section']} -> {r['folder']}")

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
print(f"Any errors are logged in {error_log_file} (if occurred).")
