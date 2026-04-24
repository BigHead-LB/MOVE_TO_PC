import pyvisa
import numpy as np
import time
import os
from PySide6.QtCore import QObject, Signal


# --- 算法：中值滤波 ---
def simple_medfilt(x, k=5):
    k = k if k % 2 == 1 else k + 1
    edge = k // 2
    x_padded = np.pad(x, (edge, edge), mode='edge')
    stacked = np.zeros((len(x), k))
    for i in range(k):
        stacked[:, i] = x_padded[i: i + len(x)]
    return np.median(stacked, axis=1)


# --- 逻辑模块 2：读取原始 TXT 并创建滤波后的 TXT ---
def filter_raw_file(input_filename):
    if not os.path.exists(input_filename):
        raise FileNotFoundError(f"找不到原始文件: {input_filename}")

    # 1. 加载刚才保存的原始数据
    data = np.loadtxt(input_filename, skiprows=1, delimiter='\t')
    ids, times, volts = data[:, 0], data[:, 1], data[:, 2]

    # 2. 滤波
    volts_cleaned = simple_medfilt(volts, k=5)

    # 3. 创建滤波后的 TXT 文件
    output_filename = input_filename.replace(".txt", "_cleaned.txt")
    new_data = np.column_stack((ids, times, volts_cleaned))
    np.savetxt(output_filename, new_data,
               header="id\tTime(s)\tVoltage(V)",
               fmt=["%d", "%.6f", "%.6f"],
               delimiter="\t",
               comments='')
    return output_filename


# --- 逻辑模块 3：计算波动率 ---
def calculate_variation(cleaned_filename):
    data = np.loadtxt(cleaned_filename, skiprows=1, delimiter='\t')
    volts = data[:, 2]

    # --- 关键修改：必须先计算基础值，确保 v_max, v_min 在任何分支都存在 ---
    v_max = np.max(volts)
    v_min = np.min(volts)
    v_ave = np.mean(volts)

    # 检查是否全为零或无效数据（空负载常见情况）
    if abs(v_ave) < 1e-9:  # 均值接近0
        variation = 0.0
    else:
        # 修改点：确保这里计算并赋值给 variation
        variation = (v_max - v_min) / abs(v_ave)

    # 确保无论走哪个分支，都返回 4 个值
    return variation, v_max, v_min, v_ave


# --- UI 线程 Worker ---
class ScopeWorker(QObject):
    finished = Signal(float)
    error = Signal(str)
    status_update = Signal(str)

    def __init__(self, visa_address, ch_num):
        super().__init__()
        self.visa_address = visa_address
        self.ch_num = ch_num

    def run_capture_task(self):
        """完整的三步走流水线逻辑"""
        rm = pyvisa.ResourceManager()
        scope = None
        try:

            # --- 步骤 1: 物理采集并创建原始 TXT ---
            self.status_update.emit(f"步骤 1: 正在连接示波器 {self.visa_address}...")
            scope = rm.open_resource(self.visa_address)
            scope.timeout = 35000

            # 写入完整的配置指令
            scope.write("HEADER OFF")
            scope.write("ACQuire:STATE STOP")
            scope.write("HORizontal:RECOrdlength 100000")
            scope.write("HORizontal:SCAle 1.0")
            scope.write("ACQuire:STOPAfter SEQuence")

            self.status_update.emit("开始 10 秒采样 (请稍候)...")
            scope.write("ACQuire:STATE ON")
            time.sleep(0.5)
            scope.write("TRIGGER FORCE")

            # --- 保护：防止 BUSY? 陷入死循环 ---
            start_wait_time = time.time()
            while scope.query("BUSY?").strip() == "1":
                time.sleep(0.5)
                # 如果 15 秒还没采样结束，说明示波器状态异常
                if time.time() - start_wait_time > 15:
                    raise TimeoutError("示波器采样超时，请检查通道是否连接或触发设置。")

            self.status_update.emit("采集完成，正在从内存提取数据...")

            # 配置数据传输参数
            scope.write(f"DATA:SOUrce CH{self.ch_num}")
            scope.write("DATA:ENCdg RIBinary")
            scope.write("DATA:WIDth 2")
            scope.write("DATA:START 1")
            scope.write("DATA:STOP 100000")

            # 获取缩放因子
            ymult = float(scope.query("WFMPRE:YMULT?"))
            yoff = float(scope.query("WFMPRE:YOFF?"))
            yzero = float(scope.query("WFMPRE:YZERO?"))
            xincr = float(scope.query("WFMPRE:XINCR?"))

            # 读取原始二进制曲线
            raw = scope.query_binary_values("CURVE?", datatype='h', is_big_endian=True, container=np.array)

            # --- 保护：检查读取的数据是否有效 ---
            if raw is None or len(raw) < 100:
                raise ValueError(f"读取到的波形数据过短或为空（CH{self.ch_num}），请检查通道是否开启。")

            # 物理单位转换
            probe_ratio = 10  # 你的探头是 10X
            volts = ((raw - yoff) * ymult + yzero) * probe_ratio
            times = np.arange(len(volts)) * xincr
            ids = np.arange(1, len(volts) + 1)

            # 保存原始文件
            raw_filename = f"dpo4104_10s_CH{self.ch_num}.txt"
            combined_data = np.column_stack((ids, times, volts))
            np.savetxt(raw_filename, combined_data,
                       header="id\tTime(s)\tVoltage(V)",
                       fmt=["%d", "%.6f", "%.6f"],
                       delimiter="\t",
                       comments='')
            # 后台输出读取成功信息
            print(f"\n[后台信息] 数据读取完毕，原始文件已保存：{raw_filename}")


            # --- 步骤 2: 处理原始文件生成 Cleaned 文件 ---
            self.status_update.emit("步骤 2: 正在处理原始 TXT 并生成滤波文件...")
            cleaned_filename = filter_raw_file(raw_filename)

            # --- 步骤 3: 读取 Cleaned 文件计算结果 ---
            self.status_update.emit("步骤 3: 正在读取滤波结果并计算波动率...")
            # 调用修改后的计算函数，获取所有统计值
            result_variation, vmax, vmin, vave = calculate_variation(cleaned_filename)

            # --- 后台打印详细统计结果 ---
            print("=" * 40)
            print("执行分析完毕:")
            print(f"  - 最大值: {vmax:.6f} V")
            print(f"  - 最小值: {vmin:.6f} V")
            print(f"  - 平均值: {vave:.6f} V")
            print(f"  - 波动率: {result_variation:.4%}")
            print("=" * 40)

            self.status_update.emit("全部流程执行成功！")

            # 在发送完成信号前，尝试恢复示波器运行状态
            try:
                scope.write("ACQuire:STATE RUN")
                scope.close()
                scope = None
            except:
                pass

            self.finished.emit(result_variation)

        except Exception as e:
            # 捕获所有硬件断开、误触或数据异常，发送给主界面显示
            print(f"\n[后台报错] 发生异常: {e}")
            self.error.emit(str(e))
        finally:
            if scope:
                try:
                    scope.close()
                except:
                    pass
            rm.close()