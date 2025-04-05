#!/bin/bash

cleanup() {
    echo "发送SIGINT信号，正在终止Python进程..."
    kill -SIGINT $PID1 $PID2

    # 稍长一点时间给程序优雅退出
    timeout=5
    while [ $timeout -gt 0 ]; do
        if ! ps -p $PID1 > /dev/null && ! ps -p $PID2 > /dev/null; then
            break
        fi
        sleep 1
        timeout=$((timeout-1))
    done

    # 如果5秒后仍未退出，强制终止
    if ps -p $PID1 > /dev/null; then
        echo "强制终止camera2mp4.py"
        kill -SIGKILL $PID1
    fi
    if ps -p $PID2 > /dev/null; then
        echo "强制终止controller.py"
        kill -SIGKILL $PID2
    fi

    echo "所有Python进程已终止。"
    exit
}

trap cleanup SIGINT SIGTERM

python3 /home/yvonne/Documents/EyeBlink/realsense/camera2mp4.py &
PID1=$!

python3 /home/yvonne/Documents/EyeBlink/FLIR_LEPTON/controller.py &
PID2=$!

echo "Python脚本已启动，进程ID分别为 $PID1 和 $PID2"

wait
