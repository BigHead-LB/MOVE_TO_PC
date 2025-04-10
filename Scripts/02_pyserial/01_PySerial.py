#示波器通讯测试

import serial
import time

# 串口配置
port = "COM6"  # 修改为你的串口号，例如 COM3 或 /dev/ttyUSB0
baudrate = 9600  # 波特率
timeout = 1  # 超时时间（秒）

try:
    # 打开串口
    ser = serial.Serial(port, baudrate, timeout=timeout)
    print(f"串口 {port} 已打开，波特率 {baudrate}")

    # 发送数据
    def send_data(data):
        if ser.is_open:
            ser.write(data.encode('utf-8'))  # 将字符串转为字节发送
            print(f"发送: {data}")
        else:
            print("串口未打开，无法发送数据")

    # 接收数据
    def receive_data():
        if ser.is_open:
            received = ser.readline().decode('utf-8').strip()  # 接收并解码
            print(f"接收到: {received}")
            return received
        else:
            print("串口未打开，无法接收数据")
            return None

    #     send_data(f"SYSTem:AUTO")  # 发送数据
    #     time.sleep(1)  # 延迟 1 秒
    #     receive_data()  # 接收数据
    send_data(f"*RST\n")
    time.sleep(1)  # 延迟 1 秒
    receive_data()  # 接收数据


#设置方大Scale
#:CHANnel1:SCALe?  read
#:CHANnel<n>:SCALe <range>
#:CHANnel1:SCALe 5

#设置探头衰减比
#:CHAN1:PROB?
#:CHAN1:PROB 10

#退出示波器的控制
# *RST\n

except serial.SerialException as e:
    print(f"串口错误: {e}")

finally:
    # 关闭串口
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("串口已关闭")
#20250410
