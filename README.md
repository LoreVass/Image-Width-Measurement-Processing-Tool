# Image Width Measurement Processing Tool

## Overview
This project provides a Python-based tool for processing images and measuring the width of irregular 2D objects images. The script was written for a research project focused on duck bills, hence the irregular shape. The tool uses the OpenCV library to analyse and process image files, comparing the measurements to predefined expected values from a CSV file. The processed results are then saved in an Excel file for further analysis. The correct measurements are only possible if scaling, the total length of the image in mm, is provided.

## Features
- File Selection: Selects image folder and CSV file through a user-friendly file dialog.
- Measurement Function: Measures the width of objects in images using contours and thresholds and computes statistics such as mean width, coefficient of variation, and width ratios.
- Output: Results are saved in an Excel file on the user's desktop.
- Error Checking: Handles missing or invalid images, skipping processing for these files. Moreover, it enables the user to select the correct threshold to define the shape outline.

## Requirements
- Python 3.x
- Required libraries:
  - OpenCV (`cv2`): For image processing and measurement.
  - Pandas (`pd`): For handling CSV and Excel data.
  - Numpy (`np`): For numerical operations.
  - Tkinter (`tk`): For graphical file dialogs.

You can install the required libraries using `pip`:

bash:
pip install opencv-python pandas numpy tkinter


## How to Use

1. **Run the Script**:
   - Ensure that your Python environment has the required libraries installed.
   

2. **Select Image Folder**:
   - A file dialog will appear asking you to select the folder containing the images you want to process.
   - The script will process all images in the folder.

3. **Select CSV File**:
   - Another file dialog will appear to allow you to select a CSV file containing the expected measurements, corresponding image IDs and a scaling factor.
   - The CSV file must have columns: `ID`, `LENGTH`, `MIN_WIDTH`, `MAX_WIDTH`. 'LENGTH' will be used as the scaling factor.

4. **Measurement, Debug and Results**:
   - The script will ask to select a threshold in order to correctly outline he object.
   - After selection, the script will ask to confirm the selected threshold. If not confirmed, it will be possible to change the threshold value.
   - The script will then process the image, measuring its width based on the contours found and comparing it to the values in the CSV file.
   - The process is repeated for each image.
   - After processing, the results will be saved in an Excel file named `output_measurements.xlsx` on your desktop.

5. **Review Results**:
   - The output Excel file will contain columns for the measured widths, expected widths, and errors.

## Example CSV Format
'''csv
ID,LENGTH,MIN_WIDTH,MAX_WIDTH
image1.jpg,150,10,50
image2.jpg,200,15,60
...
'''

- `ID`: The image filename (e.g., `image1.jpg`).
- `LENGTH`: Known length in millimeters of the object in the image ---> Used as scaling factor.
- `MIN_WIDTH`: Expected minimum width of the object in millimeters ---> Used to limit measurements to avoid errors.
- `MAX_WIDTH`: Expected maximum width of the object in millimeters ---> If available, used as comparison.

## Notes
- Error Handling: If any image or CSV file is not found or is not processed correctly, it will be skipped, and a message will be printed to the console.
- The tool is intended for use with images where the object is clearly distinguishable from the background.
