import os
import inspect
import shutil
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Set_up.empty_zip import empty_dataset_testy_zip_single_frame
from Set_up.dataset_csv import create_dataset_csv, create_meta_file


def create_temporary_dataset(imput_image_path, model_path):
    """Creates a temporary dataset for structural purposes in the execution of the locate_frame function.

    Args:
        imput_image_path (str): Path to the input image.
        model_path (str): Path to the model you want to use. Should contain a 'models' folder with the model in it and a dataset folder with the dataset used to train the model.
    """
    # Automatically determine the directory of the caller
    caller_frame = inspect.stack()[-1]
    caller_file = caller_frame.filename
    caller_dir = os.path.dirname(os.path.abspath(caller_file))

    # Create the temp_dataset directory in the caller's directory
    temp_dataset_dir = os.path.join(caller_dir, "temp_dataset")
    if not os.path.exists(temp_dataset_dir):
        os.makedirs(temp_dataset_dir)
    else:
        # Clear the directory if it already exists
        for file in os.listdir(temp_dataset_dir):
            file_path = os.path.join(temp_dataset_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    # Copy the training dataset
    train_set = os.path.join(model_path, "dataset", "train")
    shutil.copytree(
        train_set, os.path.join(temp_dataset_dir, "train"), dirs_exist_ok=True
    )

    # Create test directories and copy the input image
    os.makedirs(os.path.join(temp_dataset_dir, "test"), exist_ok=True)
    os.makedirs(os.path.join(temp_dataset_dir, "test", "test_x"), exist_ok=True)

    shutil.copy(imput_image_path, os.path.join(temp_dataset_dir, "test", "test_x"))
    empty_dataset_testy_zip_single_frame(
        os.path.join(temp_dataset_dir, "test", "test_y"), imput_image_path
    )

    # Generate dataset CSV and META.json
    create_dataset_csv(temp_dataset_dir, os.path.join(temp_dataset_dir, "dataset.csv"))
    create_meta_file(os.path.join(temp_dataset_dir, "META.json"))
