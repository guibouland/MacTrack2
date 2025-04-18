from PIL import Image, ImageDraw
from read_roi import read_roi_zip, read_roi_file
import cv2
import numpy as np
import os
import sys
from roifile import ImagejRoi
import zipfile
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from locate.locate import locate_frame

# from visualisation.iou import mean_global_iou


def visualize_roi(image_path, roi_path, output_folder, color="red"):
    """Visualize the region of interest (ROI) on the image without white borders.

    Args:
        image_path (str): Path to the image file.
        roi_path (str): Path to the ROI file. Can be a .zip or .roi file.
        output_folder (str): Path to the folder where the output image will be saved.
        color (str, optional): Outline color for the ROI. Defaults to "red".

    Raises:
        ValueError: If the ROI file format is not supported.
        ValueError: If the ROI type is not recognized.

    Returns:
        None
    """
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    if roi_path.endswith(".roi"):
        rois = read_roi_file(roi_path)
    elif roi_path.endswith(".zip"):
        rois = read_roi_zip(roi_path)
    else:
        raise ValueError(f"Unsupported ROI file format: {roi_path}")

    for roi_name, roi in rois.items():
        if roi["type"] == "polygon":
            points = list(zip(roi["x"], roi["y"]))
            draw.line(points + [points[0]], fill=color, width=1)
        else:
            raise ValueError(f"Unsupported ROI type: {roi['type']}")

    output_path = os.path.join(
        output_folder, f"{os.path.splitext(os.path.basename(image_path))[0]}_roi.png"
    )
    image.save(output_path, "PNG")


# Example usage

# image_path = "/home/gbouland/warm/run_models2/model/dataset/test/test_x/001_frame.png"
# roi_path = "/home/gbouland/warm/run_models2/model/dataset/test/test_y/001_masks.zip"
# visualize_roi(
#    image_path, roi_path, "/home/gbouland/Stage-LPHI-2024/mactrack/visualisation/"
# )
# input_image = (
#    "/home/gbouland/warm/run_models1/model_crop/dataset/test/test_x/001_frame_crop.png"
# )
# roi_path = (
#    "/home/gbouland/warm/run_models1/model_crop/dataset/test/test_y/001_masks_crop.zip"
# )
# visualize_roi(
#    image_path=input_image,
#    roi_path=roi_path,
#    output_folder="/home/gbouland/Stage-LPHI-2024/mactrack/visualisation",
# )


