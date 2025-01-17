# HDR Grouper Script

## Overview
The **HDR Grouper Script** is a Python tool designed to help photographers organize High Dynamic Range (HDR) photo sets by analyzing EXIF metadata in NEF files (Nikon RAW format). It groups photos based on their exposure bias and capture time, then organizes them into subfolders for streamlined processing.

---

## Features
- Extracts critical EXIF metadata from NEF files.
- Groups photos into HDR sets based on:
  - Exposure bias variations.
  - Time intervals (within 1 second).
  - Odd-numbered sets with a minimum of 3 photos.
- Organizes HDR groups into separate subfolders (e.g., `HDR_01`, `HDR_02`).
- Logs skipped files that lack necessary EXIF data.
- Includes progress indicators and error handling.
- Automatically retries EXIF extraction for certain error cases.
- Improved handling of edge cases like misconfigured file metadata.

---

## Requirements

### Python Libraries
Ensure the following libraries are installed:
- `os`
- `shutil`
- `exifread`
- `datetime`
- `tqdm`
- `icecream`
- `time`

To install missing libraries, use:
```bash
pip install exifread tqdm icecream
```

### Supported File Format
- `.nef` (Nikon RAW format)

---

## How to Use

### 1. Clone or Download the Script
Download the script to your local machine.

### 2. Run the Script
Run the script using Python:
```bash
python HDR_Grouper_v13.py
```

### 3. Provide the Folder Path
When prompted, input the full path to the folder containing your NEF files:
```
Enter the folder path to scan for NEF files: /path/to/your/folder
```

### 4. Output
- HDR sets are grouped and moved to subfolders (`HDR_01`, `HDR_02`, etc.) within the provided folder.
- Skipped files (due to missing EXIF data) are logged for review.

---

## Example Workflow
1. Place all your NEF files in a folder (e.g., `HDR_Photos`).
2. Run the script and enter the folder path when prompted.
3. Check the `HDR_Photos` folder for subfolders named `HDR_01`, `HDR_02`, etc.
4. Process the grouped HDR sets in your preferred photo editing software.

---

## Error Handling
- Files without required EXIF data are skipped and logged.
- Groups with no variation in exposure bias or insufficient photos are ignored.
- Added handling for partial groupings and warnings when folder permissions are restricted.

---

## Limitations
- Designed specifically for NEF files with valid EXIF metadata.
- Assumes consistent camera settings for HDR shooting (e.g., exposure bracketing).
- Customizable time intervals and grouping criteria are not yet implemented.

---

## Contributing
Feel free to submit bug reports, feature requests, or contributions to improve the script. Fork the repository and create a pull request for contributions.

---

## License
This script is released under the MIT License. See `LICENSE` for details.

---

## Author
Developed by [Your Name]. If you have any questions, feel free to contact me at [your.email@example.com].
