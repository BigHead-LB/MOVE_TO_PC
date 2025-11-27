#20251125
#check the csv file
#verify A.csv and B.csv, begin line5: memory address A-B value same or not
#example:
#python compare.py C:/base/pd_gamma.csv C:/daily/20251120 pd_gamma.csv C:/output 0x00000000 0x00017FFF

import os
import glob
import pandas as pd
import sys


def load_hex_dump(path):
    """Load memory dump CSV. Return dict {row_address: [16 bytes]}."""
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    data = {}

    # Data begins at line index 4 (line 5). First 4 lines are header/info.
    for line in lines[4:]:
        line = line.strip()
        if not line:
            continue

        parts = line.split(",")

        row_addr = int(parts[0], 16)            # Example: 0x00000040
        bytes_16 = [int(x, 16) for x in parts[1:17]]

        data[row_addr] = bytes_16

    return data


def get_byte(data, addr):
    """Return the byte value for the absolute address."""
    row = addr & 0xFFFFFFF0    # row base address (16 bytes aligned)
    col = addr & 0x0F          # column offset 0–15

    if row in data:
        return data[row][col]
    return None


def compare_range(base_data, target_data, start_addr, end_addr):
    """Compare two memory tables in the given address range."""
    for addr in range(start_addr, end_addr + 1):
        b = get_byte(base_data, addr)
        t = get_byte(target_data, addr)
        if b != t:
            return "different"
    return "same"


# ======================
# Main Program
# ======================
if len(sys.argv) != 7:
    print("Usage: python compare.py <base_file> <target_path> <target_file> <output_dir> <addr_start> <addr_end>")
    print("Example: python compare.py C:/base/base.csv C:/daily pd_gamma.csv C:/out 0x0000024D 0x0000194E")
    sys.exit(1)

base_file = os.path.normpath(sys.argv[1])
target_path = os.path.normpath(sys.argv[2])
target_file = sys.argv[3]
output_dir = os.path.normpath(sys.argv[4])

try:
    addr_start = int(sys.argv[5], 16)   # hex address
    addr_end = int(sys.argv[6], 16)
except:
    print("Address must be hex format, example: 0x0000024D")
    sys.exit(1)

# Output files
os.makedirs(output_dir, exist_ok=True)
csv_output = os.path.join(output_dir, "compare_result.csv")
txt_output = os.path.join(output_dir, "compare_result.txt")

# Load base memory dump
base_data = load_hex_dump(base_file)

results = []

# Search target files
file_list = glob.glob(os.path.join(target_path, "**", target_file), recursive=True)

for file_path in file_list:
    folder_name = os.path.basename(os.path.dirname(file_path))

    try:
        target_data = load_hex_dump(file_path)
        result = compare_range(base_data, target_data, addr_start, addr_end)
    except Exception as e:
        result = f"error: {e}"

    results.append({
        "folder": folder_name,
        "addr_range": f"{sys.argv[5]} - {sys.argv[6]}",
        "result": result
    })

# Save CSV
pd.DataFrame(results).to_csv(csv_output, index=False, encoding="utf-8-sig")

# Save TXT
with open(txt_output, "w", encoding="utf-8-sig") as f:
    for r in results:
        f.write(f"{r['folder']} | {r['addr_range']} | {r['result']}\n")

print(f"Done!")
print(f"CSV saved to: {csv_output}")
print(f"TXT saved to: {txt_output}")
