#PDA36A2 这个，output 0-10V，
#当前 Gain 60，测试1 带涂层的，
#最终 gain 50 适合一点

import pyvisa
import numpy as np
import sys
import time
import configparser
import os
import matplotlib.pyplot as plt

log_buffer = []

def log_print(*args, **kwargs):

    message = " ".join(str(arg) for arg in args)

    print(message, **kwargs)

    log_buffer.append(message)


# load config
config = configparser.ConfigParser()
config.read("config.ini")

# read config
visa_address = config["SCOPE"]["visa_address"]
ch_num = int(config["SCOPE"]["channel"])

capture_seconds = float(config["SCOPE"]["capture_seconds"])
horizontal_scale = float(config["SCOPE"]["horizontal_scale"])

target_points = int(config["SCOPE"]["target_points"])

probe_ratio = float(config["SCOPE"]["probe_ratio"])

serial_number = config["SCOPE"]["serial_number"]

median_filter_k = int(config["FILTER"]["median_filter_k"])


# filter
def simple_medfilt(x, k=105):
    """
    纯 numpy 实现的一维中值滤波
    x: 输入数组 (电压数据)
    k: 窗口大小 (必须是奇数, 如 3, 5, 7)
    """

    # 确保 k 是奇数
    k = k if k % 2 == 1 else k + 1

    edge = k // 2

    # 为了处理边界，在原始数组两端填充一些数据
    # 'edge' 模式会重复边界值，避免滤波后边缘出现 0
    x_padded = np.pad(x, (edge, edge), mode='edge')

    # 构建滑动窗口矩阵
    # 这是一个比较巧妙的 numpy 技巧，能避免写 Python 循环，速度很快
    # 对于 100k 条数据，这种矩阵化操作效率最高
    stacked = np.zeros((len(x), k))

    for i in range(k):
        stacked[:, i] = x_padded[i: i + len(x)]

    # 在每一行取中位数
    return np.median(stacked, axis=1)


# generate waveform png
def generate_plot(times, volts, output_png, title):

    plt.figure(figsize=(16, 6))

    plt.plot(times, volts)

    plt.title(title)

    plt.xlabel("Time (s)")

    plt.ylabel("Voltage (V)")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(output_png, dpi=200)

    plt.close()

    log_print(f"波形图已保存: {output_png}")


# filter the noisy
def process_existing_file(filename):

    try:

        log_print(f"正在处理: {filename}")

        data = np.loadtxt(filename, skiprows=1, delimiter='\t')

        ids = data[:, 0]
        times = data[:, 1]
        volts = data[:, 2]

        # 1. 执行中值滤波
        volts_cleaned = simple_medfilt(volts, k=median_filter_k)

        # 2. 计算波动率: (MAX - MIN) / Ave
        v_max = np.max(volts_cleaned)

        v_min = np.min(volts_cleaned)

        v_ave = np.mean(volts_cleaned)

        # 防止除以 0
        variation = (v_max - v_min) / abs(v_ave) if v_ave != 0 else 0

        # 3. 保存滤波后的文件
        output_name = filename.replace(".txt", "_cleaned.txt")

        new_data = np.column_stack((ids, times, volts_cleaned))

        np.savetxt(
            output_name,
            new_data,
            header="id\tTime(s)\tVoltage(V)",
            fmt=["%d", "%.6f", "%.6f"],
            delimiter="\t",
            comments=''
        )

        # generate cleaned waveform png
        cleaned_png_file = output_name.replace(".txt", ".png")

        generate_plot(
            times,
            volts_cleaned,
            cleaned_png_file,
            f"DPO4104 CH{ch_num} Cleaned Waveform"
        )

        log_print(f"处理成功: {output_name}")

        # --- 新增：打印 Filter 后的统计数据 ---
        log_print(
            f"Filter 后统计 -> 最大: {v_max:.3f} V, "
            f"最小: {v_min:.3f} V, "
            f"平均: {v_ave:.3f} V"
        )

        # --- 关键修改：返回计算结果 ---
        return variation

    except Exception as e:

        log_print(f"处理失败: {e}")

        return None


# 在你采集完数据后手动调用即可
# process_existing_file("dpo4104_10s_CH1.txt")

