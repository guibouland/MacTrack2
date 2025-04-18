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


# Exemple d'utilisation
# zip_pred = "/home/gbouland/Stage-LPHI-2024/mactrack/visualisation/output/test_def/ROIs_pred_def/004_frame_masks.zip"
# zip_gt = "/home/gbouland/warm/model_test/model/dataset/test/test_y/004_masks.zip"
# canvas_shape = get_image_shape(
#    "/home/gbouland/Stage-LPHI-2024/mactrack/visualisation/output/comparison/004_frame_heatmap_roi_roi.png"
# )
# iou_global = compute_global_iou(zip_pred, zip_gt, canvas_shape=canvas_shape)
# print(f"IoU global : {iou_global:.4f}")


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


# print(
#    mean_global_iou(
#        "/home/gbouland/Stage-LPHI-2024/mactrack/visualisation/output/test_def/ROIs_pred_def/",
#        "/home/gbouland/warm/model_test/model_small/dataset/test/test_y/",
#        "/home/gbouland/Stage-LPHI-2024/mactrack/visualisation/output/comparison/",
#    )
# )

# print(
#    mean_global_iou(
#        "/home/gbouland/Stage-LPHI-2024/mactrack/visualisation/output/test_def/ROIs_pred_def/",
#        "/home/gbouland/warm/model_test/model_slides/dataset/train/train_y/",
#        "/home/gbouland/Stage-LPHI-2024/mactrack/visualisation/output/comparison/",
#    )
# )
#


## 2e test
def call(y_true, y_pred):
    _y_true = y_true[0].copy()
    _y_pred = y_pred["mask"]
    _y_pred[_y_pred > 0] = 1
    if np.sum(_y_true) == 0:
        _y_true = 1 - _y_true
        _y_pred = 1 - _y_pred
    intersection = np.logical_and(_y_true, _y_pred)
    union = np.logical_or(_y_true, _y_pred)
    score = 1.0 - np.sum(intersection) / np.sum(union)
    return score


def compute_one(y_true, y_pred):
    score = 0.0
    y_size = len(y_true)
    for i in range(y_size):
        _y_true = y_true[i].copy()
        _y_pred = y_pred[i]
        score += call(_y_true, _y_pred)
    return score / y_size
