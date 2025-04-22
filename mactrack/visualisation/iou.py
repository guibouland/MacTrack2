import numpy as np
from read_roi import read_roi_zip
from skimage.draw import polygon
import cv2
import os


def roi_to_mask(shape, roi):
    mask = np.zeros(shape, dtype=np.uint8)
    x = np.array(roi["x"])
    y = np.array(roi["y"])
    rr, cc = polygon(y, x)
    mask[rr, cc] = 1
    return mask


def build_global_mask(roi_dict, shape):
    mask = np.zeros(shape, dtype=np.uint8)
    for roi in roi_dict.values():
        # print(roi)
        try:
            mask |= roi_to_mask(shape, roi)
        except Exception as e:
            print(f"Error processing ROI {roi}: {e}")
            continue
    return mask


def compute_global_iou(zip1_path, zip2_path, shape):
    rois1 = read_roi_zip(zip1_path)
    rois2 = read_roi_zip(zip2_path)

    mask1 = build_global_mask(rois1, shape)
    mask2 = build_global_mask(rois2, shape)

    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()

    iou = intersection / union if union > 0 else 0
    return iou


def get_image_shape(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")
    return img.shape[:2]


def get_folder_shapes(folder_path):
    """Gets the shapes of images in a folder.
    WARNING! The folder must only contain images.
    The function will raise an error if it finds any other files.

    Args:
        folder_path (str): Folder path containing images.

    Raises:
        ValueError: If the folder contains non-image files or if an image cannot be read.

    Returns:
        list: List of the shapes of the images in the folder.
    """
    shapes = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img = cv2.imread(os.path.join(folder_path, filename))
            if img is None:
                raise ValueError(
                    f"Could not read image at {os.path.join(folder_path, filename)}"
                )
            shapes.append(img.shape[:2])
        else:
            raise ValueError(f"File {filename} is not an image.")
    return shapes


def mean_global_iou(zip_pred_folder, zip_gt_folder, image_folder):
    """Function that computes the mean global IoU between two folders of zip files.
    The zip files are expected to contain ROIs in ImageJ format.
    The function will raise an error if the number of zip files in the two folders is not the same.

    Args:
        zip_pred_folder (str): Path to the folder containing predicted zip files.
        zip_gt_folder (str): Path to the folder containing ground truth zip files.
        image_folder (str): Path to the folder containing images to get the shape.

    Raises:
        ValueError: If the number of zip files in the two folders is not the same.

    Returns:
        float: Mean global IoU between the predicted and ground truth zip files.
    """
    zip_pred_files = [
        os.path.join(zip_pred_folder, f) for f in sorted(os.listdir(zip_pred_folder))
    ]
    for zip_ in zip_pred_files:
        if not zip_.endswith(".zip"):
            raise ValueError(f"{zip_} is not a zip file.")
    zip_gt_files = [
        os.path.join(zip_gt_folder, f) for f in sorted(os.listdir(zip_gt_folder))
    ]
    for zip_ in zip_gt_files:
        if not zip_.endswith(".zip"):
            raise ValueError(f"{zip_} is not a zip file.")
    shapes = get_folder_shapes(image_folder)
    if len(zip_pred_files) != len(zip_gt_files):
        raise ValueError("The number of zip files in the two folders is not the same.")

    ious = []
    for zip_pred, zip_gt, shape in zip(zip_pred_files, zip_gt_files, shapes):
        print(zip_pred, zip_gt, shape)
        iou = compute_global_iou(zip_pred, zip_gt, shape=shape)
        ious.append(iou)

    mean_iou = np.mean(ious)
    return mean_iou, ious
