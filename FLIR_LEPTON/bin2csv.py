import os
import csv

# Set temperature range
min_temp_in_celsius = 20.0
max_temp_in_celsius = 35.0

# Map grayscale value to temperature
def map_g_to_temp(g):
    return ((g * (max_temp_in_celsius - min_temp_in_celsius)) / 255.0) + min_temp_in_celsius

# Load metadata file
def load_metadata(metadata_path):
    metadata = []
    with open(metadata_path, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            frame_index = int(row[0])
            width = int(row[1])
            height = int(row[2])
            filename = os.path.basename(row[3])  # Extract only the filename
            metadata.append((frame_index, width, height, filename))
    return metadata

# Parse binary file and convert to temperature data
def process_bin_file(file_path, width, height):
    with open(file_path, "rb") as f:
        raw_data = f.read()
    
    # Convert raw grayscale data to temperature
    temp_data = [map_g_to_temp(b) for b in raw_data]

    # Reshape to 2D array for saving to CSV
    temp_matrix = []
    for y in range(height):
        row = temp_data[y * width : (y + 1) * width]
        temp_matrix.append(row)
    
    return temp_matrix

# Main program
def main(data_folder):
    metadata_file = os.path.join(data_folder, "metadata.csv")
    
    if not os.path.exists(metadata_file):
        print("Metadata file not found:", metadata_file)
        return

    metadata = load_metadata(metadata_file)
    
    # Create combined CSV output
    combined_csv_filename = os.path.join(data_folder, "combined_temperature_data.csv")
    
    with open(combined_csv_filename, "w", newline="") as combined_file:
        writer = csv.writer(combined_file)
        
        # Write header
        writer.writerow(["Frame", "Y", "X", "Temperature (°C)"])
        
        for frame_index, width, height, bin_filename in metadata:
            bin_file_path = os.path.join(data_folder, bin_filename)
            
            if not os.path.exists(bin_file_path):
                print(f"Binary file not found: {bin_file_path}")
                continue

            # Process binary file
            temp_matrix = process_bin_file(bin_file_path, width, height)
            
            # Write each pixel's temperature data to the CSV
            for y in range(height):
                for x in range(width):
                    temperature = temp_matrix[y][x]
                    writer.writerow([frame_index, y, x, f"{temperature:.2f}"])
            
            print(f"Processed and written: Frame {frame_index}")
    
    print(f"\nAll data saved to: {combined_csv_filename}")

# Run program
if __name__ == "__main__":
    data_folder = input("Enter the folder path containing binary data and metadata.csv: ")
    main(data_folder)