def capture_dpo4104_100k_shot():

    rm = pyvisa.ResourceManager()

    try:

        # create output folder
        result_folder = os.path.join(
            "Tektronix_Dpo4104_result",
            serial_number
        )

        os.makedirs(result_folder, exist_ok=True)

        log_print(f"尝试连接 DPO4104: {visa_address}")

        scope = rm.open_resource(visa_address)

        # 增加超时时间，10万点传输需要一点时间
        scope.timeout = 30000

        # 2. 示波器底层配置
        scope.write("HEADER OFF")

        # --- 关键修正：执行远程 Autoset 解决看不到信号的问题 ---
        log_print("执行远程 Autoset 以寻找信号...")

        scope.write("AUTOSet EXECute")

        time.sleep(3)  # 等待示波器自动调整完成

        scope.write("ACQuire:STATE STOP")

        # --- 修正内容：在 Autoset 基础上强制修正倍率和记录长度 ---
        log_print(f"正在优化通道 CH{ch_num} 配置...")

        scope.write(f"CH{ch_num}:PRObe {probe_ratio}")

        # 重新锁定我们要的参数，因为 Autoset 会改掉它们
        scope.write(f"HORizontal:RECOrdlength {target_points}")

        scope.write(f"HORizontal:SCAle {horizontal_scale}")

        scope.write("ACQuire:STOPAfter SEQuence")

        # ---------------------------------------------------------

        log_print(
            f"开始 {capture_seconds} 秒单次采样 "
            f"(采样点数: {target_points}, CH{ch_num})..."
        )

        scope.write("ACQuire:STATE ON")

        # 强制触发确保开始采集
        time.sleep(0.5)

        scope.write("TRIGGER FORCE")

        # 3. 等待采集结束 (DPO系列 BUSY? 非常可靠)
        while scope.query("BUSY?").strip() == "1":
            time.sleep(0.2)

        log_print(f"采集完成，正在提取 {target_points} 个点的数据...")

        # 4. 配置传输协议
        scope.write(f"DATA:SOUrce CH{ch_num}")

        scope.write("DATA:ENCdg RIBinary")  # 16位大端序

        scope.write("DATA:WIDth 2")

        scope.write("DATA:START 1")

        scope.write(f"DATA:STOP {target_points}")

        # 5. 获取缩放系数
        ymult = float(scope.query("WFMPRE:YMULT?"))

        yoff = float(scope.query("WFMPRE:YOFF?"))

        yzero = float(scope.query("WFMPRE:YZERO?"))

        xincr = float(scope.query("WFMPRE:XINCR?"))

        # 6. 读取二进制数据
        raw = scope.query_binary_values(
            "CURVE?",
            datatype='h',
            is_big_endian=True,
            container=np.array
        )

        # 7. 转换为电压和时间
        volts = (raw - yoff) * ymult + yzero

        times = np.arange(len(raw)) * xincr

        # 准备 ID 列 (从1开始)
        ids = np.arange(1, len(volts) + 1)

        # 8. 打印简要统计结果 (修改：包含最大、最小、平均)
        v_max_raw = np.max(volts)

        v_min_raw = np.min(volts)

        v_ave_raw = np.mean(volts)

        log_print("-" * 30)

        log_print(f"Filter 前原始数据统计 (CH{ch_num}):")

        log_print(f"实际读取点数: {len(volts)}")

        log_print(f"最大电压: {v_max_raw:.3f} V")

        log_print(f"最小电压: {v_min_raw:.3f} V")

        log_print(f"平均电压: {v_ave_raw:.3f} V")

        log_print("-" * 30)

        # 9. 保存文件 (ID Time Voltage 格式)
        output_file = os.path.join(
            result_folder,
            f"dpo4104_CH{ch_num}.txt"
        )

        # 合并数据并保存
        combined_data = np.column_stack((ids, times, volts))

        np.savetxt(
            output_file,
            combined_data,
            header="id\tTime(s)\tVoltage(V)",
            fmt=["%d", "%.6f", "%.6f"],
            delimiter="\t",
            comments=''
        )

        # generate raw waveform png
        raw_png_file = os.path.join(
            result_folder,
            f"dpo4104_CH{ch_num}.png"
        )

        generate_plot(
            times,
            volts,
            raw_png_file,
            f"DPO4104 CH{ch_num} Raw Waveform"
        )

        log_print(f"数据已成功保存至: {output_file}")

        return output_file  # 确保 main 能够拿到文件名

    except Exception as e:

        log_print(f"读取过程中发生错误: {e}")

        return None

    finally:

        try:

            scope.write("ACQuire:STATE RUN")  # 任务结束，让示波器恢复运行

            scope.close()

        except:
            pass

        rm.close()


if __name__ == "__main__":

    # capture the waveform
    capture_dpo4104_single_shot = capture_dpo4104_100k_shot

    output_path = capture_dpo4104_single_shot()

    # filter the noisy
    if output_path:

        result_variation = process_existing_file(output_path)

        if result_variation is not None:

            log_print(
                f"\n信号的最终波动率为: "
                f"{result_variation:.4f} "
                f"(即 {result_variation:.2%})"
            )

            # save result log
            result_txt_path = os.path.join(
                "Tektronix_Dpo4104_result",
                serial_number,
                "result.txt"
            )

            with open(result_txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(log_buffer))


            # 你现在可以在这里根据这个变量做任何你想做的操作
            if result_variation > 0.20:

                # 做你想做的事，比如触发报警、记录日志等
                pass