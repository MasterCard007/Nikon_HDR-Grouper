import os
import shutil
from exifread import process_file
from datetime import datetime
from fractions import Fraction
from tqdm import tqdm
import time

def extract_metadata(folder_path):
    def parse_date(date_str):
        """Parse EXIF date string into a datetime object."""
        try:
            return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except Exception:
            return None

    def parse_exposure_bias(value):
        """Parse exposure bias value as a fraction."""
        try:
            if '/' in value:
                return Fraction(value)
            return Fraction(float(value))
        except ValueError:
            return None

    files_data = []

    for file_name in tqdm(os.listdir(folder_path), desc="Extracting metadata", unit="file"):
        if file_name.lower().endswith(('.nef', '.jpg', '.jpeg', '.png')):
            file_path = os.path.join(folder_path, file_name)

            try:
                with open(file_path, 'rb') as f:
                    tags = process_file(f, details=False)

                date_taken = tags.get('EXIF DateTimeOriginal')
                exposure_bias = tags.get('EXIF ExposureBiasValue')

                files_data.append({
                    'File Name': file_name,
                    'Date Taken': parse_date(str(date_taken)) if date_taken else None,
                    'Exposure Bias': parse_exposure_bias(str(exposure_bias)) if exposure_bias else None
                })

            except Exception:
                pass  # Suppress error messages

    return files_data

def group_hdr_photos(photo_data):
    """Group photos into HDR sets based on relaxed time difference and exposure bias."""
    photo_data.sort(key=lambda x: x['File Name'])  # Sort by file name

    def is_within_margin(bias1, bias2, margin=Fraction(2)):
        return abs(bias1 - bias2) <= margin

    hdr_groups = []
    temp_group = []

    for i in range(len(photo_data)):
        current = photo_data[i]

        if i > 0:
            prev = photo_data[i - 1]

            # Compare time difference (relaxed to 3 seconds)
            time_diff = (current['Date Taken'] - prev['Date Taken']).total_seconds() if current['Date Taken'] and prev['Date Taken'] else float('inf')

            if temp_group and time_diff > 3:
                hdr_groups.append(temp_group)
                temp_group = []

        temp_group.append(current)

    if temp_group:
        hdr_groups.append(temp_group)

    # Split and validate groups
    valid_groups = []
    for group in hdr_groups:
        biases = [photo['Exposure Bias'] for photo in group if photo['Exposure Bias'] is not None]
        unique_biases = set(biases)

        if len(unique_biases) > 1:  # Ensure at least two distinct exposure biases
            min_bias = min(unique_biases)
            max_bias = max(unique_biases)

            if max_bias - min_bias > 3:  # Ensure the range of biases is greater than 3
                if len(biases) > 9:  # Split into smaller subgroups if too large
                    for i in range(0, len(biases), 9):
                        subgroup = group[i:i + 9]
                        if len(subgroup) in {3, 5, 7, 9}:
                            valid_groups.append(subgroup)
                elif len(biases) in {3, 5, 7, 9}:
                    biases.sort()
                    if all(is_within_margin(biases[i], biases[i + 1]) for i in range(len(biases) - 1)):
                        valid_groups.append(group)

    return valid_groups

def move_hdr_photos(folder_path, hdr_groups):
    """Move and copy HDR photos into group subfolders."""
    for group_index, group in enumerate(tqdm(hdr_groups, desc="Moving HDR photos", unit="group"), start=1):
        group_folder = os.path.join(folder_path, f"HDR_Group_{group_index:02}")
        os.makedirs(group_folder, exist_ok=True)

        for i, photo in enumerate(group):
            source_path = os.path.join(folder_path, photo['File Name'])
            target_path = os.path.join(group_folder, photo['File Name'])

            if i == 0:
                shutil.copy(source_path, target_path)  # Copy the first photo
            else:
                shutil.move(source_path, target_path)  # Move the rest

# Main function to run the script
def main():
    folder_path = input("Enter the folder path containing the photos: ").strip()

    if not os.path.exists(folder_path):
        print("The specified folder does not exist.")
        return

    start_time = time.time()

    photo_data = extract_metadata(folder_path)
    hdr_groups = group_hdr_photos(photo_data)
    move_hdr_photos(folder_path, hdr_groups)

    end_time = time.time()

    print(f"\nProcessing completed.")
    print(f"Total HDR groups created: {len(hdr_groups)}")
    print(f"Total processing time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
