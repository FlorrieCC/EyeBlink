from seekcamera import (
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCamera,
    SeekCameraIOType,
)

# Event callback function
def on_event(camera, event_type, event_status, _user_data):
    if event_type == SeekCameraManagerEvent.CONNECT:
        print(f"Camera connected: {camera.chipid}")
    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        print(f"Camera disconnected: {camera.chipid}")
    elif event_type == SeekCameraManagerEvent.ERROR:
        print(f"Camera error: {event_status}")
    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        print(f"Camera ready to pair: {camera.chipid}")

def main():
    # Create a camera manager
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Print the waiting message before registering the event callback
        print("Waiting for camera connection...")

        # Register event callback
        manager.register_event_callback(on_event)

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Program exited")

if __name__ == "__main__":
    main()