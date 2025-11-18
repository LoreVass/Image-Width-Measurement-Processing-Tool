import cv2
import pandas as pd
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox


# --- FILE SELECTION FUNCTIONS ---
def select_folder():
    """Opens a dialog to select an image folder."""
    folder_selected = filedialog.askdirectory(title="Select Image Folder")
    if folder_selected:
        print(f"Selected Image Folder: {folder_selected}")
    return folder_selected


def select_file():
    """Opens a dialog to select a CSV file."""
    file_selected = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[["CSV Files", "*.csv"]]
    )
    if file_selected:
        print(f"Selected CSV File: {file_selected}")
    return file_selected


def ask_background_color():
    """
    Ask the user whether the background is black (object lighter)
    or not (assume white / light background with darker object).

    Returns True if background is black, False otherwise.
    """
    answer = messagebox.askyesno(
        "Background Color",
        "Is the background black?\n\n"
        "YES  -> background black, object lighter\n"
        "NO   -> background white/light, object darker"
    )
    return answer  # True if black, False if white


# --- MASK CREATION FOR REAL OBJECTS ---
def get_binary_mask(image_bgr, background_is_black: bool):
    """
    Creates a clean binary mask (255 = object, 0 = background) for real photos.
    Handles:
      - uneven lighting (CLAHE)
      - small speckles (morphology)
      - known background polarity (black vs white)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Improve contrast (helps with texture / reflections)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)

    # Reduce noise
    blurred = cv2.GaussianBlur(eq, (5, 5), 0)

    # Threshold based on background color
    if background_is_black:
        # dark background, lighter object
        _, binary = cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    else:
        # light background, darker object
        _, binary = cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

    # Morphological cleaning: remove speckles + fill tiny gaps
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    return binary   # 255 = object, 0 = background


# --- ALIGN OBJECT HORIZONTALLY ---
def align_mask_horizontal(binary):
    """
    Rotates the binary mask so that the object's main axis is horizontal.
    Uses the minAreaRect of the largest contour.
    Returns the rotated mask.
    """
    h, w = binary.shape

    contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return binary  # fallback: nothing to rotate

    largest = max(contours, key=cv2.contourArea)

    rect = cv2.minAreaRect(largest)  # (center, (w_box, h_box), angle)
    (cx, cy), (w_box, h_box), angle = rect

    # We want the LONG side to be horizontal
    if w_box < h_box:
        angle = angle + 90.0

    # Rotate in the opposite direction of the detected angle
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    rotated = cv2.warpAffine(
        binary, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=0
    )

    return rotated


# --- MEASUREMENT FUNCTION ---
def measure_width(image_path, known_length_mm, expected_min_width_mm, background_is_black):
    """
    Real-object version:
      - reads color image
      - builds a robust binary mask
      - aligns object horizontally
      - measures vertical thickness for every x-column across whole body
      - uses known length (mm) as scale.

    known_length_mm: true object length (tip-to-tip) in mm.
    expected_min_width_mm: filter to ignore very thin/noisy columns if desired.
    background_is_black: bool, True if background is black.
    """
    # Load BGR image
    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        print(f"[ERROR] Image file not found or unreadable: {image_path}. Skipping...")
        return None

    # 1) Binary mask (handles texture, speckles)
    binary = get_binary_mask(image_bgr, background_is_black)

    # 2) Auto-rotate so main axis is horizontal
    binary_rot = align_mask_horizontal(binary)

    # 3) Largest contour on rotated mask
    contours, _ = cv2.findContours(
        binary_rot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        print(f"[WARNING] No contours found in {image_path}. Skipping...")
        return None

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    if w == 0 or h == 0:
        print(f"[WARNING] Zero-size bounding box in {image_path}. Skipping...")
        return None

    # Length in pixels = horizontal extent AFTER rotation
    length_px = w
    scale_factor = known_length_mm / length_px  # mm per pixel along x

    # 4) Measure thickness at each x (column) across the whole body
    widths_pixels = []
    for col in range(x, x + w):
        column = binary_rot[y:y + h, col]
        width_px = np.sum(column == 255)
        widths_pixels.append(width_px)

    if not widths_pixels:
        print(f"[WARNING] No width samples in {image_path}. Skipping...")
        return None

    # Convert to mm
    widths_mm = [w_px * scale_factor for w_px in widths_pixels]

    # Filter tiny/noisy columns if you want (set MIN_WIDTH to 0 in CSV to keep all)
    filtered_widths_mm = [w_mm for w_mm in widths_mm if w_mm >= expected_min_width_mm]
    if not filtered_widths_mm:
        print(f"[WARNING] No valid widths >= expected min ({expected_min_width_mm} mm) in {image_path}. Skipping...")
        return None

    # Stats
    min_width_mm = float(np.min(filtered_widths_mm))
    max_width_mm = float(np.max(filtered_widths_mm))
    mean_width_mm = float(np.mean(filtered_widths_mm))

    width_ratio = mean_width_mm / known_length_mm
    std_dev_width_mm = float(np.std(filtered_widths_mm))
    coefficient_variation = (std_dev_width_mm / mean_width_mm) * 100 if mean_width_mm != 0 else 0.0

    print(
        f"[OK] {os.path.basename(image_path)} | "
        f"Min = {min_width_mm:.2f} mm, Max = {max_width_mm:.2f} mm, "
        f"Mean = {mean_width_mm:.2f} mm, Ratio = {width_ratio:.4f}, CV = {coefficient_variation:.2f}%"
    )

    return (
        os.path.basename(image_path),
        min_width_mm,
        max_width_mm,
        mean_width_mm,
        width_ratio,
        coefficient_variation,
    )


# --- MAIN FUNCTION ---
def main():
    # Tkinter root
    root = tk.Tk()
    root.withdraw()

    # Ask background color FIRST
    background_is_black = ask_background_color()
    print(f"Background is black: {background_is_black}")

    # Select image folder and CSV
    image_folder = select_folder()
    if not image_folder:
        messagebox.showerror("Error", "No image folder selected. Exiting.")
        return

    csv_file = select_file()
    if not csv_file:
        messagebox.showerror("Error", "No CSV file selected. Exiting.")
        return

    # Read CSV
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        messagebox.showerror("Error", f"Error reading CSV file:\n{e}")
        return

    required_cols = ['ID', 'LENGTH', 'MIN_WIDTH', 'MAX_WIDTH']
    for col in required_cols:
        if col not in df.columns:
            messagebox.showerror("Error", f"CSV file is missing required column: '{col}'")
            return

    results = []
    total_rows = len(df)
    print(f"Processing {total_rows} entries from CSV...\n")

    for index, row in df.iterrows():
        image_name = str(row['ID'])
        image_path = os.path.join(image_folder, image_name)

        if not os.path.exists(image_path):
            print(f"[MISSING] Image not found: {image_path}. Skipping...")
            continue

        try:
            known_length_mm = float(row['LENGTH'])
            expected_min_width = float(row['MIN_WIDTH'])
            expected_max_width = float(row['MAX_WIDTH'])
        except Exception as e:
            print(f"[ERROR] Invalid numeric value in row {index} ({image_name}): {e}. Skipping...")
            continue

        result = measure_width(image_path, known_length_mm, expected_min_width, background_is_black)
        if result is not None:
            (img_id,
             min_width_mm,
             max_width_mm,
             mean_width_mm,
             width_ratio,
             coefficient_variation) = result

            min_width_error = abs(min_width_mm - expected_min_width)
            max_width_error = abs(max_width_mm - expected_max_width)

            results.append(
                (
                    img_id,
                    min_width_mm,
                    max_width_mm,
                    mean_width_mm,
                    width_ratio,
                    coefficient_variation,
                    expected_min_width,
                    expected_max_width,
                    min_width_error,
                    max_width_error,
                )
            )

    if not results:
        messagebox.showwarning("No Results", "No valid measurements were produced. Check logs in the console.")
        return

    # Save results to Desktop as Excel
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_excel_file = os.path.join(desktop_path, "output_measurements.xlsx")

    output_df = pd.DataFrame(
        results,
        columns=[
            'ID',
            'Min Width (mm)',
            'Max Width (mm)',
            'Mean Width (mm)',
            'Width Ratio',
            'Coefficient of Variation (%)',
            'Expected Min Width (mm)',
            'Expected Max Width (mm)',
            'Min Width Error (mm)',
            'Max Width Error (mm)',
        ],
    )

    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        output_df.to_excel(writer, index=False)

    print(f"\n✅ Results saved to: {output_excel_file}")
    messagebox.showinfo("Done", f"Results saved to:\n{output_excel_file}")


if __name__ == "__main__":
    main()
