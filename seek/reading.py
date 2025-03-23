import time
import numpy as np
import cv2
from queue import Queue
from threading import Lock
from seekcamera import (
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCamera,
    SeekCameraIOType,
    SeekCameraFrameFormat,
    SeekFrame,
)
import os 

# Overlay temperature information on the image
def put_temp(image, temp1, temp2, sensor_name):
    cv2.putText(image, f"{sensor_name}: {temp1:.1f}~{temp2:.1f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(image, f"{sensor_name}: {temp1:.1f}~{temp2:.1f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

# Circular buffer
class ImageBuffer:
    def __init__(self, buffer_size=5):
        self.buffer_size = buffer_size
        self.read = 0
        self.write = 0
        self.buffer = [None] * buffer_size

    def add(self, image):
        self.buffer[self.write] = image
        self.write = (self.write + 1) % self.buffer_size

    def get(self):
        image = self.buffer[self.read]
        self.read = (self.read + 1) % self.buffer_size
        return image

# Frame available callback function
def on_frame(camera, camera_frame, renderer):
    frame_data = None

    if renderer.data_format == "THERMOGRAPHY_FLOAT":
        frame = camera_frame.thermography_float
        if frame is None:
            print("Invalid frame data!")
            return

        frame_data = frame.data
        # frame_data = np.flip(frame_data, 0)  # Vertical flip
        frame_data = np.flip(frame_data, 1)  # Horizontal flip
        frame_data = frame_data.astype(np.uint8)  # Convert to uint8 type
        frame_data = cv2.normalize(frame_data, None, 0, 255, cv2.NORM_MINMAX)  # Normalize
        frame_data = cv2.resize(frame_data, (320, 240), interpolation=cv2.INTER_NEAREST)  # Resize
        frame_data = cv2.applyColorMap(frame_data, cv2.COLORMAP_JET)  # Color mapping

        # Get temperature range and overlay on the image
        seek_min = np.min(frame.data)
        seek_max = np.max(frame.data)
        put_temp(frame_data, seek_min, seek_max, "seek")

        # If recording video, also write to CSV file
        if renderer.recording:
            np.savetxt(renderer.csv_file, frame.data, fmt="%.1f", delimiter=",")

    elif renderer.data_format == "COLOR_ARGB8888":
        frame = camera_frame.color_argb8888
        if frame is None:
            print("Invalid frame data!")
            return

        frame_data = frame.data
        frame_data = np.flip(frame_data, 0)  # Vertical flip
        frame_data = np.flip(frame_data, 1)  # Horizontal flip
        frame_data = cv2.resize(frame_data, (320, 240), interpolation=cv2.INTER_NEAREST)  # Resize

    # Put the processed frame data into the buffer
    if frame_data is not None:
        renderer.frame_buffer.add(frame_data)

    # If recording video, add frame data to the video writer
    if renderer.recording:
        renderer.video_writer.write(frame_data)

    # Mark frame as processed
    renderer.frame_processed = True

# Event callback function
def on_event(camera, event_type, event_status, renderer):
    if event_type == SeekCameraManagerEvent.CONNECT:
        print(f"Camera connected: {camera.chipid}")
        # Register frame callback function
        camera.register_frame_available_callback(on_frame, renderer)
        # Start capture session
        if renderer.data_format == "THERMOGRAPHY_FLOAT":
            camera.capture_session_start(SeekCameraFrameFormat.THERMOGRAPHY_FLOAT)
        elif renderer.data_format == "COLOR_ARGB8888":
            camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)
    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        print(f"Camera disconnected: {camera.chipid}")
    elif event_type == SeekCameraManagerEvent.ERROR:
        print(f"Camera error: {event_status}")
    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        print(f"Camera ready to pair: {camera.chipid}")

def main():
    # Create camera manager
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Create renderer object
        class Renderer:
            def __init__(self, data_format="THERMOGRAPHY_FLOAT"):
                self.data_format = data_format
                self.frame_processed = False
                self.frame_buffer = ImageBuffer(buffer_size=5)  # Buffer size is 5
                self.frame_buffer_lock = Lock()
                self.recording = False
                self.video_writer = None
                self.csv_file = None

        # Select data format
        # "THERMOGRAPHY_FLOAT" or "COLOR_ARGB8888"
        data_format = "THERMOGRAPHY_FLOAT"

        renderer = Renderer(data_format=data_format)

        # Register event callback
        manager.register_event_callback(on_event, renderer)

        # Print instructions
        print("Waiting for camera connection...")
        print("\nUser controls:")
        print("r:    Start/stop recording video and saving CSV file")
        print("q:    Quit the program")

        # Keep the program running, waiting for camera connection and processing frame data
        try:
            while True:
                # Check if there is a new frame
                if renderer.frame_processed:
                    renderer.frame_processed = False

                # Get the latest frame data from the buffer and display it
                with renderer.frame_buffer_lock:
                    frame_data = renderer.frame_buffer.get()
                    if frame_data is not None:
                        cv2.imshow("Seek Thermal Camera", frame_data)

                # Detect key input
                key = cv2.waitKey(1)
                if key == ord("q"):  # Press 'q' to quit
                    break
                elif key == ord("r"):  # Press 'r' to start/stop recording video and saving CSV file

                    SAVE_DIR = "seek_data"  # 保存路径
                    if not os.path.exists(SAVE_DIR):
                        os.makedirs(SAVE_DIR)
                    if not renderer.recording:
                        # Start recording video and saving CSV file
                        renderer.recording = True
                        video_name = os.path.join(SAVE_DIR, "thermography_video.mp4")  # 添加保存路径
                        csv_name = os.path.join(SAVE_DIR, "thermography_data.csv")
                        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Change to MP4 encoder
                        renderer.video_writer = cv2.VideoWriter(video_name, fourcc, 10.0, (320, 240))
                        renderer.csv_file = open(csv_name, "w")
                        print(f"Started recording video and saving CSV file: {video_name} and {csv_name}")
                    else:
                        # Stop recording video and saving CSV file
                        renderer.recording = False
                        renderer.video_writer.release()
                        renderer.csv_file.close()
                        print("Video recording and CSV file saving completed!")

                # Sleep briefly to avoid excessive CPU usage
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Program exited")

        # Close OpenCV windows
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()