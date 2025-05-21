import pyvisa
import time

def safe_query_float(instr, command):
    try:
        value = instr.query(command).strip()
        return float(value)
    except Exception:
        return None

def safe_query_str(instr, command):
    try:
        value = instr.query(command).strip()
        return value
    except Exception:
        return None

def initialize_channel(instr, channel):
    """初始化通道，强制打开显示，设置探头倍率和量程"""
    try:
        instr.write(f":CHAN{channel}:DISP ON")  # 开启通道显示
        instr.write(f":CHAN{channel}:PROB 10")  # 设置探头倍率为 1 倍
        instr.write(f":CHAN{channel}:SCAL 2")  # 设置垂直量程，按实际调整
#        instr.write(f":CHAN{channel}:COUP DC")  # 设置耦合方式为直流
        instr.write(f":CHAN{channel}:BAND 20")  # 设置带宽限制为 20 MHz，按实际需要调整
        instr.write(f":TRIG:EDGE:SOU CHAN{channel}")  # 设置触发源为当前通道
        instr.write(f":TRIG:EDGE:LEV 1")  # 设置触发电平为 0 V
    except Exception as e:
        print(f"初始化通道{channel}失败: {e}")

def get_channel_settings(instr, channel):
    """读取通道的探针倍率和垂直量程"""
    prob = safe_query_str(instr, f":CHAN{channel}:PROB?")
    scale = safe_query_str(instr, f":CHAN{channel}:SCAL?")
    return prob, scale

def measure_channel(instr, channel):
    """读取指定通道的平均电压和频率"""
    v_avg = safe_query_float(instr, f":MEAS:VAV? CHAN{channel}")
    freq = safe_query_float(instr, f":MEAS:FREQ? CHAN{channel}")
    return v_avg, freq

def measure_peak_to_peak(instr, channel):
    """读取指定通道的峰-峰值"""
    v_pp = safe_query_float(instr, f":MEAS:VPP? CHAN{channel}")
    return v_pp

def measure_rms(instr, channel):
    """读取指定通道的有效值"""
    v_rms = safe_query_float(instr, f":MEAS:VRMS? CHAN{channel}")
    return v_rms

def measure_max(instr, channel):
    """读取指定通道的最大值"""
    v_max = safe_query_float(instr, f":MEAS:VMAX? CHAN{channel}")
    return v_max

def measure_min(instr, channel):
    """读取指定通道的最小值"""
    v_min = safe_query_float(instr, f":MEAS:VMIN? CHAN{channel}")
    return v_min

rm = pyvisa.ResourceManager()

try:
    scope = rm.open_resource('USB0::0x1AB1::0x0588::DS1ET232202103::INSTR')
    scope.timeout = 3000

    results = {}

    for ch in [1, 2]:
        print(f"\n处理通道 {ch} ...")
        initialize_channel(scope, ch)
        time.sleep(0.5)  # 等待设置生效

        # 读取并打印基础设置
        prob, scale = get_channel_settings(scope, ch)
        print(f"通道{ch} 探针倍率: {prob if prob else '未知'}")
        print(f"通道{ch} 垂直量程: {scale if scale else '未知'}")

        # 读取各种测量值
        v_avg = measure_channel(scope, ch)[0]
        freq = measure_channel(scope, ch)[1]
        v_pp = measure_peak_to_peak(scope, ch)
        v_rms = measure_rms(scope, ch)
        v_max = measure_max(scope, ch)
        v_min = measure_min(scope, ch)

        # 存储结果
        results[ch] = {
            '平均电压': v_avg,
            '频率': freq,
            '峰-峰值': v_pp,
            '有效值': v_rms,
            '最大值': v_max,
            '最小值': v_min
        }

    print("\n最终测量结果：")
    for ch, measurements in results.items():
        print(f"\n通道{ch} 测量结果：")
        for param, value in measurements.items():
            if value is not None:
                print(f"{param}: {value:.3f} V")
            else:
                print(f"{param}: 无效")

finally:
    try:
        scope.write(":KEY:FORCE")  # 退出远程控制，恢复本地操作
    except:
        pass
    try:
        scope.close()
    except:
        pass
    rm.close()
