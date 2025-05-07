from PIL import Image, ImageDraw
from read_roi import read_roi_zip, read_roi_file
import cv2
import numpy as np
import os
import sys
from roifile import ImagejRoi
import zipfile
import shutil
import inspect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from locate.locate import locate_frame


def visualize_roi(image_path, roi_path, output_folder, color="red"):
    """Visualize the region of interest (ROI) on an image without white borders.

    This function overlays the specified ROI on the given image and saves the
    resulting visualization to the specified output folder.

    :param str image_path: Path to the image file.
    :param str roi_path: Path to the ROI file. Supported formats are `.zip` and `.roi`.
    :param str output_folder: Path to the folder where the output image will be saved.
    :param str color: Outline color for the ROI. Defaults to "red".

    :raises ValueError: If the ROI file format is not supported.
    :raises ValueError: If the ROI type is not recognized.

    :returns: None
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


def pred_to_rois(pred, min_length):
    """
    Convert model predictions into Regions of Interest (ROIs).

    This function processes the output of the 'locate_frame' function, extracts contours
    from the masks, and generates ROIs for each contour. Each ROI is represented as a
    polygon with its coordinates.

    Parameters
    ----------
    pred : list
        A list of predictions from the model on a frame. Each element in the list is a
        tuple containing a list of masks and a score. The masks are expected to be
        binary arrays.
    min_length : int
        The minimum length of the contour to be considered a valid ROI. This helps
        filter out small artefacts or noise.

    Returns
    -------
    dict
        A dictionary where each key is a unique name for the ROI, and the value is a
        dictionary containing the following information:
            - type (str): The type of the ROI (e.g., "polygon").
            - x (list of float): The x-coordinates of the ROI's contour points.
            - y (list of float): The y-coordinates of the ROI's contour points.
            - n (int): The number of points in the contour.
            - width (int): Placeholder for width (currently set to 0).
            - name (str): The unique name of the ROI.
            - position (int): Placeholder for position (currently set to 0).
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


from roifile import ImagejRoi, ROI_TYPE


def create_polygon_roi(points, **kwargs):
    """
    Create an ImagejRoi object with the type set to POLYGON.

    Parameters:
    ----------
    points : list
        List of (x, y) coordinates for the polygon.
    kwargs : dict
        Additional arguments to pass to ImagejRoi.frompoints.

    Returns:
    -------
    ImagejRoi
        An ImagejRoi object with the type set to POLYGON.
    """
    roi = ImagejRoi.frompoints(points, **kwargs)
    roi.roitype = ROI_TYPE.POLYGON  # Override the ROI type to POLYGON
    return roi


