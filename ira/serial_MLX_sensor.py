import serial
import time
import ast
import numpy as np
import cv2
import pickle
# import pyrealsense2 as rs


# Interpolating the subpage into a complete frame by using the bilinear interpolating method with window size at 3x3.
def SubpageInterpolating(subpage):
    shape = subpage.shape
    mat = subpage.copy()
    for i in range(shape[0]):
        for j in range(shape[1]):
            if mat[i,j] > 0.0:
                continue
            num = 0
            try:
                top = mat[i-1,j]
                num = num+1
            except:
                top = 0.0
            
            try:
                down = mat[i+1,j]
                num = num+1
            except:
                down = 0.0
            
            try:
                left = mat[i,j-1]
                num = num+1
            except:
                left = 0.0
            
            try:
                right = mat[i,j+1]
                num = num+1
            except:
                right = 0.0
            mat[i,j] = (top + down + left + right)/num
    return mat

def main(save_flag=False):
    # find the uart port with the following code:
    # import serial.tools.list_ports
    # ports = serial.tools.list_ports.comports()
    # for port in ports:
    #     print(port.device)
    storage_path = "./"
    if save_flag:
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        fps = 10
        out = cv2.VideoWriter(storage_path + "recording.mp4",fourcc,fps,(640*3, 480*3))
        
    # Open serial port (example with '/dev/tty.SLAB_USBtoUART' replace with your port and desired baud rate)
    # port = '/dev/tty.SLAB_USBtoUART'
    port = '/dev/ttyUSB0'
    baud_rate = 921600
    ser = serial.Serial(port, baud_rate, timeout=1)
    
    # set two whit images 
    color_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
    result_dict = {
        "temperature": [],
    }
    
    if not ser.is_open:
        print(f"Failed to open serial port {port}")
        return

    print(f"Reading data from {port} at {baud_rate} baud")
    # calculate the frame rate
    start_time = time.time()
    frame_count = 0

    while True:
        data = ser.readline().strip()
        if len(data) > 0:
            msg_str = str(data.decode('utf-8'))

        try:
            dict_data = ast.literal_eval(msg_str)
            Detected_temperature = np.array(dict_data["data"]).reshape((24,32))
            
            frame_count += 1
            if frame_count % 100 == 0:
                elapsed_time = time.time() - start_time
                print(f"Frame rate: {frame_count / elapsed_time:.2f} fps")
        except:
            print("Error")
            continue

        ira_interpolated = SubpageInterpolating(Detected_temperature)
        ira_interpolated = np.flip(ira_interpolated, 0)
        # ira_interpolated = np.flip(ira_interpolated, 1)
        ira_norm = ((ira_interpolated - np.min(ira_interpolated))/ (37 - np.min(ira_interpolated))) * 255
        ira_expand = np.repeat(ira_norm, 20, 0)
        ira_expand = np.repeat(ira_expand, 20, 1)
        ira_img_colored = cv2.applyColorMap((ira_expand).astype(np.uint8), cv2.COLORMAP_JET)
        
        cv2.namedWindow('All', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('All', ira_img_colored)
        key = cv2.waitKey(1) 
        if key == 27 or key == 113:
            break
    cv2.destroyAllWindows()
    if save_flag:
        out.release()   

    ser.close()
    return result_dict

if __name__ == "__main__":
    result_dict = main(save_flag=False)
    if len(result_dict["temperature"]) > 0:
        with open('data.pkl', 'wb') as f:
            pickle.dump(result_dict, f)