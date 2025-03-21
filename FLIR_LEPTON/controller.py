import serial
import time
import keyboard

# 根据实际情况修改串口端口名
port = "COM4"  # Windows如"COM3"，Linux/Mac如"/dev/ttyACM0"
baudrate = 115200

# 初始化串口连接（只打开一次串口）
ser = serial.Serial(port, baudrate, timeout=1)

def send_command(cmd):
    ser.write((cmd + '\n').encode())
    response = ser.readline().decode().strip()
    print("OpenMV回复:", response)

if __name__ == "__main__":
    send_command("start")
    print("开发板已启动，正在采集数据...（按'q'键停止）")

    try:
        while True:
            if keyboard.is_pressed('q'):
                print("检测到'q'键，准备停止...")
                break
            time.sleep(0.05)  # 避免CPU占用率过高

    except KeyboardInterrupt:
        print("手动中断")

    send_command("stop")
    print("发送停止指令，开发板将停止采集...")

    # 正确关闭串口连接
    ser.close()
    print("串口连接已关闭。")