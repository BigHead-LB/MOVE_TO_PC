# Function: Tektronix TDS 2024/2024B auto-detect & measure via USB or RS232
# Usage: python script.py <VISA_ADDRESS> <channel_list>
# Example:
#   python script.py USB0::0x0699::0x036A::C032490::INSTR 1,2
#   python script.py ASRL3::INSTR 1

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
        instr.write(f"SELECT:CH{ch} ON")
        instr.write(f"CH{ch}:PROBE 10")
        instr.write(f"CH{ch}:SCALE 0.5")
        instr.write(f"CH{ch}:BANDWIDTH 20E+6")
        instr.write(f"TRIGGER:EDGE:SOURCE CH{ch}")
        instr.write(f"TRIGGER:EDGE:LEVEL 0.5")
    except Exception as e:
        log_print(f"Failed to initialize CH{ch}: {e}")

def get_channel_settings(instr, ch):
    prob = safe_query_str(instr, f"CH{ch}:PROBE?")
    scale = safe_query_str(instr, f"CH{ch}:SCALE?")
    return prob, scale

def measure(instr, ch, mtype):
    try:
        instr.write(f"MEASUREMENT:IMMED:SOURCE CH{ch}")
        instr.write(f"MEASUREMENT:IMMED:TYPE {mtype}")
        time.sleep(0.3)
        return safe_query_float(instr, "MEASUREMENT:IMMED:VALUE?")
    except Exception as e:
        log_print(f"Failed to measure {mtype} on CH{ch}: {e}")
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

log_file = None

def log_print(*args, **kwargs):
    print(*args, **kwargs)
    if log_file:
        print(*args, **kwargs, file=log_file)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <VISA_ADDRESS> <channel_list>")
        sys.exit(1)

    visa_address = sys.argv[1]
    try:
        channels = [int(ch.strip()) for ch in sys.argv[2].split(',') if ch.strip() in ['1', '2', '3', '4']]
        if not channels:
            raise ValueError
    except:
        print("Channel format error. Only 1–4 allowed, comma-separated.")
        sys.exit(1)

    rm = pyvisa.ResourceManager()

    with open("measurement_log.txt", "w", encoding="utf-8") as log_file:
        try:
            scope = rm.open_resource(visa_address)
            scope.timeout = 5000

            # 如果是串口设备，则额外设置参数
            if visa_address.startswith("ASRL"):
                scope.baud_rate = 9600
                scope.data_bits = 8
                scope.stop_bits = pyvisa.constants.StopBits.one
                scope.parity = pyvisa.constants.Parity.none
                scope.flow_control = pyvisa.constants.FlowControl.none

            log_print(f"Connected to {visa_address}")
            idn = safe_query_str(scope, "*IDN?")
            log_print(f"IDN: {idn if idn else 'Unknown'}")

            results = {}

            for ch in channels:
                log_print(f"\nInitializing CH{ch} ...")
                initialize_channel(scope, ch)
                time.sleep(0.5)

                prob, scale = get_channel_settings(scope, ch)
                log_print(f"CH{ch} Probe: {prob if prob else 'N/A'}, Scale: {scale if scale else 'N/A'} V/div")

                log_print(f"Measuring CH{ch} ...")
                results[ch] = measure_all(scope, ch)

            log_print("\n======= Measurement Results =======")
            for ch, measurements in results.items():
                log_print(f"\nCH{ch}:")
                for name, val in measurements.items():
                    if val is not None:
                        unit = "Hz" if "Frequency" in name else "V"
                        log_print(f"{name}: {val:.3f} {unit}")
                    else:
                        log_print(f"{name}: Error")

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
