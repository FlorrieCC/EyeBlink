import os
import json
import struct
import re
from datetime import datetime
from tqdm import tqdm


# 温度范围
min_temp_in_celsius = 20.0
max_temp_in_celsius = 37.0

# 灰度值映射到温度
def map_g_to_temp(g):
    return ((g * (max_temp_in_celsius - min_temp_in_celsius)) / 255.0) + min_temp_in_celsius

# 加载 metadata.csv
def load_metadata(metadata_path):
    metadata = []
    with open(metadata_path, "r") as f:
        next(f)
        for line in f:
            frame_index, width, height, filename = line.strip().split(",")
            filename = os.path.basename(filename.strip())
            metadata.append((int(frame_index), int(width), int(height), filename))
    return metadata

# 获取 image 文件夹中的毫秒级时间戳
def get_sorted_timestamps(image_folder):
    timestamps = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(".jpg"):
            base = os.path.splitext(filename)[0]
            try:
                dt = datetime.strptime(base, "%Y%m%d%H%M%S%f")
                timestamps.append((filename, dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]))
            except ValueError:
                continue
    timestamps.sort()
    return [ts for _, ts in timestamps]

# 解析 .bin 文件为二维温度矩阵
def process_bin_file(file_path, width, height):
    with open(file_path, "rb") as f:
        raw_data = f.read()

    expected_len = width * height * 2
    if len(raw_data) != expected_len:
        raise ValueError(f"数据长度错误：{file_path}，期望 {expected_len} 字节，实际 {len(raw_data)}")

    # 解码为 uint16 像素值
    pixel_values = struct.unpack(f"<{width * height}H", raw_data)

    # 归一化到 0~255 灰度值
    min_val = min(pixel_values)
    max_val = max(pixel_values)
    norm_values = [
        int((val - min_val) * 255 / (max_val - min_val)) if max_val != min_val else 0
        for val in pixel_values
    ]

    # 映射到温度并转为二维矩阵
    temp_values = [round(map_g_to_temp(g), 2) for g in norm_values]
    matrix_2d = [temp_values[y * width : (y + 1) * width] for y in range(height)]
    return matrix_2d

# 主程序
def main(data_folder):
    metadata_file = os.path.join(data_folder, "metadata.csv")
    image_folder = os.path.join(os.path.dirname(data_folder), "image")

    if not os.path.exists(metadata_file):
        print("❌ 找不到 metadata.csv")
        return
    if not os.path.isdir(image_folder):
        print("❌ 找不到 image 文件夹")
        return

    metadata = load_metadata(metadata_file)
    timestamps = get_sorted_timestamps(image_folder)

    all_frames = []

    pbar = tqdm(
        metadata,
        desc="🚀 处理进度",
        ncols=90,
        bar_format="🔄 {desc} |{bar}| ✅ {percentage:3.0f}% ⏱️ {elapsed} ⏳{remaining} ⚡{rate_fmt} 📦 {n_fmt}/{total_fmt}"
    )

    for i, (frame_index, width, height, bin_filename) in enumerate(pbar):
        if i >= len(timestamps):
            tqdm.write(f"⚠️ 跳过帧 {frame_index}，没有对应时间戳")
            continue

        bin_path = os.path.join(data_folder, bin_filename)
        if not os.path.exists(bin_path):
            tqdm.write(f"⚠️ 未找到 bin 文件: {bin_path}")
            continue

        try:
            matrix_2d = process_bin_file(bin_path, width, height)
        except Exception as e:
            tqdm.write(f"❌ 错误帧 {frame_index}: {e}")
            continue

        frame_json = {
            "frame_id": frame_index,
            "timestamp": timestamps[i],
            "matrix": matrix_2d,
            "matrix_shape": [height, width]
        }

        all_frames.append(frame_json)
        pbar.set_postfix_str(f"Frame {frame_index}")




    # 写入 JSON 文件，确保 matrix 是一行，并且整体 JSON 合法
    output_path = os.path.join(data_folder, "all_frames.json")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i, frame in enumerate(all_frames):
            # 转为字符串
            json_str = json.dumps(frame, ensure_ascii=False, separators=(",", ":"))

            # 把 matrix 中的换行和空格移除 —— 只对 "matrix":[[...],[...],...] 部分
            json_str = re.sub(r'"matrix":\s*\[(.*?)\]', lambda m: '"matrix":[' + re.sub(r'\s+', '', m.group(1)) + ']', json_str, flags=re.DOTALL)

            # 写入
            f.write("  " + json_str)
            if i < len(all_frames) - 1:
                f.write(",\n")
            else:
                f.write("\n")
        f.write("]")

    print(f"\n🎉 所有数据已保存到：{output_path}")

# 启动入口
if __name__ == "__main__":
    folder = input("请输入包含二进制数据和 metadata.csv 的文件夹路径：").strip().strip("'")
    main(folder)
