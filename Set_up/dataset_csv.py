import os
import csv
import json


def create_dataset_csv(input_folder, output_csv):
    train_x_folder = os.path.join(input_folder, "train/train_x")
    train_y_folder = os.path.join(input_folder, "train/train_y")
    test_x_folder = os.path.join(input_folder, "test/test_x")
    test_y_folder = os.path.join(input_folder, "test/test_y")

    with open(output_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["input", "label", "set"])

        # Process training data
        train_x_files = sorted(
            [f for f in os.listdir(train_x_folder) if f.endswith((".png", ".jpg"))]
        )
        train_y_files = sorted(
            [f for f in os.listdir(train_y_folder) if f.endswith(".zip")]
        )

        for x_file, y_file in zip(train_x_files, train_y_files):
            writer.writerow(
                [
                    os.path.join("train/train_x", x_file),
                    os.path.join("train/train_y", y_file),
                    "training",
                ]
            )

        # Process testing data
        test_x_files = sorted(
            [f for f in os.listdir(test_x_folder) if f.endswith((".png", ".jpg"))]
        )
        test_y_files = sorted(
            [f for f in os.listdir(test_y_folder) if f.endswith(".zip")]
        )

        for x_file, y_file in zip(test_x_files, test_y_files):
            writer.writerow(
                [
                    os.path.join("test/test_x", x_file),
                    os.path.join("test/test_y", y_file),
                    "testing",
                ]
            )


# Example usage
input_folder = "/home/gbouland/Stage-LPHI-2024/input/norma/dataset"
output_csv = "/home/gbouland/Stage-LPHI-2024/input/norma/dataset/dataset.csv"
create_dataset_csv(input_folder, output_csv)


def create_meta_file(meta_path):
    """Create a META.json file for 'dataset' structure.

    Args:
        meta_path (str): Path to the META.json file to be created.
    """

    # Content of the JSON file
    meta_data = {
        "name": "Macrophage",
        "scale": 1.0,
        "label_name": "macrophage",
        "mode": "dataframe",
        "input": {"type": "image", "format": "hsv"},
        "label": {"type": "roi", "format": "polygon"},
    }

    # Create the JSON file with the content in it
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=4)
