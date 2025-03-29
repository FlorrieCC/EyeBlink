#!/bin/bash

# ./run_script.sh

# 定义一个函数，用于终止后台运行的Python进程
cleanup() {
    echo "正在终止所有Python进程..."
    pkill -f "/home/yvonne/Documents/EyeBlink/realsense/camera2mp4.py"
    pkill -f "/home/yvonne/Documents/EyeBlink/FLIR_LEPTON/controller.py"
    exit
}

# 捕获退出信号（如Ctrl+C），并调用cleanup函数
trap cleanup SIGINT SIGTERM

# 同时运行三个Python脚本
python3 /home/yvonne/Documents/EyeBlink/realsense/camera2mp4.py &
PID1=$!

python3 /home/yvonne/Documents/EyeBlink/FLIR_LEPTON/controller.py &
PID2=$!

echo "Python脚本已启动，进程ID分别为 $PID1 和 $PID2"

# 等待所有后台进程完成
wait

echo "所有脚本执行完毕"
