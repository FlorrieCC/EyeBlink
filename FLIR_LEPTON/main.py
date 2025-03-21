import pyb
import sensor, image, time, os

usb = pyb.USB_VCP()

def collect_data():
    # ===== 将你现有的数据采集代码放在这里 =====
    threshold_list = [(70, 100, -30, 40, 20, 100)]

    print("Resetting Lepton...")
    sensor.reset()
    sensor.set_color_palette(image.PALETTE_IRONBOW)

    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)
    sensor.skip_frames(time=5000)
    clock = time.clock()

    start_timestamp = time.ticks_ms()
    start_time_str = "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(
        *time.localtime()[:6], start_timestamp % 1000
    )

    main_folder = "LeptonData/{}".format(start_time_str)
    image_folder = "{}/image".format(main_folder)
    meta_folder = "{}/meta".format(main_folder)

    for folder in [main_folder, image_folder, meta_folder]:
        if folder not in os.listdir():
            try:
                os.mkdir(folder)
            except OSError as e:
                print("Failed to create folder {}: {}".format(folder, e))
                return

    metadata_filename = "{}/metadata.csv".format(meta_folder)
    with open(metadata_filename, "w") as meta_file:
        meta_file.write("Frame,Width,Height,Filename\n")

    frame_count = 0
    print("开始采集数据...")
    while True:
        clock.tick()
        img = sensor.snapshot()

        width, height = img.width(), img.height()
        raw_data = img.bytearray()

        frame_filename = "{}/frame_{:05d}.bin".format(meta_folder, frame_count)
        with open(frame_filename, "wb") as frame_file:
            frame_file.write(raw_data)

        with open(metadata_filename, "a") as meta_file:
            meta_file.write("{},{},{},{}\n".format(frame_count, width, height, frame_filename))

        for blob in img.find_blobs(
            threshold_list, pixels_threshold=200, area_threshold=200, merge=True
        ):
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())

        current_timestamp = time.ticks_ms()
        current_time_str = "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(
            *time.localtime()[:6], current_timestamp % 1000
        )
        image_name = "{}/{}.jpg".format(image_folder, current_time_str)

        try:
            img.save(image_name)
        except OSError as e:
            print("Failed to save image:", e)
            continue

        frame_count += 1

        # 每隔一段时间检查是否收到停止指令
        if usb.any():
            cmd = usb.readline().decode().strip()
            if cmd == 'stop':
                print("收到停止指令，停止采集...")
                break

        print("Saved Frame {} - FPS: {:.2f}".format(frame_count, clock.fps()))

while True:
    if usb.any():
        cmd = usb.readline().decode().strip()
        if cmd == 'start':
            usb.write("Data collection started\n")
            collect_data()
            usb.write("Data collection stopped\n")
        else:
            usb.write("Unknown command\n")
