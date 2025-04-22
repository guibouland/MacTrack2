import os
import zipfile
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from Set_up.count import get_frame_count


def empty_dataset_testy_zip(testy_folder, video_path):
    """
    Function that creates empty zip files.
    """
    folder_path = os.path.dirname(os.path.realpath(__file__))
    parent_folder = os.path.dirname(folder_path)
    testy_path = os.path.join(parent_folder, testy_folder)
    os.makedirs(testy_path, exist_ok=True)

    n = get_frame_count(video_path)

    # Create n empty zip files
    for i in range(n):
        zip_filename = os.path.join(testy_path, f"{i:03d}_masks.zip")
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            pass


# same but for a unique frame in the test_x folder and not a video
def empty_dataset_testy_zip_single_frame(testy_folder, frame_path):
    """
    Function that creates empty zip file.
    """
    folder_path = os.path.dirname(os.path.realpath(__file__))
    parent_folder = os.path.dirname(folder_path)
    testy_path = os.path.join(parent_folder, testy_folder)
    os.makedirs(testy_path, exist_ok=True)

    # get the name of the frame
    frame_name = os.path.basename(frame_path)
    # Create a zip file with the name of the frame
    zip_filename = os.path.join(testy_path, f"{frame_name}_masks.zip")
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        pass
