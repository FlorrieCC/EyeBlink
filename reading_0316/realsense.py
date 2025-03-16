import pyrealsense2 as rs
import numpy as np
import time

def check_camera_connection():
    # 初始化 RealSense 管道
    pipeline = rs.pipeline()
    config = rs.config()
    
    # 配置彩色流
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    try:
        # 启动管道
        pipeline.start(config)
        print("相机连接成功！")
        
        # 添加延迟以确保相机初始化完成
        time.sleep(1)
        
        # 获取设备信息
        device = pipeline.get_active_profile().get_device()
        device_name = device.get_info(rs.camera_info.name)
        serial_number = device.get_info(rs.camera_info.serial_number)
        
        print(f"设备名称: {device_name}")
        print(f"序列号: {serial_number}")
        
        # 获取一帧彩色图像数据
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        
        if color_frame:
            print("成功获取彩色图像数据！")
            # 如果需要处理图像数据，可以将其转换为 NumPy 数组
            color_image = np.asanyarray(color_frame.get_data())
            print(f"彩色图像尺寸: {color_image.shape}")
        else:
            print("未获取到彩色图像数据，请检查相机配置。")
        
    except Exception as e:
        print(f"相机连接失败：{e}")
    finally:
        # 停止管道
        pipeline.stop()

if __name__ == "__main__":
    check_camera_connection()