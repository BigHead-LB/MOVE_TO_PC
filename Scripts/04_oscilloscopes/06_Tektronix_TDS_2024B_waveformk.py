#address
#USB0::0x0699::0x036A::C032490::INSTR 1

import pyvisa
import time
import sys
import numpy as np


# ================= 工具函数 =================

def log_print(*args, **kwargs):
    print(*args, **kwargs)


# ================= 核心采集函数 =================

def capture_segmented_10s(instr, ch, filename):
    all_volts = []
    all_times = []

    try:
        # 1. 初始化设置
        instr.write("HEADER OFF")
        instr.write("ACQuire:STATE STOP")

        # --- 垂直参数：探头设为 1X ---
        instr.write(f"CH{ch}:PRObe 1")  # <--- 已修改为 1
        instr.write(f"CH{ch}:SCAle 1.0")  # 1V/div (5V信号占5格)
        instr.write(f"CH{ch}:POSition 0")
        instr.write(f"CH{ch}:COUpling DC")

        # --- 水平参数：1s 总长 (100ms/div) ---
        instr.write("HORizontal:SCAle 0.1")
        instr.write("ACQuire:MODe SAMPLE")

        segments = 10
        log_print(f"--- 开始 10 段拼接采集 (CH{ch}, Probe 1X) ---")

        for i in range(segments):
            log_print(f"正在采集第 {i + 1}/{segments} 段...")

            # 2. 触发单次采集
            instr.write("ACQuire:STOPAfter SEQuence")
            instr.write("ACQuire:STATE ON")

            # 强制触发
            time.sleep(0.1)
            instr.write("TRIGGER FORCE")

            # 3. 关键：等待示波器忙碌结束
            while instr.query("BUSY?").strip() == "1":
                time.sleep(0.1)

            # 4. 数据传输配置
            instr.write(f"DATA:SOUrce CH{ch}")
            instr.write("DATA:ENCdg RIBinary")
            instr.write("DATA:WIDth 2")

            # 获取转换系数
            actual_pt = int(instr.query("WFMPRE:NR_PT?"))
            x_incr = float(instr.query("WFMPRE:XINCR?"))
            ymult = float(instr.query("WFMPRE:YMULT?"))
            yoff = float(instr.query("WFMPRE:YOFF?"))
            yzero = float(instr.query("WFMPRE:YZERO?"))

            # 读取原始二进制数据 (Big-Endian)
            raw = instr.query_binary_values("CURVE?", datatype='h', is_big_endian=True, container=np.array)

            # 电压转换公式
            volts = (raw - yoff) * ymult + yzero
            # 时间轴拼接（每段偏移 1.0 秒）
            times = (np.arange(len(raw)) * x_incr) + (i * 1.0)

            all_volts.append(volts)
            all_times.append(times)

        # 5. 数据拼接与下采样
        final_volts = np.concatenate(all_volts)
        final_times = np.concatenate(all_times)

        # 抽稀到 1000 个点以满足保存要求
        target_pts = 1000
        step = max(1, len(final_volts) // target_pts)
        resampled_volts = final_volts[::step][:target_pts]
        resampled_times = final_times[::step][:target_pts]

        # 6. 保存到文件
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Index\tTime(s)\tVoltage(V)\n")
            for idx, (t, v) in enumerate(zip(resampled_times, resampled_volts)):
                f.write(f"{idx}\t{t:.6f}\t{v:.6f}\n")

        log_print("-" * 35)
        log_print(f"拼接采集成功！")
        log_print(f"最大电压: {np.max(final_volts):.3f} V")
        log_print(f"最小电压: {np.min(final_volts):.3f} V")
        log_print(f"文件保存为: {filename}")
        log_print("-" * 35)

    except Exception as e:
        log_print(f"采集报错: {e}")


# ================= 主程序 =================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <VISA_ADDRESS> <CH_NUM>")
        sys.exit(1)

    # 清洗 VISA 地址
    raw_addr = sys.argv[1]
    visa_address = "".join(c for c in raw_addr if ord(c) < 128).strip()

    try:
        ch_to_capture = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    except:
        ch_to_capture = 1

    rm = pyvisa.ResourceManager()

    try:
        log_print(f"正在建立连接: {visa_address}")
        scope = rm.open_resource(visa_address)
        scope.timeout = 15000  # 15秒超时

        output_file = f"waveform_CH{ch_to_capture}_10s_concat.txt"
        capture_segmented_10s(scope, ch_to_capture, output_file)

    except Exception as e:
        log_print(f"初始化失败: {e}")

    finally:
        try:
            scope.write("ACQuire:STATE RUN")  # 恢复运行
            scope.close()
        except:
            pass
        rm.close()
        log_print("Done.")