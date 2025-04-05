import serial
import time
import cv2
import numpy as np
import signal

running = True

def signal_handler(sig, frame):
    global running
    print("Received SIGINT, cleaning up...")

    send_command("stop")
    running = False  # Tell main loop to exit

    # Wait for trailing log
    timeout = 2
    start = time.time()
    while time.time() - start < timeout:
        try:
            read_frame_and_log()
        except TimeoutError:
            continue


# Register SIGINT handler
signal.signal(signal.SIGINT, signal_handler)

# Replace with your own serial port
PORT = '/dev/ttyACM0'
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=1)

def send_command(cmd):
    ser.write((cmd + '\n').encode())
    print(f"Command sent: {cmd}")

def read_exactly(n):
    """Read exactly n bytes (wait until full)"""
    data = bytearray()
    while len(data) < n:
        chunk = ser.read(n - len(data))
        if not chunk:
            raise RuntimeError("Serial read timeout or interrupted")
        data.extend(chunk)
    return data

def read_frame_and_log(timeout = 3):
    """Read one image frame and the following log line"""
    # 1. Look for header 0xAA55
    start_time = time.time()

    if time.time() - start_time > timeout:
        raise TimeoutError("Timeout while waiting for header")

    header = ser.read(2)
    if not header:
        return  # No data, skip this round
    if header == b'\xAA\x55':
        # Image frame
        # 2. Read 4-byte image length
        size_bytes = read_exactly(4)
        img_size = int.from_bytes(size_bytes, 'big')

        # 3. Read image content
        img_data = read_exactly(img_size)

        # 4. Decode image
        np_img = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img is not None:
            cv2.imshow("OpenMV Live Feed", img)
            cv2.waitKey(1)
            
    elif header == b'\xAB\xCD':
        # 5. Log frame (read until newline)
        log_line = ser.readline().decode(errors='ignore').strip()
        if log_line:
            print(f"[LOG] {log_line}")
    else:
        print(f"[WARN] Unknown header: {header}")
        return



if __name__ == "__main__":
    send_command("start")
    print("Board started, collecting data...")
    try:
        while running:
            read_frame_and_log()
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        ser.close()
        cv2.destroyAllWindows()
        print("Serial connection closed.")
