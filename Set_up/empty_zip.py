import os
import zipfile
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from Set_up.count import get_frame_count


def empty_dataset_testy_zip(testy_folder, video_path):
    """
    Function that creates empty zip files in the ``test_y`` folder. The number of zip files created matched the number of frmaes of the video file you provided.
    Parameters:
        testy_folder (str): Path to the testy folder.
        video_path (str): Path to the video file.
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
    Function that creates empty zip file in the ``test_y`` folder for a unique frame. The zip file created matched the name of the frame you provided.
    
    Parameters:
        testy_folder (str): Path to the testy folder.
        frame_path (str): Path to the frame file.
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
