#Function: TekTronix TDS 2024B init&show measure result
#**.py <USB_Address> <channel1,channel2..>
#**.py USB0::0x0699::0x036A::C032490::INSTR 1,2


import pyvisa
import time
import sys

def safe_query_float(instr, command):
    try:
        value = instr.query(command).strip()
        return float(value)
    except Exception:
        return None

def safe_query_str(instr, command):
    try:
        return instr.query(command).strip()
    except Exception:
        return None

def initialize_channel(instr, ch):
    try:
        instr.write(f"SELECT:CH{ch} ON")          # Enable channel display
        instr.write(f"CH{ch}:PROBE 10")           # Probe attenuation 10x
        instr.write(f"CH{ch}:SCALE 0.5")          # Vertical scale, adjust as needed
        instr.write(f"CH{ch}:BANDWIDTH 20E+6")    # Bandwidth limit 20 MHz
        instr.write(f"TRIGGER:EDGE:SOURCE CH{ch}")
        instr.write(f"TRIGGER:EDGE:LEVEL 0.5")    # Trigger level
    except Exception as e:
        log_print(f"Failed to initialize channel CH{ch}: {e}")

def get_channel_settings(instr, ch):
    prob = safe_query_str(instr, f"CH{ch}:PROBE?")
    scale = safe_query_str(instr, f"CH{ch}:SCALE?")
    return prob, scale

def measure(instr, ch, mtype):
    try:
        instr.write(f"MEASUREMENT:IMMED:SOURCE CH{ch}")
        instr.write(f"MEASUREMENT:IMMED:TYPE {mtype}")
        time.sleep(0.3)  # Wait for measurement to stabilize
        return safe_query_float(instr, "MEASUREMENT:IMMED:VALUE?")
    except Exception as e:
        log_print(f"Failed to measure {mtype} on channel {ch}: {e}")
        return None

def measure_all(instr, ch):
    return {
        "Mean Voltage": measure(instr, ch, "MEAN"),
        "Frequency": measure(instr, ch, "FREQUENCY"),
        "Peak-to-Peak": measure(instr, ch, "PK2pk"),
        "RMS Voltage": measure(instr, ch, "VRMS"),
        "Maximum Voltage": measure(instr, ch, "MAXIMUM"),
        "Minimum Voltage": measure(instr, ch, "MINIMUM")
    }

# 全局文件句柄
log_file = None

def log_print(*args, **kwargs):
    """打印到控制台，并写入日志文件"""
    print(*args, **kwargs)
    if log_file:
        print(*args, **kwargs, file=log_file)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <VISA_ADDRESS> <channel_list, comma separated, e.g. 1,2>")
        sys.exit(1)

    visa_address = sys.argv[1]
    try:
        channels = [int(ch.strip()) for ch in sys.argv[2].split(',') if ch.strip() in ['1','2','3','4']]
        if not channels:
            raise ValueError
    except:
        print("Channel parameter format error. Only digits 1,2,3,4 allowed, separated by commas.")
        sys.exit(1)

    rm = pyvisa.ResourceManager()

    # 打开日志文件（覆盖写）
    with open("measurement_log.txt", "w", encoding="utf-8") as log_file:
        try:
            scope = rm.open_resource(visa_address)
            scope.timeout = 5000

            results = {}

            log_print(f"VISA address: {visa_address}")
            log_print(f"Channels to measure: {channels}")

            for ch in channels:
                log_print(f"\nInitializing channel CH{ch} ...")
                initialize_channel(scope, ch)
                time.sleep(0.5)

                prob, scale = get_channel_settings(scope, ch)
                log_print(f"Channel {ch} probe attenuation: {prob if prob else 'Unknown'}")
                log_print(f"Channel {ch} vertical scale: {scale if scale else 'Unknown'} V/div")

                log_print(f"Starting measurement on channel CH{ch} ...")
                results[ch] = measure_all(scope, ch)

            log_print("\n======= Final Measurement Results =======")
            for ch, measurements in results.items():
                log_print(f"\nChannel {ch} Measurements:")
                for name, val in measurements.items():
                    if val is not None:
                        unit = "Hz" if "Frequency" in name else "V"
                        log_print(f"{name}: {val:.3f} {unit}")
                    else:
                        log_print(f"{name}: Invalid")

        finally:
            try:
                scope.write("LOC")  # Return to local control
            except:
                pass
            try:
                scope.close()
            except:
                pass
            rm.close()
