import pyvisa
import numpy as np
import sys


def log_print(*args, **kwargs):
    print(*args, **kwargs)


def read_current_screen_minimal():
    # 1. 解析命令行参数
    if len(sys.argv) < 2:
        print("用法: python script.py <VISA_ADDRESS> <CH_NUM>")
        sys.exit(1)

    # 清洗地址字符串
    raw_addr = sys.argv[1]
    visa_address = "".join(c for c in raw_addr if ord(c) < 128).strip()

    # 获取通道号
    try:
        ch_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    except:
        ch_num = 1

    rm = pyvisa.ResourceManager()

    try:
        log_print(f"尝试连接: {visa_address}")
        # 打开资源并设置较长的超时
        scope = rm.open_resource(visa_address)
        scope.timeout = 5000

        log_print(f"正在从 CH{ch_num} 提取当前屏幕波形...")

        # 2. 配置传输协议
        scope.write(f"DATA:SOU CH{ch_num}")
        scope.write("DATA:ENC RIB")  # Big-endian signed binary
        scope.write("DATA:WID 2")  # 16-bit

        # 3. 获取缩放系数 (读取电压的关键)
        ymult = float(scope.query("WFMPRE:YMULT?"))
        yoff = float(scope.query("WFMPRE:YOFF?"))
        yzero = float(scope.query("WFMPRE:YZERO?"))
        xincr = float(scope.query("WFMPRE:XINCR?"))

        # 4. 读取原始二进制数据
        # 使用 is_big_endian=True 是因为泰克 TDS 系列通常是大端序
        raw = scope.query_binary_values("CURVE?", datatype='h', is_big_endian=True, container=np.array)

        # 5. 转换为电压和时间
        volts = (raw - yoff) * ymult + yzero
        times = np.arange(len(raw)) * xincr

        # 6. 打印结果
        v_max = np.max(volts)
        v_min = np.min(volts)
        log_print("-" * 30)
        log_print(f"读取点数: {len(volts)}")
        log_print(f"最大电压: {v_max:.3f} V")
        log_print(f"最小电压: {v_min:.3f} V")
        log_print(f"平均电压: {np.mean(volts):.3f} V")
        log_print("-" * 30)

        # 7. 保存文件
        output_file = f"screen_dump_CH{ch_num}.txt"
        np.savetxt(output_file, np.column_stack((times, volts)),
                   header="Time(s)\tVoltage(V)", fmt="%.6f")
        log_print(f"数据已保存至: {output_file}")

    except Exception as e:
        log_print(f"读取过程中发生错误: {e}")
        log_print("提示: 请确保示波器处于 STOP 状态，且屏幕上有正常波形。")
    finally:
        try:
            scope.close()
        except:
            pass
        rm.close()


if __name__ == "__main__":
    read_current_screen_minimal()