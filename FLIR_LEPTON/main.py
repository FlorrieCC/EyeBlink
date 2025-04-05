import pyb
import sensor, image, time, os

usb = pyb.USB_VCP()

def send_img(img):
    img_bytes = img.compress(quality=90)
    size = len(img_bytes)

    usb.write(b'\xAA\x55')  # Frame header: two bytes indicating the start of an image
    usb.write(size.to_bytes(4, 'big'))  # Image length
    usb.write(img_bytes)  # Image content

def collect_data():

    log_str = "Resetting Lepton..."
    usb.write(b'\xAB\xCD')
    usb.write(log_str.encode())

    sensor.reset()
    sensor.set_color_palette(image.PALETTE_IRONBOW)

    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)  # Resolution: 160x120
    sensor.skip_frames(time=2000)
    clock = time.clock()

    # Generate a main folder name based on the current time
    start_timestamp = time.ticks_ms()
    start_time_str = "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(
        *time.localtime()[:6], start_timestamp % 1000
    )

    # Create three directories (only image_folder will be used to store images)
    main_folder = "LeptonData/0405_{}".format(start_time_str)
    image_folder = "{}/image".format(main_folder)  
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

    # ======= metadata.csv: records info like frame index, resolution, file name =======
    metadata_filename = "{}/metadata.csv".format(meta_folder)
    meta_file = open(metadata_filename, "w")
    meta_file.write("Frame,Width,Height,Filename\n")

    frame_count = 0

    log_str = "Starting data collection..."
    usb.write(b'\xAB\xCD')
    usb.write(log_str.encode())

    while True:
        clock.tick()
        img = sensor.snapshot()

        width, height = img.width(), img.height()
        raw_data = img.bytearray()

        # ======= Save each frame as an individual .bin file (raw image data) =======
        frame_filename = "{}/frame_{:05d}.bin".format(meta_folder, frame_count)
        with open(frame_filename, "wb") as frame_file:
            frame_file.write(raw_data)
        meta_file.write("{},{},{},{}\n".format(frame_count, width, height, frame_filename))

        # ======= Save image as .jpg file =======
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

        # Send image via serial port
        send_img(img)

        frame_count += 1

        # Check for 'stop' command via serial
        if usb.any():
            cmd = usb.readline().decode().strip()
            if cmd == 'stop':
                meta_file.close()
                break

        log_str = "Saved Frame {} - FPS: {:.2f}\n".format(frame_count, clock.fps())
        usb.write(b'\xAB\xCD')
        usb.write(log_str.encode())

# ======= Main loop: wait for serial command to start collection =======
while True:
    if usb.any():
        cmd = usb.readline().decode().strip()
        if cmd == 'start':
            while usb.any():
                usb.read(usb.any())  # Discard old data

            usb.write(b'\xAB\xCD')
            usb.write("Data collection started\n")

            collect_data()

            usb.write(b'\xAB\xCD')
            usb.write("Data collection stopped\n")
        else:
            usb.write(b'\xAB\xCD')
            usb.write("Unknown command\n")
