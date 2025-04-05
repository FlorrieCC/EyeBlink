#!/bin/bash

# ./run_script.sh

# Define a function to terminate background Python processes
cleanup() {
    echo "Terminating all Python processes..."
    pkill -f "/home/yvonne/Documents/EyeBlink/realsense/camera2mp4.py"
    pkill -f "/home/yvonne/Documents/EyeBlink/seek/reading.py"
    pkill -f "/home/yvonne/Documents/EyeBlink/FLIR_LEPTON/controller.py"
    exit
}

# Catch exit signals (e.g., Ctrl+C) and call the cleanup function
trap cleanup SIGINT SIGTERM

# Run three Python scripts simultaneously
python3 /home/yvonne/Documents/EyeBlink/realsense/camera2mp4.py &
PID1=$!

python3 /home/yvonne/Documents/EyeBlink/seek/reading.py &
PID2=$!

python3 /home/yvonne/Documents/EyeBlink/FLIR_LEPTON/controller.py &
PID3=$!

echo "Python scripts started with process IDs: $PID1, $PID2, and $PID3"

# Wait for all background processes to complete
wait

echo "All scripts have finished execution"
