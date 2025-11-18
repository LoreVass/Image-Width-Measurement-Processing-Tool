Image Width Measurement Processing Tool

This repository provides a Python tool for automated width measurement of objects in images using OpenCV.
It was originally developed for biological morphometrics but is fully generalizable to any elongated or irregular shape.

Overview

The tool measures object width along its entire length by:

Segmenting the object using adaptive thresholding and morphological cleanup.

Automatically aligning the main axis horizontally.

Measuring vertical thickness at every x-coordinate.

Converting pixel values to millimeters using a known reference length.

Computing summary statistics:

Minimum width

Maximum width

Mean width

Width ratio (mean width / total length)

Coefficient of variation (CV)

The output is saved as an Excel file on the user’s Desktop.

Features

Fully automated width measurement along the entire object.

Robust segmentation for real images (handles uneven lighting, reflections, noise).

CLAHE contrast normalization and Gaussian denoising.

Morphological filtering to remove speckles and fill small gaps.

Automatic orientation correction using minAreaRect.

Supports both black and white backgrounds.

Batch processing via CSV input.

Excel output containing all width statistics.

Validation with synthetic shapes (rectangles, ellipses, polygons).

Input Requirements

The program requires a CSV file with the following columns:

ID: Image filename

LENGTH: Known object length in millimeters

MIN_WIDTH: Minimum expected width (used as a filter)

MAX_WIDTH: Maximum expected width (reference only)

Example

ID,LENGTH,MIN_WIDTH,MAX_WIDTH
sample1.jpg,300,0,300
sample2.jpg,150,0,150

Images must be located inside the folder selected at runtime.

Output

The program produces an Excel file containing:

Image ID

Minimum width (mm)

Maximum width (mm)

Mean width (mm)

Width ratio

Coefficient of variation (%)

Expected minimum width

Expected maximum width

Error values compared to expected widths

Output is automatically saved to:

~/Desktop/output_measurements.xlsx

Installation

Install required dependencies:

pip install opencv-python pandas numpy xlsxwriter

Usage

Run the script:

python main.py


Follow the prompts to:

Specify whether the background is black.

Select the image folder.

Select the CSV file.

The script will process every image and generate the Excel output.

Validation

The tool has been validated using synthetic shapes such as:

Rectangles (constant width)

Ellipses

Trapezoids

Triangles

Cross shapes

Star shapes

Fish-like polygons

These tests confirm that width measurement and CV behave consistently with geometric expectations.

Project Structure
Image-Width-Measurement-Processing-Tool/
├── main.py
├── README.md
├── example.csv
└── Test_shapes/

License

Released under the MIT License.