def save_rois_to_folder(rois, folder_path, frame_name):
    """Save ROIs for each objects as .roi files in a zip file.

    Args:
        rois (dict): Dictionary containing ROIs.
        Each key is a unique name for the ROI and the value is a dictionary
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

                ij_roi = create_polygon_roi(points=np.column_stack((x, y)))
                ij_roi.name = name

                roi_path = os.path.join(folder_path, f"{name}.roi")
                ij_roi.tofile(roi_path)

                zipf.write(roi_path, arcname=f"{name}.roi")

                os.remove(roi_path)


def comp_model_frame(frame, model_path, roi_frame):
    """
    Create an image comparison between the model's predictions and the ground truth.

    This function processes a given frame using a specified model, generates predicted
    ROIs (Regions of Interest), and visualizes them alongside the ground truth ROIs.
    It is designed to compare the model's predictions with the ground truth after
    the model has been run. Note that if there are multiple models in the 'models'
    folder, the function will process all of them, resulting in multiple red outlines.
    It is recommended to keep only one model in the 'models' folder for accurate comparison.

    Parameters
    ----------
    frame : str
        Path to the frame image.
    model_path : str
        Path to the model folder. The folder must include the 'models' and 'dataset'
        subfolders, as well as the 'dataset.csv' and 'META.json' files.
    roi_frame : str
        Path to the ground truth ROI frame. This must be a .zip file containing the
        ROIs or a .roi file.

    Returns
    -------
        The function does not return any value. It generates visualizations and saves
        them in the appropriate directories.

    Notes
    -----
    - The function creates several temporary directories for intermediate outputs,
      which are cleaned up after processing.
    - The final outputs, including predicted ROIs, visualizations, and masks, are
      saved in the 'test_def' directory within the 'model_output' folder.
    - Ensure that the input paths are valid and the required files are present in
      the specified directories.
    """
    # Get the directory in which this function will be used
    called_path = os.path.dirname(os.path.abspath(inspect.stack()[-1].filename))
    print(called_path)
    # Define the output directory
    output_dir = os.path.join(called_path, "model_output")
    print(output_dir)
    # Locate objects in the frame using the model
    loc = locate_frame(frame, model_path, "model_output")
    # Convert model predictions to ROIs
    rois_pred = pred_to_rois(loc, min_length=1)
    # Define the folder to save predicted ROIs
    rois_folder = os.path.join(output_dir, "ROIs_pred")
    # Extract the frame name from the path
    frame_name = frame.split("/")[-1].split(".")[0]
    # Save predicted ROIs to the folder
    save_rois_to_folder(rois_pred, rois_folder, frame_name=frame_name)

    # Get the image from the list_comp folder
    imgs = os.listdir(os.path.join(output_dir, "list_comp"))
    imgs.sort()
    img_path = os.path.join(output_dir, "list_comp", imgs[0])
    # Get the ROI file from the ROIs_pred folder
    roi_path = os.path.join(rois_folder, os.listdir(rois_folder)[0])
    # Create a temporary folder for visualization
    os.makedirs(os.path.join(output_dir, "viz_temp"), exist_ok=True)
    viz_temp = os.path.join(output_dir, "viz_temp")
    # Visualize the predicted ROIs on the image
    visualize_roi(img_path, roi_path, viz_temp)

    # Visualize the ground truth ROIs on the image with predicted ROIs
    img_path = os.path.join(output_dir, viz_temp, os.listdir(viz_temp)[0])
    os.makedirs(os.path.join(output_dir, "comparison"), exist_ok=True)
    visualize_roi(
        img_path, roi_frame, os.path.join(output_dir, "comparison"), color="blue"
    )

    # Create directories for final outputs
    os.makedirs(os.path.join(output_dir, "test_def"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "test_def", "ROIs_pred_def"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "test_def", "1st_viz_pred"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "test_def", "masks_def"), exist_ok=True)

    # Copy predicted ROIs, visualizations, and masks to the final output directories
    shutil.copy(
        roi_path,
        os.path.join(output_dir, "test_def", "ROIs_pred_def"),
    )
    shutil.copy(
        os.path.join(viz_temp, os.listdir(viz_temp)[0]),
        os.path.join(output_dir, "test_def", "1st_viz_pred"),
    )
    shutil.copy(
        os.path.join(
            output_dir, "masks_frame", os.listdir(output_dir + "/masks_frame")[0]
        ),
        os.path.join(output_dir, "test_def", "masks_def"),
    )

    # Clean up temporary directories
    shutil.rmtree(os.path.join(output_dir, "list_comp"))
    shutil.rmtree(os.path.join(output_dir, "ROIs_pred"))
    shutil.rmtree(os.path.join(output_dir, "viz_temp"))
    shutil.rmtree(os.path.join(called_path, "temp_dataset"))
    shutil.rmtree(os.path.join(output_dir, "list_sep"))
    shutil.rmtree(os.path.join(output_dir, "masks_frame"))


def comp_model(model_path, train=False):
    """
    comp_model(model_path, train=False)
    Compare the model predictions with the ground truth.

    This function takes a test or training dataset and a model path, then compares
    the model's predictions with the ground truth data. The comparison results are
    stored in an output directory.

    Parameters
    ----------
    model_path : str
        The path to the directory containing the model and dataset.
    train : bool, optional
        If True, the training dataset is used for comparison. If False, the test
        dataset is used. Default is False.

    Raises
    ------
    FileNotFoundError
        If the specified dataset or model path does not exist.
    PermissionError
        If there are insufficient permissions to access or modify the output directory.

    Notes
    -----
    - The function assumes a specific directory structure under `model_path`:
      - `dataset/train/train_x` and `dataset/train/train_y` for training data.
      - `dataset/test/test_x` and `dataset/test/test_y` for test data.
    - The output directory is cleared and recreated for each function call.

    See Also
    --------
    comp_model_frame : Function used to compare individual frames.
    """
    if train:
        set = "train"
    else:
        set = "test"
    caller_path = os.path.dirname(os.path.abspath(inspect.stack()[1].filename))
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
    output_dir = os.path.join(caller_path, "model_output")
    # Clean it if it already exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    else:
        os.makedirs(output_dir, exist_ok=True)

    for img, roi in zip(test_set_folder, gt_folder):
        print(f"Comparing {img} with {roi}")
        # Paths to the images and ROIs
        img_path = os.path.join(model_path, "dataset", f"{set}", f"{set}_x", img)
        roi_path = os.path.join(model_path, "dataset", f"{set}", f"{set}_y", roi)
        # Compare the model with the ground truth
        comp_model_frame(img_path, model_path, roi_path)
