import cv2
import pandas as pd
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


# --- FILE SELECTION FUNCTIONS ---
def select_folder():
    """Opens a dialog to select an image folder."""
    folder_selected = filedialog.askdirectory(title="Select Image Folder")
    if folder_selected:
        print(f"Selected Image Folder: {folder_selected}")
    return folder_selected


def select_file():
    """Opens a dialog to select a CSV file."""
    file_selected = filedialog.askopenfilename(title="Select CSV File", filetypes=[["CSV Files", "*.csv"]])
    if file_selected:
        print(f"Selected CSV File: {file_selected}")
    return file_selected


# --- MEASUREMENTS FUNCTIONS --- SELECT THRESHOLD VALUE
def select_threshold():
    """Opens a dialog to input the threshold value."""
    threshold = simpledialog.askinteger("Input", "Enter threshold value:", minvalue=0, maxvalue=255, initialvalue=15)
    if threshold is None:  # If the user cancels the dialog
        print("No threshold value entered. Using default (15).")
        threshold = 15
    return threshold


def confirm_threshold(threshold_value, image):
    """Shows a confirmation dialog asking if the user is happy with the threshold and displays the thresholded image."""
    # Apply manual thresholding
    _, binary = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)

    # Debugging visualization
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(f"No contours found in {image}. Skipping...")
        return None

    # Get the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    debug_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(debug_image, [largest_contour], -1, (0, 0, 255), 2)
    cv2.imshow("Thresholded Image", debug_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Ask user for confirmation
    answer = messagebox.askquestion("Threshold Accepted?",
                                    f"Are you happy with the selected threshold value of {threshold_value}?",
                                    icon='question')
    return answer.lower() == 'yes'


def measure_width(image_path, known_length_mm, expected_min_width_mm, threshold_value=None):
    """Processes an image to measure width using contours and thresholding."""
    # Load image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Image file not found: {image_path}. Skipping...")
        return None

    # If no threshold is passed, prompt the user to enter it
    if threshold_value is None:
        threshold_value = select_threshold()

    # Keep asking for a valid threshold until the user is satisfied
    while not confirm_threshold(threshold_value, image):
        threshold_value = select_threshold()

    # Apply manual thresholding
    _, binary = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(f"No contours found in {image_path}. Skipping...")
        return None

    # Get the largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Get bounding box dimensions
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Scaling factor calculation
    scale_factor = known_length_mm / h

    # Measure width across the object's height
    widths = [np.sum(binary[row, x:x + w] == 255) for row in range(y, y + h)]

    # Convert width from pixels to mm
    widths_mm = [width * scale_factor for width in widths]

    # Filter out widths smaller than the expected minimum width
    filtered_widths_mm = [width for width in widths_mm if width >= expected_min_width_mm]
    if not filtered_widths_mm:
        print(f"No valid widths found in {image_path}. Skipping...")
        return None

    # Calculate width statistics
    min_width_mm = min(filtered_widths_mm)
    max_width_mm = max(filtered_widths_mm)
    mean_width_mm = np.mean(filtered_widths_mm)

    # Width ratio and coefficient of variation
    width_ratio = mean_width_mm / known_length_mm
    std_dev_width_mm = np.std(filtered_widths_mm)
    coefficient_variation = (std_dev_width_mm / mean_width_mm) * 100



    print(
        f"Processing {image_path}: Min Width = {min_width_mm} mm, Max Width = {max_width_mm} mm, Mean Width = {mean_width_mm} mm, Width Ratio = {width_ratio}, CV = {coefficient_variation}%")

    return os.path.basename(image_path), min_width_mm, max_width_mm, mean_width_mm, width_ratio, coefficient_variation


# --- MAIN FUNCTION---
def main():
    # --- FILE SELECTION ---
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    image_folder = select_folder()
    csv_file = select_file()

    # --- READ CSV FILE ---
    df = pd.read_csv(csv_file)

    # --- PROCESS IMAGES AND COMPUTE MEASUREMENTS ---
    results = []
    for index, row in df.iterrows():
        image_name = row['ID']
        image_path = os.path.join(image_folder, image_name)

        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}. Skipping...")
            continue

        known_length_mm = row['LENGTH']
        expected_min_width = row['MIN_WIDTH']
        expected_max_width = row['MAX_WIDTH']

        result = measure_width(image_path, known_length_mm, expected_min_width)
        if result:
            # Add expected values and errors
            result += (expected_min_width, expected_max_width, abs(result[1] - expected_min_width), abs(result[2] - expected_max_width))
            results.append(result)

    # --- SAVE RESULTS TO DESKTOP AS EXCEL FILE ---
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_excel_file = os.path.join(desktop_path, "output_measurements.xlsx")
    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        output_df = pd.DataFrame(results, columns=['ID', 'Min Width (mm)', 'Max Width (mm)', 'Mean Width (mm)',
                                                   'Width Ratio', 'Coefficient of Variation (%)', 'Expected Min Width', 'Expected Max Width',
                                                   'Min Width Error', 'Max Width Error'])
        output_df.to_excel(writer, index=False)

    print(f"Results saved to {output_excel_file}")

# --- RUN SCRIPT ONLY IF EXECUTED DIRECTLY ---
if __name__ == "__main__":
    main()
