import pyb
import sensor, image, time, os

usb = pyb.USB_VCP()

def collect_data():

    log_str = "Resetting Lepton..."
    usb.write(b'\xAB\xCD')
    usb.write(log_str.encode())

    sensor.reset()
    sensor.set_color_palette(image.PALETTE_IRONBOW)

    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)  # 分辨率为 160x120
    sensor.skip_frames(time=2000)
    clock = time.clock()

    # 生成一个基于当前时间的主目录
    start_timestamp = time.ticks_ms()
    start_time_str = "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(
        *time.localtime()[:6], start_timestamp % 1000
    )

    # 创建三个目录（这里只保留 image_folder 是为了保留你的结构，但暂时不存图）
    main_folder = "LeptonData/{}".format(start_time_str)
    image_folder = "{}/image".format(main_folder)  # 保留但不使用
    meta_folder = "{}/meta".format(main_folder)

    for folder in [main_folder, image_folder, meta_folder]:
        if folder not in os.listdir():
            try:
                os.mkdir(folder)
            except OSError as e:
                log_str = "Failed to create folder {}: {}".format(folder, e)
                usb.write(b'\xAB\xCD')
                usb.write(log_str.encode())

                return

    # ======= metadata.csv：用于记录每帧的位置、尺寸、偏移量等信息 =======
    metadata_filename = "{}/metadata.csv".format(meta_folder)
    meta_file = open(metadata_filename, "w")
    meta_file.write("Frame,Width,Height,Offset,Length\n")  # 添加了偏移量和长度列

    # ======= data_stream.bin：将所有帧合并写入这个大文件 =======
    datastream_filename = "{}/data_stream.bin".format(meta_folder)
    data_file = open(datastream_filename, "ab")

    frame_count = 0

    log_str = "开始采集数据..."
    usb.write(b'\xAB\xCD')
    usb.write(log_str.encode())

    while True:
        clock.tick()
        img = sensor.snapshot()

        #通过串口发送img
        send_img(img)

        width, height = img.width(), img.height()
        raw_data = img.bytearray()
        length = len(raw_data)
        offset = data_file.tell()  # 当前写入的位置

        # 写入图像原始数据到大 bin 文件中
        data_file.write(raw_data)

        # 写入每帧的元数据
        meta_file.write("{},{},{},{},{}\n".format(frame_count, width, height, offset, length))

        # ======= 如果想恢复“每帧保存成单独 bin 文件”，改回这里：=======
        # frame_filename = "{}/frame_{:05d}.bin".format(meta_folder, frame_count)
        # with open(frame_filename, "wb") as frame_file:
        #     frame_file.write(raw_data)
        # meta_file.write("{},{},{},{}\n".format(frame_count, width, height, frame_filename))


        # ======= 保存图像（.jpg）=======
        # current_timestamp = time.ticks_ms()
        # current_time_str = "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(
        #     *time.localtime()[:6], current_timestamp % 1000
        # )
        # image_name = "{}/{}.jpg".format(image_folder, current_time_str)
        # try:
        #     if frame_count % 5 == 0: 
        #         img.save(image_name)
        # except OSError as e:
        #     print("Failed to save image:", e)
        #     continue

        frame_count += 1

        # 检查串口是否收到 stop 指令
        if usb.any():
            cmd = usb.readline().decode().strip()
            if cmd == 'stop':
                meta_file.close()
                data_file.close()

                break

        log_str = "Saved Frame {} - FPS: {:.2f}\n".format(frame_count, clock.fps())
        usb.write(b'\xAB\xCD')
        usb.write(log_str.encode())



def send_img(img):
    img_bytes = img.compress(quality=90)
    size = len(img_bytes)

    usb.write(b'\xAA\x55')  # 帧头：两个字节标识图像开始
    usb.write(size.to_bytes(4, 'big'))  # 图像长度
    usb.write(img_bytes)  # 图像内容



# ======= 主循环：等待串口命令控制采集 =======
while True:
    if usb.any():
        cmd = usb.readline().decode().strip()
        if cmd == 'start':
            while usb.any():
                usb.read(usb.any())  # 丢弃旧数据

            usb.write(b'\xAB\xCD')
            usb.write("Data collection started\n")

            collect_data()

            usb.write(b'\xAB\xCD')
            usb.write("Data collection stopped\n")
        else:
            usb.write(b'\xAB\xCD')
            usb.write("Unknown command\n")
