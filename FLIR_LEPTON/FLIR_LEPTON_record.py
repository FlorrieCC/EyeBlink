import sensor
import image
import time
import os

# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
threshold_list = [(70, 100, -30, 40, 20, 100)]

# 设置相机
print("Resetting Lepton...")
sensor.reset()
print(
    "Lepton Res (%dx%d)"
    % (
        sensor.ioctl(sensor.IOCTL_LEPTON_GET_WIDTH),
        sensor.ioctl(sensor.IOCTL_LEPTON_GET_HEIGHT),
    )
)
print(
    "Radiometry Available: "
    + ("Yes" if sensor.ioctl(sensor.IOCTL_LEPTON_GET_RADIOMETRY) else "No")
)
# Make the color palette cool
sensor.set_color_palette(image.PALETTE_IRONBOW)

# sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=5000)
clock = time.clock()

# 获取当前时间戳
start_timestamp = time.ticks_ms()
start_time_str = "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(
    time.localtime()[0], time.localtime()[1], time.localtime()[2],
    time.localtime()[3], time.localtime()[4], time.localtime()[5],
    start_timestamp % 1000
)

# 设置主文件夹路径
main_folder = "LeptonData/{}".format(start_time_str)
image_folder = "{}/image".format(main_folder)
meta_folder = "{}/meta".format(main_folder)

# 创建主文件夹和子文件夹
for folder in [main_folder, image_folder, meta_folder]:
    if folder not in os.listdir():
        try:
            os.mkdir(folder)
        except OSError as e:
            print("Failed to create folder {}: {}".format(folder, e))
            raise

# 创建元数据文件 (记录每一帧的信息)
metadata_filename = "{}/metadata.csv".format(meta_folder)
with open(metadata_filename, "w") as meta_file:
    meta_file.write("Frame,Width,Height,Filename\n")  # 表头

# 录制帧并保存
frame_count = 0
try:
    while True:
        clock.tick()
        img = sensor.snapshot()  # 拍摄一帧

        # 获取图像宽度、高度和原始数据
        width = img.width()
        height = img.height()
        raw_data = img.bytearray()
        
        # 保存原始数据到二进制文件
        frame_filename = "{}/frame_{:05d}.bin".format(meta_folder, frame_count)
        with open(frame_filename, "wb") as frame_file:
            frame_file.write(raw_data)
        
        # 记录当前帧的信息到元数据文件中
        with open(metadata_filename, "a") as meta_file:
            meta_file.write("{},{},{},{}\n".format(frame_count, width, height, frame_filename))
            
            

        # 查找色块
        for blob in img.find_blobs(
            threshold_list, pixels_threshold=200, area_threshold=200, merge=True
        ):
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
        
        # 获取当前时间作为图片名称
        current_timestamp = time.ticks_ms()
        current_time_str = "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(
            time.localtime()[0],  # 年
            time.localtime()[1],  # 月
            time.localtime()[2],  # 日
            time.localtime()[3],  # 时
            time.localtime()[4],  # 分
            time.localtime()[5],  # 秒
            current_timestamp % 1000  # 毫秒
        )
        image_name = "{}/{}.jpg".format(image_folder, current_time_str)
        
        # 保存图像
        try:
            img.save(image_name)
        except OSError as e:
            print("Failed to save image:", e)
            continue  # 跳过当前帧，继续下一帧
        
        frame_count += 1
        print("Saved Frame {} - FPS: {:.2f}".format(frame_count, clock.fps()))
except KeyboardInterrupt:
    print("Recording stopped by user.")
