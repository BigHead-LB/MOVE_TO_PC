import pyvisa
import numpy as np
import sys
import time


def log_print(*args, **kwargs):
    print(*args, **kwargs)

#filter
def simple_medfilt(x, k=5):
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


# filter the noisy
def process_existing_file(filename):
    try:
        log_print(f"正在处理: {filename}")
        data = np.loadtxt(filename, skiprows=1, delimiter='\t')

        ids = data[:, 0]
        times = data[:, 1]
        volts = data[:, 2]

        # 1. 执行中值滤波
        volts_cleaned = simple_medfilt(volts, k=5)

        # 2. 计算波动率: (MAX - MIN) / Ave
        v_max = np.max(volts_cleaned)
        v_min = np.min(volts_cleaned)
        v_ave = np.mean(volts_cleaned)

        # 防止除以 0
        variation = (v_max - v_min) / abs(v_ave) if v_ave != 0 else 0

        # 3. 保存滤波后的文件
        output_name = filename.replace(".txt", "_cleaned.txt")
        new_data = np.column_stack((ids, times, volts_cleaned))
        np.savetxt(output_name, new_data,
                   header="id\tTime(s)\tVoltage(V)",
                   fmt=["%d", "%.6f", "%.6f"],
                   delimiter="\t",
                   comments='')

        log_print(f"处理成功: {output_name}")

        # --- 关键修改：返回计算结果 ---
        return variation

    except Exception as e:
        log_print(f"处理失败: {e}")
        return None

# 在你采集完数据后手动调用即可
# process_existing_file("dpo4104_10s_CH1.txt")

def capture_dpo4104_100k_shot():
    # 1. 解析命令行参数
    if len(sys.argv) < 2:
        print("用法: python script.py <VISA_ADDRESS> <CH_NUM>")
        sys.exit(1)

    raw_addr = sys.argv[1]
    visa_address = "".join(c for c in raw_addr if ord(c) < 128).strip()

    try:
        ch_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    except:
        ch_num = 1

    # 目标参数设置
    target_points = 100000  # 10万点

    rm = pyvisa.ResourceManager()

    try:
        log_print(f"尝试连接 DPO4104: {visa_address}")
        scope = rm.open_resource(visa_address)
        # 增加超时时间，10万点传输需要一点时间
        scope.timeout = 30000

        # 2. 示波器底层配置
        scope.write("HEADER OFF")
        scope.write("ACQuire:STATE STOP")

        # 设置记录长度为 100,000 点
        scope.write(f"HORizontal:RECOrdlength {target_points}")
        # 设置时基为 1s/div (全屏10s)
        scope.write("HORizontal:SCAle 1.0")
        # 设置单次触发模式
        scope.write("ACQuire:STOPAfter SEQuence")

        log_print(f"开始 10 秒单次采样 (采样率: 10k S/s, CH{ch_num})...")
        scope.write("ACQuire:STATE ON")

        # 强制触发确保开始采集
        time.sleep(0.5)
        scope.write("TRIGGER FORCE")

        # 3. 等待采集结束 (DPO系列 BUSY? 非常可靠)
        while scope.query("BUSY?").strip() == "1":
            time.sleep(0.2)
        log_print("采集完成，正在提取 100,000 个点的数据...")

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
        raw = scope.query_binary_values("CURVE?", datatype='h', is_big_endian=True, container=np.array)

        # 7. 转换为电压和时间
        volts = (raw - yoff) * ymult + yzero
        times = np.arange(len(raw)) * xincr

        # 准备 ID 列 (从1开始)
        ids = np.arange(1, len(volts) + 1)

        # 8. 打印简要统计结果
        log_print("-" * 30)
        log_print(f"实际读取点数: {len(volts)}")
        log_print(f"最大电压: {np.max(volts):.3f} V")
        log_print(f"平均电压: {np.mean(volts):.3f} V")
        log_print("-" * 30)

        # 9. 保存文件 (ID Time Voltage 格式)
        output_file = f"dpo4104_10s_CH{ch_num}.txt"

        # 合并数据并保存
        # fmt: 第一列整数，后两列6位小数。delimiter: \t 实现 Excel 对齐
        combined_data = np.column_stack((ids, times, volts))
        np.savetxt(output_file, combined_data,
                   header="id\tTime(s)\tVoltage(V)",
                   fmt=["%d", "%.6f", "%.6f"],
                   delimiter="\t",
                   comments='')

        log_print(f"数据已成功保存至: {output_file}")

    except Exception as e:
        log_print(f"读取过程中发生错误: {e}")
    finally:
        try:
            scope.write("ACQuire:STATE RUN")  # 任务结束，让示波器恢复运行
            scope.close()
        except:
            pass
        rm.close()


if __name__ == "__main__":
    #capture the waveformk
    capture_dpo4104_single_shot = capture_dpo4104_100k_shot
    capture_dpo4104_single_shot()

    #filter the noisy
    result_variation = process_existing_file("dpo4104_10s_CH1.txt")

    if result_variation is not None:
        log_print(f"\n信号的最终波动率为: {result_variation:.4f} (即 {result_variation:.2%})")

        # 你现在可以在这里根据这个变量做任何你想做的操作
        if result_variation > 0.20:
            # 做你想做的事，比如触发报警、记录日志等
            pass