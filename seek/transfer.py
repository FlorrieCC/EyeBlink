import os
import csv

def convert_seek_to_lepton_format(seek_csv_path, output_csv_path, frame_height=None):
    # Read all rows from the original Seek Thermal CSV file
    with open(seek_csv_path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print("CSV file is empty!")
        return

    # Automatically detect frame width (number of columns)
    frame_width = len(rows[0])
    
    # Ask user to input frame height (number of rows per frame) if not given
    if frame_height is None:
        print(f"Detected frame width: {frame_width}")
        while True:
            try:
                frame_height = int(input("Enter the number of rows (frame height): "))
                break
            except ValueError:
                print("Invalid number. Please enter an integer.")

    total_rows = len(rows)
    if total_rows % frame_height != 0:
        print("⚠️ Warning: CSV row count is not divisible by frame height. Possible incomplete frame.")

    # Calculate total number of frames
    frame_count = total_rows // frame_height
    print(f"Detected total frames: {frame_count}, Frame size: {frame_width}x{frame_height}")

    # Convert and save to new CSV file in Lepton-style format
    with open(output_csv_path, "w", newline="") as out_f:
        writer = csv.writer(out_f)
        # Write header
        writer.writerow(["Frame", "Y", "X", "Temperature (°C)"])

        for frame_idx in range(frame_count):
            for y in range(frame_height):
                row_index = frame_idx * frame_height + y
                temp_row = [float(val) for val in rows[row_index]]
                for x, temp in enumerate(temp_row):
                    writer.writerow([frame_idx, y, x, f"{temp:.2f}"])

    print(f"✅ Converted CSV saved to: {output_csv_path}")


# ==== Main Program Entry ====
if __name__ == "__main__":
    seek_csv_path = input("Enter path to Seek Thermal CSV file: ").strip()
    output_csv = os.path.splitext(seek_csv_path)[0] + "_lepton_format.csv"
    convert_seek_to_lepton_format(seek_csv_path, output_csv)
