import pyrealsense2 as rs
import numpy as np
import cv2
import time
from datetime import datetime

# 设置参数
SAVE_INTERVAL = 2 * 60  # 每隔 2 分钟(120秒)保存一个文件
FRAME_WIDTH, FRAME_HEIGHT = 640, 480
FPS = 15

# 1. 创建 RealSense pipeline 和 config
pipeline = rs.pipeline()
config = rs.config()
# 启用深度和彩色流，可根据需求修改分辨率和帧率
config.enable_stream(rs.stream.depth, FRAME_WIDTH, FRAME_HEIGHT, rs.format.z16, FPS)
config.enable_stream(rs.stream.color, FRAME_WIDTH, FRAME_HEIGHT, rs.format.bgr8, FPS)

# 2. 启动流水线
pipeline.start(config)

# 3. 初始化保存相关变量
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4编码格式
start_time = time.time()
file_index = 1

def new_filename():
    """
    生成带时间戳或编号的MP4文件名。
    可自行选择想要的命名方式，这里用当前时间+递增编号。
    """
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"output_{now_str}_{file_index}.mp4"

# 创建第一个输出文件
current_filename = new_filename()
out = cv2.VideoWriter(current_filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

try:
    while True:
        # 获取 RealSense 帧
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        # 转成 Numpy
        color_image = np.asanyarray(color_frame.get_data())

        # 写入当前 MP4
        out.write(color_image)

        # 在窗口显示（可选）
        cv2.imshow("RealSense", color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 判断是否超时，需要切换文件
        elapsed = time.time() - start_time
        if elapsed >= SAVE_INTERVAL:
            # 关闭旧的
            out.release()
            file_index += 1
            # 新的文件名
            current_filename = new_filename()
            out = cv2.VideoWriter(current_filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
            # 重置计时
            start_time = time.time()

except Exception as e:
    print("Error:", e)
finally:
    # 收尾
    out.release()
    pipeline.stop()
    cv2.destroyAllWindows()
