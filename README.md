# Image Width Measurement Processing Tool

This repository provides a Python tool for automated width measurement of objects from images using OpenCV.  
The method was originally developed for biological morphometrics but is fully general-purpose and applicable to any elongated or irregular shape.

---

## Overview

The tool extracts object width along its entire length by:

1. Segmenting the object using adaptive thresholding and morphological operations.  
2. Automatically aligning the main axis horizontally using a minimum-area bounding box.  
3. Measuring vertical thickness at each x-coordinate.  
4. Converting pixel values to millimeters using a known reference length.  
5. Computing summary statistics:
   - **Minimum width**
   - **Maximum width**
   - **Mean width**
   - **Width ratio** (mean width / total length)
   - **Coefficient of Variation (CV)**

The final results are saved to an Excel file on the user’s Desktop.

---

## Features

- Automated measurement of width across the entire object  
- Robust segmentation for real photographs  
- CLAHE contrast normalization  
- Gaussian denoising  
- Morphological cleanup to remove speckles and fill gaps  
- Automatic alignment via `minAreaRect`  
- Supports black and white backgrounds  
- Batch processing through CSV input  
- Excel output with detailed width metrics  
- Validated with synthetic control shapes (rectangles, ellipses, polygons)

---

## Input Requirements

The tool requires a CSV file containing the following columns:

| Column        | Description                                    |
|---------------|------------------------------------------------|
| **ID**        | Image filename                                 |
| **LENGTH**    | True object length in millimeters              |
| **MIN_WIDTH** | Minimum expected width (filter threshold)      |
| **MAX_WIDTH** | Maximum expected width (reference only)        |

**Example CSV:**

```
ID,LENGTH,MIN_WIDTH,MAX_WIDTH
sample1.jpg,300,0,300
sample2.jpg,150,0,150
```

Images must be located inside the folder selected during execution.

---

## Output

The program produces an Excel file containing:

- Image ID  
- Minimum width (mm)  
- Maximum width (mm)  
- Mean width (mm)  
- Width ratio  
- Coefficient of variation (%)  
- Expected minimum width  
- Expected maximum width  
- Error margins for minimum and maximum widths  

Output is saved automatically to:

```
~/Desktop/output_measurements.xlsx
```

---

## Installation

Install required dependencies:

```
pip install opencv-python pandas numpy xlsxwriter
```

---

## Usage

Run the tool from the terminal:

```
python main.py
```

You will be prompted to:

1. Specify whether the background is black.  
2. Select the folder containing images.  
3. Select the CSV file.

The script will process all entries and generate the Excel output file.

---

## Validation

The tool has been validated on synthetic shapes including:

- Rectangles  
- Ellipses  
- Trapezoids  
- Triangles  
- Cross-shaped polygons  
- Star-shaped polygons  
- Synthetic fish-like shapes  

These tests confirm that the width measurements and CV values behave consistently with geometric expectations.

---

## Project Structure

```
Image-Width-Measurement-Processing-Tool/
├── main.py
├── README.md
├── example.csv
└── Test_shapes/
```

---

## License

This project is released under the MIT License.
