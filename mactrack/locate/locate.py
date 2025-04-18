import os
import cv2
import numpy as np
import shutil
import inspect
from kartezio.inference import ModelPool
from kartezio.fitness import FitnessIOU
from kartezio.dataset import read_dataset
from numena.image.basics import image_normalize
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from locate.temp_dataset import create_temporary_dataset


def filter_small_shapes(image, min_size):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_size:
            cv2.drawContours(image, [contour], 0, 0, -1)

    return image


def extract_objects(image, output_dir, filename):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_dir = os.path.join(output_dir, filename.split(".")[0])
    os.makedirs(image_dir, exist_ok=True)
    object_count = 0

    for i, contour in enumerate(contours):
        mask = np.zeros_like(image)
        cv2.drawContours(mask, [contour], 0, (255), -1)
        object_image = cv2.bitwise_and(image, image, mask=mask)
        cv2.imwrite(os.path.join(image_dir, f"object_{i}.png"), object_image)
        object_count += 1

    return object_count


def locate(input_folder):
    caller_frame = inspect.stack()[1]
    caller_file = caller_frame.filename
    caller_dir = os.path.dirname(os.path.abspath(caller_file))

    output_dir = os.path.join(caller_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_dir_masks = os.path.join(output_dir, "masks")
    if not os.path.exists(output_dir_masks):
        os.makedirs(output_dir_masks)

    # Number of frames in video
    n = len(os.listdir(os.path.join(input_folder, "dataset", "test", "test_x")))

    fitness = FitnessIOU()
    ensemble = ModelPool(
        os.path.join(input_folder, r"models"), fitness, regex="*/elite.json"
    ).to_ensemble()
    dataset = read_dataset(os.path.join(input_folder, r"dataset"), counting=True)
    p_test = ensemble.predict(dataset.test_x)

    for i in range(n):
        mask_list = [image_normalize(pi[0][i]["mask"]) for pi in p_test]
        heatmap = np.array(mask_list).mean(axis=0)
        heatmap_cp = (heatmap * 255.0).astype(np.uint8)

        cv2.imwrite(os.path.join(output_dir_masks, f"heatmap_test_{i}.png"), heatmap_cp)

    input_dir_masks = os.path.join(output_dir, "masks")
    output_dir_masks2 = os.path.join(output_dir, "list_comp")
    if not os.path.exists(output_dir_masks2):
        os.makedirs(output_dir_masks2)

    file_list = os.listdir(input_dir_masks)
    min_shape_size = 100

    for filename in file_list:
        input_path = os.path.join(input_dir_masks, filename)
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

        colored_image = 255 * (image > 0).astype("uint8")
        colored_image = filter_small_shapes(colored_image, min_shape_size)
        output_path = os.path.join(output_dir_masks2, filename)

        cv2.imwrite(output_path, colored_image)

    shutil.rmtree(output_dir_masks)

    input_dir_masks2 = output_dir_masks2
    output_dir_list = os.path.join(output_dir, "list_sep")
    if not os.path.exists(output_dir_list):
        os.makedirs(output_dir_list)

    file_list = os.listdir(input_dir_masks2)
    image_objects_count = {}

    for filename in file_list:
        input_path = os.path.join(input_dir_masks2, filename)
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        object_count = extract_objects(image, output_dir_list, filename)
        image_objects_count[filename] = object_count

    with open(os.path.join(output_dir, "summary.txt"), "w") as summary_file:
        for filename, count in image_objects_count.items():
            summary_file.write(f"{filename} : {count} objets\n")

    return p_test


def locate_frame(input_image_path, model_path):
    """Same function as locate but for a single frame. Used for model building or to test the performences of the model.

    Args:
        input_image_path (str): Path to the input image.
        model_path (str): Path to the model you want to use. Should contain a 'models' folder with the model in it and a dataset folder with the dataset used to train the model.

    Returns:
        list: p_test, the prediction on the input frame
    """
    caller_frame = inspect.stack()[1]
    caller_file = caller_frame.filename
    caller_dir = os.path.dirname(os.path.abspath(caller_file))

    output_dir = os.path.join(caller_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    output_dir_masks = os.path.join(output_dir, "masks_frame")
    if not os.path.exists(output_dir_masks):
        os.makedirs(output_dir_masks)

    fitness = FitnessIOU()
    ensemble = ModelPool(
        os.path.join(os.path.dirname(model_path), r"models"),
        fitness,
        regex="*/elite.json",
    ).to_ensemble()
    create_temporary_dataset(input_image_path, os.path.dirname(model_path))
    dataset = read_dataset(os.path.join(caller_dir, r"temp_dataset"), counting=True)

    p_test = ensemble.predict(dataset.test_x)

    mask_list = [image_normalize(pi[0][0]["mask"]) for pi in p_test]
    heatmap = np.array(mask_list).mean(axis=0)
    heatmap_cp = (heatmap * 255.0).astype(np.uint8)

    heatmap_filename = os.path.basename(input_image_path).split(".")[0] + "_heatmap.png"
    cv2.imwrite(os.path.join(output_dir_masks, heatmap_filename), heatmap_cp)

    output_dir_masks2 = os.path.join(output_dir, "list_comp")
    if not os.path.exists(output_dir_masks2):
        os.makedirs(output_dir_masks2)

    min_shape_size = 100
    input_path = os.path.join(output_dir_masks, heatmap_filename)
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    colored_image = 255 * (img > 0).astype("uint8")
    colored_image = filter_small_shapes(colored_image, min_shape_size)
    output_path = os.path.join(output_dir_masks2, heatmap_filename)
    cv2.imwrite(output_path, colored_image)

    output_dir_list = os.path.join(output_dir, "list_sep")
    if not os.path.exists(output_dir_list):
        os.makedirs(output_dir_list)

    object_count = extract_objects(colored_image, output_dir_list, heatmap_filename)

    with open(os.path.join(output_dir, "summary.txt"), "a") as summary_file:
        summary_file.write(f"{heatmap_filename} : {object_count} objets\n")

    return p_test
