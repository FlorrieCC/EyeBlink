import os
import csv

# 设置温度范围
min_temp_in_celsius = 20.0
max_temp_in_celsius = 35.0

# 将灰度值映射到温度
def map_g_to_temp(g):
    return ((g * (max_temp_in_celsius - min_temp_in_celsius)) / 255.0) + min_temp_in_celsius

# 读取元数据文件
def load_metadata(metadata_path):
    metadata = []
    with open(metadata_path, "r") as f:
        reader = csv.reader(f)
        next(reader)  # 跳过标题行
        for row in reader:
            frame_index = int(row[0])
            width = int(row[1])
            height = int(row[2])
            filename = os.path.basename(row[3])  # 确保只提取文件名
            metadata.append((frame_index, width, height, filename))
    return metadata

# 解析二进制文件并转换为温度数据
def process_bin_file(file_path, width, height):
    with open(file_path, "rb") as f:
        raw_data = f.read()
    
    # 将原始数据转换为温度数据
    temp_data = [map_g_to_temp(b) for b in raw_data]

    # 将温度数据转化为二维数组 (方便保存为 CSV)
    temp_matrix = []
    for y in range(height):
        row = temp_data[y * width : (y + 1) * width]
        temp_matrix.append(row)
    
    return temp_matrix

# 主程序
def main(data_folder):
    metadata_file = os.path.join(data_folder, "metadata.csv")
    
    if not os.path.exists(metadata_file):
        print("未找到元数据文件:", metadata_file)
        return

    metadata = load_metadata(metadata_file)
    
    # 创建合并输出的 CSV 文件
    combined_csv_filename = os.path.join(data_folder, "combined_temperature_data.csv")
    
    with open(combined_csv_filename, "w", newline="") as combined_file:
        writer = csv.writer(combined_file)
        
        # 写入标题行
        writer.writerow(["Frame", "Y", "X", "Temperature (°C)"])
        
        for frame_index, width, height, bin_filename in metadata:
            bin_file_path = os.path.join(data_folder, bin_filename)
            
            if not os.path.exists(bin_file_path):
                print(f"未找到二进制文件: {bin_file_path}")
                continue

            # 处理二进制文件
            temp_matrix = process_bin_file(bin_file_path, width, height)
            
            # 将每个像素的温度数据写入合并 CSV
            for y in range(height):
                for x in range(width):
                    temperature = temp_matrix[y][x]
                    writer.writerow([frame_index, y, x, f"{temperature:.2f}"])
            
            print(f"已处理并写入: 帧 {frame_index}")
    
    print(f"\n所有数据已保存到: {combined_csv_filename}")

# 执行程序
if __name__ == "__main__":
    data_folder = input("请输入包含二进制数据和 metadata.csv 的文件夹路径：")
    main(data_folder)