def pred_to_rois(pred, min_length):
    """Take the prediction (form the output of the 'locate_frame' function) and convert it to ROIs.
    This function extracts the contours of the masks and creates ROIs for each contour.
    Each ROI is represented as a polygon with its coordinates.

    Args:
        pred (list): Prediction from the model on a frame. Should be the output of the 'locate_frame' function.
        Each element in the list is a tuple containing a list of masks and a score.
        min_length (int): Minimum length of the contour to be considered a valid ROI (to prevent points or artefacts).

    Returns:
        dict: A dictionary where each key is a unique name for the ROI and the value is a dictionary containing
              the ROI type, coordinates (x, y), number of points (n), width, name, and position.
    """
    rois = {}

    for masks_group, score in pred:
        for obj_index, obj in enumerate(masks_group):
            mask = obj["mask"]
            if np.any(mask):
                contours, _ = cv2.findContours(
                    mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in contours:
                    all_points = contour
                    x_coords = [float(pt[0][0]) for pt in all_points]
                    y_coords = [float(pt[0][1]) for pt in all_points]
                    if (
                        not len(x_coords) < min_length
                        and not len(y_coords) < min_length
                    ):
                        name = f"{obj_index:04d}_contour_{len(rois) + 1}"
                        rois[name] = {
                            "type": "polygon",
                            "x": x_coords,
                            "y": y_coords,
                            "n": len(x_coords),
                            "width": 0,
                            "name": name,
                            "position": 0,
                        }
    return rois


def save_rois_to_folder(rois, folder_path, frame_name):
    """Save ROIs for each objects as .roi files in a zip file.

    Args:
        rois (dict): Dictionary containing ROIs. Each key is a unique name for the ROI and the value is a dictionary
        folder_path (str): Path to the folder where the ROIs will be saved.
        frame_name (str): Name of the frame. This will be used to name the zip file.

    Returns:
        None
    """
    os.makedirs(folder_path, exist_ok=True)

    grouped_rois = {}
    for name, roi in rois.items():
        image_id = name.split("_")[0]
        if image_id not in grouped_rois:
            grouped_rois[image_id] = {}
        grouped_rois[image_id][name] = roi

    for image_id, image_rois in grouped_rois.items():
        zip_path = os.path.join(folder_path, f"{frame_name}_masks.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for name, roi in image_rois.items():
                x = np.round(roi["x"]).astype(np.int16)
                y = np.round(roi["y"]).astype(np.int16)

                ij_roi = ImagejRoi.frompoints(np.column_stack((x, y)))
                ij_roi.name = name

                roi_path = os.path.join(folder_path, f"{name}.roi")
                ij_roi.tofile(roi_path)

                zipf.write(roi_path, arcname=f"{name}.roi")

                os.remove(roi_path)


def comp_model_frame(frame, model_path, roi_frame):
    """Create an image comparison between the model and the ground truth.
    This function takes a frame, a model path, and a ground truth ROI frame.
    It is used to compare the model's predictions with the ground truth after the model has been run.
    Be careful, in your 'models' folder, if you have more than one model, the function will
    take all of the available models and you will see a number of red outlines according to the number of models.
    We then recommend you to only keep one model in the 'models' folder, be it the one you want to compare with the ground truth.

    Args:
        frame (str): Path to the frame image.
        model_path (str): Path to the model folder. It must include the 'models' and 'dataset' folders, as well as the 'dataset.csv' and 'PETA.json' files.
        roi_frame (str): Path to the ground truth ROI frame. It must be a .zip file containing the ROIs or a .roi file.

    Returns:
        None
    """
    # Get the caller script's directory
    caller_path = os.path.dirname(os.path.abspath(__file__))
    # Define the output directory
    ouptut_dir = os.path.join(caller_path, "output")

    # Locate objects in the frame using the model
    loc = locate_frame(frame, model_path)
    # Convert model predictions to ROIs
    rois_pred = pred_to_rois(loc, min_length=1)
    # Define the folder to save predicted ROIs
    rois_folder = os.path.join(ouptut_dir, "ROIs_pred")
    # Extract the frame name from the path
    frame_name = frame.split("/")[-1].split(".")[0]
    # Save predicted ROIs to the folder
    save_rois_to_folder(rois_pred, rois_folder, frame_name=frame_name)

    # Get the image from the list_comp folder
    imgs = os.listdir(os.path.join(ouptut_dir, "list_comp"))
    imgs.sort()
    img_path = os.path.join(ouptut_dir, "list_comp", imgs[0])
    # Get the ROI file from the ROIs_pred folder
    roi_path = os.path.join(rois_folder, os.listdir(rois_folder)[0])
    # Create a temporary folder for visualization
    os.makedirs(os.path.join(ouptut_dir, "viz_temp"), exist_ok=True)
    viz_temp = os.path.join(ouptut_dir, "viz_temp")
    # Visualize the predicted ROIs on the image
    visualize_roi(img_path, roi_path, viz_temp)

    # Visualize the ground truth ROIs on the image with predicted ROIs
    img_path = os.path.join(ouptut_dir, viz_temp, os.listdir(viz_temp)[0])
    os.makedirs(os.path.join(ouptut_dir, "comparison"), exist_ok=True)
    visualize_roi(
        img_path, roi_frame, os.path.join(ouptut_dir, "comparison"), color="blue"
    )

    # Create directories for final outputs
    os.makedirs(os.path.join(ouptut_dir, "test_def"), exist_ok=True)
    os.makedirs(os.path.join(ouptut_dir, "test_def", "ROIs_pred_def"), exist_ok=True)
    os.makedirs(os.path.join(ouptut_dir, "test_def", "1st_viz_pred"), exist_ok=True)
    os.makedirs(os.path.join(ouptut_dir, "test_def", "masks_def"), exist_ok=True)

    # Copy predicted ROIs, visualizations, and masks to the final output directories
    shutil.copy(
        roi_path,
        os.path.join(ouptut_dir, "test_def", "ROIs_pred_def"),
    )
    shutil.copy(
        os.path.join(viz_temp, os.listdir(viz_temp)[0]),
        os.path.join(ouptut_dir, "test_def", "1st_viz_pred"),
    )
    shutil.copy(
        os.path.join(
            ouptut_dir, "masks_frame", os.listdir(ouptut_dir + "/masks_frame")[0]
        ),
        os.path.join(ouptut_dir, "test_def", "masks_def"),
    )

    # Clean up temporary directories
    shutil.rmtree(os.path.join(ouptut_dir, "list_comp"))
    shutil.rmtree(os.path.join(ouptut_dir, "ROIs_pred"))
    shutil.rmtree(os.path.join(ouptut_dir, "viz_temp"))
    shutil.rmtree(os.path.join(caller_path, "temp_dataset"))
    shutil.rmtree(os.path.join(ouptut_dir, "list_sep"))
    shutil.rmtree(os.path.join(ouptut_dir, "masks_frame"))


# Example usage

# comp_model_frame(
#    "/home/gbouland/warm/tests/model_crop/dataset/test/test_x/001_frame_crop.png",
#    "/home/gbouland/warm/tests/model_crop/",
#    "/home/gbouland/warm/tests/model_crop/dataset/test/test_y/001_masks_crop.zip",
# )
# comp_model_frame(
#    "/home/gbouland/warm/tests/model_crop/dataset/test/test_x/002_frame_crop.png",
#    "/home/gbouland/warm/tests/model_crop/",
#    "/home/gbouland/warm/tests/model_crop/dataset/test/test_y/002_masks_crop.zip",
# )


def comp_model(model_path, train=False):
    """Compare the model with the ground truth. This functions takes a test set and a model path, and compares the model prediction with the ground truth."""
    if train:
        set = "train"
    else:
        set = "test"
    caller_path = os.path.dirname(os.path.abspath(__file__))
    # Test set folder
    test_set_folder = sorted(
        os.listdir(os.path.join(model_path, "dataset", f"{set}", f"{set}_x"))
    )
    print(test_set_folder)
    # Ground truth folder
    gt_folder = sorted(
        os.listdir(os.path.join(model_path, "dataset", f"{set}", f"{set}_y"))
    )
    print(gt_folder)
    # Output folder
    output_dir = os.path.join(caller_path, "output")
    # Clean it if it already exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

    for img, roi in zip(test_set_folder, gt_folder):
        print(f"Comparing {img} with {roi}")
        # Paths to the images and ROIs
        img_path = os.path.join(model_path, "dataset", f"{set}", f"{set}_x", img)
        roi_path = os.path.join(model_path, "dataset", f"{set}", f"{set}_y", roi)
        # Compare the model with the ground truth
        comp_model_frame(img_path, model_path, roi_path)


# Example usage

# comp_model("/home/gbouland/warm/tests/model_crop/")

# on a less accurate model
comp_model("/home/gbouland/warm/model_test/model_slides/", train=True)
