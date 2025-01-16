import os
import shutil
from exifread import process_file
from datetime import datetime
from tqdm import tqdm
from icecream import ic
import time

def extract_exif(filepath):
    """Extract EXIF information from an image."""
    try:
        with open(filepath, 'rb') as f:
            tags = process_file(f, details=False)
        # Ensure necessary tags are present
        if 'EXIF ExposureBiasValue' not in tags or 'EXIF DateTimeOriginal' not in tags:
            return None
        return {
            "File Name": os.path.basename(filepath),
            "Exposure Mode": str(tags.get('EXIF ExposureMode', 'N/A')),
            "Date Taken": tags.get('EXIF DateTimeOriginal', 'N/A'),
            "Exposure Bias": str(tags.get('EXIF ExposureBiasValue', 'N/A'))
        }
    except Exception as e:
        return None

def parse_date(date_str):
    """Parse EXIF date string into a datetime object."""
    try:
        return datetime.strptime(str(date_str), '%Y:%m:%d %H:%M:%S')
    except Exception:
        return None

def parse_exposure_bias(value):
    """Parse exposure bias value, handling fractional strings."""
    try:
        if '/' in value:
            numerator, denominator = map(float, value.split('/'))
            return numerator / denominator
        return float(value)
    except ValueError:
        return None

def group_hdr_photos(data):
    """Group photos into HDR sets based on exposure conditions."""
    hdr_groups = []
    temp_group = []

    for i in range(len(data)):
        current = data[i]

        if i > 0:
            prev = data[i - 1]

            # Compare time and exposure mode
            time_diff = (current["Date Taken"] - prev["Date Taken"]).total_seconds() if current["Date Taken"] and prev["Date Taken"] else float('inf')
            same_mode = current["Exposure Mode"] == prev["Exposure Mode"]

            # Start a new group if conditions are met
            if temp_group and (time_diff > 1 or not same_mode or len(temp_group) >= 9):
                hdr_groups.append(temp_group)
                temp_group = []

        # Add the current photo to the temp group
        temp_group.append(current)

    if temp_group:
        hdr_groups.append(temp_group)

    # Refine groups based on consistent interval and sum validation
    final_groups = []
    for group in hdr_groups:
        biases = [parse_exposure_bias(photo["Exposure Bias"].split()[0]) for photo in group if photo["Exposure Bias"] != 'N/A']
        biases = [b for b in biases if b is not None]  # Remove invalid values

        if not biases:
            continue

        # Check if there is any change in exposure bias
        unique_biases = set(biases)
        if len(unique_biases) == 1:
            continue  # Skip groups with no exposure bias change

        # Check for odd number of photos and minimum group size of 3
        if len(biases) < 3 or len(biases) % 2 == 0:
            continue

        # Validate intervals and exposure bias consistency
        base_bias = biases[0]
        adjusted_biases = [bias - base_bias for bias in biases]
        sorted_biases = sorted(adjusted_biases)

        intervals = [sorted_biases[i] - sorted_biases[i - 1] for i in range(1, len(sorted_biases))]

        num_under = len([b for b in biases if b < base_bias])
        num_over = len([b for b in biases if b > base_bias])

        if len(set(intervals)) == 1 and num_under == num_over:
            final_groups.append(group)

    return final_groups

def move_and_copy_photos(folder_path, hdr_groups):
    """Move and copy HDR photos into group subfolders."""
    for group_number, group in enumerate(tqdm(hdr_groups, desc="Moving HDR Groups"), start=1):
        group_folder = os.path.join(folder_path, f"HDR_{group_number:02}")
        os.makedirs(group_folder, exist_ok=True)

        for i, photo in enumerate(group):
            source_path = os.path.join(folder_path, photo["File Name"])
            target_path = os.path.join(group_folder, photo["File Name"])

            if i == 0:
                # Copy the initial photo
                shutil.copy2(source_path, target_path)
            else:
                # Move the remaining photos
                shutil.move(source_path, target_path)

def main():
    start_time = time.time()

    # 1. Ask for the folder path
    folder_path = input("Enter the folder path to scan for NEF files: ").strip()

    if not os.path.exists(folder_path):
        print("The specified path does not exist.")
        return

    # 2. Find all NEF files
    nef_files = [
        os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.nef')
    ]

    if not nef_files:
        print("No NEF files found in the specified folder.")
        return

    # 3. Extract EXIF data
    skipped_files = []  # Track files skipped due to unrecognized format
    data = []
    for file in tqdm(nef_files, desc="Extracting EXIF Data"):
        metadata = extract_exif(file)
        if metadata:
            metadata["Date Taken"] = parse_date(metadata["Date Taken"])
            data.append(metadata)
        else:
            skipped_files.append(file)  # Track unrecognized files

    # Display skipped files summary
    if skipped_files:
        print(f"\nSkipped {len(skipped_files)} files due to missing EXIF data:")
        for skipped_file in skipped_files:
            ic(skipped_file)  # Log the skipped file paths

    # Sort by date taken and file name
    data = sorted(data, key=lambda x: (x["Date Taken"] or datetime.min, x["File Name"]))

    # 4. Group HDR photos
    hdr_groups = group_hdr_photos(data)

    # 5. Move and copy HDR photos
    move_and_copy_photos(folder_path, hdr_groups)

    end_time = time.time()
    print("HDR photos have been organized into their respective subfolders.")
    print(f"Total run time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
