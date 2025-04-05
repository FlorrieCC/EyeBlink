import os
import json
import struct
import re
from datetime import datetime
from tqdm import tqdm

# Temperature range
min_temp_in_celsius = 20.0
max_temp_in_celsius = 37.0

# Map grayscale to temperature
def map_g_to_temp(g):
    return ((g * (max_temp_in_celsius - min_temp_in_celsius)) / 255.0) + min_temp_in_celsius

# Load metadata.csv
def load_metadata(metadata_path):
    metadata = []
    with open(metadata_path, "r") as f:
        next(f)
        for line in f:
            frame_index, width, height, filename = line.strip().split(",")
            filename = os.path.basename(filename.strip())
            metadata.append((int(frame_index), int(width), int(height), filename))
    return metadata

# Extract millisecond-level timestamps from the image folder
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

# Parse .bin file into 2D temperature matrix
def process_bin_file(file_path, width, height):
    with open(file_path, "rb") as f:
        raw_data = f.read()

    expected_len = width * height * 2
    if len(raw_data) != expected_len:
        raise ValueError(f"Incorrect data length: {file_path}, expected {expected_len} bytes, got {len(raw_data)}")

    # Decode to uint16 pixel values
    pixel_values = struct.unpack(f"<{width * height}H", raw_data)

    # Normalize to 0–255 grayscale
    min_val = min(pixel_values)
    max_val = max(pixel_values)
    norm_values = [
        int((val - min_val) * 255 / (max_val - min_val)) if max_val != min_val else 0
        for val in pixel_values
    ]

    # Map to temperature and reshape into 2D matrix
    temp_values = [round(map_g_to_temp(g), 2) for g in norm_values]
    matrix_2d = [temp_values[y * width : (y + 1) * width] for y in range(height)]
    return matrix_2d

# Main function
def main(data_folder):
    metadata_file = os.path.join(data_folder, "metadata.csv")
    image_folder = os.path.join(os.path.dirname(data_folder), "image")

    if not os.path.exists(metadata_file):
        print("❌ metadata.csv not found")
        return
    if not os.path.isdir(image_folder):
        print("❌ image folder not found")
        return

    metadata = load_metadata(metadata_file)
    timestamps = get_sorted_timestamps(image_folder)

    all_frames = []

    pbar = tqdm(
        metadata,
        desc="🚀 Processing",
        ncols=90,
        bar_format="🔄 {desc} |{bar}| ✅ {percentage:3.0f}% ⏱️ {elapsed} ⏳{remaining} ⚡{rate_fmt} 📦 {n_fmt}/{total_fmt}"
    )

    for i, (frame_index, width, height, bin_filename) in enumerate(pbar):
        if i >= len(timestamps):
            tqdm.write(f"⚠️ Skipping frame {frame_index}, no matching timestamp")
            continue

        bin_path = os.path.join(data_folder, bin_filename)
        if not os.path.exists(bin_path):
            tqdm.write(f"⚠️ Binary file not found: {bin_path}")
            continue

        try:
            matrix_2d = process_bin_file(bin_path, width, height)
        except Exception as e:
            tqdm.write(f"❌ Error in frame {frame_index}: {e}")
            continue

        frame_json = {
            "frame_id": frame_index,
            "timestamp": timestamps[i],
            "matrix": matrix_2d,
            "matrix_shape": [height, width]
        }

        all_frames.append(frame_json)
        pbar.set_postfix_str(f"Frame {frame_index}")

    # Save to JSON, flatten matrix into one line and ensure valid structure
    output_path = os.path.join(data_folder, "all_frames.json")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i, frame in enumerate(all_frames):
            json_str = json.dumps(frame, ensure_ascii=False, separators=(",", ":"))
            json_str = re.sub(
                r'"matrix":\s*\[(.*?)\]',
                lambda m: '"matrix":[' + re.sub(r'\s+', '', m.group(1)) + ']',
                json_str,
                flags=re.DOTALL
            )
            f.write("  " + json_str)
            if i < len(all_frames) - 1:
                f.write(",\n")
            else:
                f.write("\n")
        f.write("]")

    print(f"\n🎉 All data saved to: {output_path}")

# Entry point
if __name__ == "__main__":
    folder = input("Enter the folder path containing binary data and metadata.csv: ").strip().strip("'")
    main(folder)
