import pyvisa
import time
import sys
import numpy as np

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
        instr.write(f"SELECT:CH{ch} ON")
        instr.write(f"CH{ch}:PROBE 1")    # 探头设置为 1:1
        instr.write(f"CH{ch}:SCALE 5")    # 垂直比例 5V/div
        instr.write(f"CH{ch}:BANDWIDTH 20E+6")
        instr.write(f"TRIGGER:EDGE:SOURCE CH{ch}")
        instr.write(f"TRIGGER:EDGE:LEVEL 0.5")
    except Exception as e:
        log_print(f"Failed to initialize channel CH{ch}: {e}")

def get_channel_settings(instr, ch):
    prob = safe_query_str(instr, f"CH{ch}:PROBE?")
    scale = safe_query_str(instr, f"CH{ch}:SCALE?")
    return prob, scale

def measure(instr, ch, mtype):
    try:
        instr.write("MEASUrement:MEAS1:STATE OFF")
        time.sleep(0.1)
        instr.write(f"MEASUrement:MEAS1:TYPE {mtype}")
        instr.write(f"MEASUrement:MEAS1:SOURCE CH{ch}")
        instr.write("MEASUrement:MEAS1:STATE ON")
        time.sleep(1)   # 延长等待时间
        val = instr.query("MEASUrement:MEAS1:VALUE?")
        return float(val)
    except Exception as e:
        log_print(f"Failed to measure {mtype} on channel {ch}: {e}")
        return None

def measure_all(instr, ch):
    return {
        "Mean Voltage": measure(instr, ch, "MEAN"),
        "Frequency": measure(instr, ch, "FREQUENCY"),
        "Peak-to-Peak": measure(instr, ch, "PK2pk"),
        "RMS Voltage": measure(instr, ch, "RMS"),
        "Maximum Voltage": measure(instr, ch, "MAXIMUM"),
        "Minimum Voltage": measure(instr, ch, "MINIMUM")
    }

def screen_average(instr, ch):
    try:
        instr.write(f"DATA:SOURCE CH{ch}")
        instr.write("DATA:ENCdg RIBinary")  # Tektronix binary format
        instr.write("DATA:WIDTH 1")         # 1 byte per sample
        instr.write("DATA:START 1")
        num_points = int(instr.query("WFMPRE:NR_PT?"))
        instr.write(f"DATA:STOP {num_points}")

        ymult = float(instr.query("WFMPRE:YMULT?"))
        yzero = float(instr.query("WFMPRE:YZERO?"))
        yoff  = float(instr.query("WFMPRE:YOFF?"))

        raw = instr.query_binary_values("CURVE?", datatype='B', container=np.array)
        volts = (raw - yoff) * ymult + yzero
        return float(np.mean(volts))
    except Exception as e:
        log_print(f"[CH{ch}] Failed to get screen average: {e}")
        return None

log_file = None
def log_print(*args, **kwargs):
    print(*args, **kwargs)
    if log_file:
        print(*args, **kwargs, file=log_file)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <VISA_ADDRESS> <channel_list, e.g. 1,2>")
        sys.exit(1)

    visa_address = sys.argv[1]
    try:
        channels = [int(ch.strip()) for ch in sys.argv[2].split(',') if ch.strip() in ['1','2','3','4']]
        if not channels:
            raise ValueError
    except:
        print("Channel parameter format error. Use only 1,2,3,4 comma-separated.")
        sys.exit(1)

    rm = pyvisa.ResourceManager()

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

                screen_avg = screen_average(scope, ch)
                results[ch]["Screen Average"] = screen_avg

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
                scope.write("LOC")
            except:
                pass
            try:
                scope.close()
            except:
                pass
            rm.close()
