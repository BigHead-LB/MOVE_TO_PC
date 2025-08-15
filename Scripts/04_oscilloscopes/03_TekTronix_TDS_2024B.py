import pyvisa

rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
print(instruments)  # 查看连接了哪些仪器

scope = rm.open_resource('USB0::0x0699::0x036A::C032490::INSTR')  # 替换成实际地址
print(scope.query('*IDN?'))  # 读取设备识别信息
