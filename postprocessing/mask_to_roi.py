import cv2
import numpy as np
from roifile import ImagejRoi, ROI_TYPE
import os
import zipfile


def mask_to_roi(mask_path, output_path):
    """
    Convert a binary mask PNG image to an ImageJ ROI file and save it.

    Args:
        mask_path (str): Path to the binary mask image (PNG or JPG).
        output_path (str): Path to save the .roi file.
    """
    # Read the mask image as grayscale
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"Could not read mask image: {mask_path}")

    # Threshold to ensure binary
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No contours found in mask.")

    # Use the largest contour
    contour = max(contours, key=cv2.contourArea)
    points = contour.squeeze()
    if points.ndim == 1:
        points = np.expand_dims(points, 0)
    points = [(int(x) * 2, int(y) * 2) for x, y in points]

    # Create ImageJ ROI
    roi = ImagejRoi.frompoints(points)
    roi.roitype = ROI_TYPE.POLYGON

    # Save ROI
    roi.tofile(output_path)


def masks_folder_to_zip(input_folder):
    """
    Convert all mask images in a folder to ImageJ ROI files and save them in a zip file.

    Args:
        input_folder (str): Path to the folder containing mask images.
    """
    roi_files = []
    temp_folder = os.path.join(input_folder, "_temp_rois")
    os.makedirs(temp_folder, exist_ok=True)

    for fname in sorted(os.listdir(input_folder)):
        if fname.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")):
            mask_path = os.path.join(input_folder, fname)
            roi_name = os.path.splitext(fname)[0] + ".roi"
            roi_path = os.path.join(temp_folder, roi_name)
            try:
                mask_to_roi(mask_path, roi_path)
                roi_files.append(roi_path)
            except Exception as e:
                print(f"Skipping {fname}: {e}")

    zip_name = os.path.basename(os.path.normpath(input_folder)) + ".zip"
    zip_path = os.path.join(os.path.dirname(input_folder), zip_name)
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for roi_file in roi_files:
            zipf.write(roi_file, arcname=os.path.basename(roi_file))

    # Clean up temporary ROI files
    for roi_file in roi_files:
        os.remove(roi_file)
    os.rmdir(temp_folder)

    print(f"Saved {len(roi_files)} ROIs to {zip_path}")


def folder_to_zips(input_folder):
    """
    Convert all subfolders in the input folder to zip files containing ImageJ ROI files in an output folder.

    Args:
        input_folder (str): Path to the folder containing subfolders with mask images.
    """
    for subfolder in sorted(os.listdir(input_folder)):
        subfolder_path = os.path.join(input_folder, subfolder)
        if os.path.isdir(subfolder_path):
            print(f"Processing {subfolder_path}...")
            masks_folder_to_zip(subfolder_path)


folder_to_zips(
    "/home/gbouland/video_norma/output/list_def",
)
