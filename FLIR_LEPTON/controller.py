import serial
import time
import cv2
import numpy as np

# 修改为你对应的串口号
PORT = '/dev/ttyACM0'
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=1)

def send_command(cmd):
    ser.write((cmd + '\n').encode())
    print(f"已发送指令: {cmd}")

def read_exactly(n):
    """读取刚好 n 字节的数据（如果不够就继续读）"""
    data = bytearray()
    while len(data) < n:
        chunk = ser.read(n - len(data))
        if not chunk:
            raise RuntimeError("串口读取超时或中断")
        data.extend(chunk)
    return data

def read_frame_and_log(timeout = 3):
    """读取一帧图像数据并读取后续一条日志"""
    # 1. 寻找帧头 0xAA55
    start_time = time.time()

    if time.time() - start_time > timeout:
        raise TimeoutError("等待帧头超时")

    header = ser.read(2)
    if not header:
        return  # 没有数据，跳过这一轮
    if header == b'\xAA\x55':
        # 图像帧处理
        # 2. 读取4字节图像长度
        size_bytes = read_exactly(4)
        img_size = int.from_bytes(size_bytes, 'big')

        # 3. 读取图像内容
        img_data = read_exactly(img_size)

        # 4. 解码图像
        np_img = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img is not None:
            cv2.imshow("OpenMV Live Feed", img)
            cv2.waitKey(1)
            
    elif header == b'\xAB\xCD':
        # 5. 日志帧处理（读到 \n 为止）
        log_line = ser.readline().decode(errors='ignore').strip()
        if log_line:
            print(f"[LOG] {log_line}")
    else:
        print(f"[WARN] 未知帧头: {header}")
        return



if __name__ == "__main__":
    send_command("start")
    print("开发板已启动，正在采集数据...")
    try:
        while True:
            read_frame_and_log()
    except KeyboardInterrupt:
        send_command("stop")

        # 等待一段时间接收“尾部日志”
        timeout = 2  
        start = time.time()
        while time.time() - start < timeout:
            try:
                read_frame_and_log()
            except TimeoutError:
                # 超时跳出，不需要频繁报错
                continue

        ser.close()
        cv2.destroyAllWindows()
        print("串口连接已关闭。")

