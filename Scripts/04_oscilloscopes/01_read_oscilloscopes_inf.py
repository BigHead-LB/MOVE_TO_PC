import pyvisa

rm = pyvisa.ResourceManager()
resources = rm.list_resources()

print("可用 VISA 设备列表：")
for res in resources:
    print(res)

# 测试每个设备的 ID
for res in resources:
    try:
        dev = rm.open_resource(res)
        idn = dev.query("*IDN?")
        print(f"{res} 响应: {idn.strip()}")
    except Exception as e:
        print(f"{res} 无法访问: {e}")
