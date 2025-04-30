import os
from moviepy.editor import VideoFileClip


def convert_avi_to_mp4(avi_file):
    """
    Converts an AVI video file to MP4 format using moviepy.

    Parameters:
        avi_file (str): Path to the input AVI file.

    Returns:
        str: Path to the generated MP4 file.
    """
    if not avi_file.lower().endswith(".avi"):
        raise ValueError("Input file must be an AVI file.")

    clip = VideoFileClip(avi_file)
    mp4_file = avi_file.replace(".avi", ".mp4")
    clip.write_videofile(mp4_file)

    return mp4_file


def convert_all_avi_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".avi"):
                avi_file_path = os.path.join(root, file_name)
                convert_avi_to_mp4(avi_file_path)


# Delete avi files in folder and subfolders
def delete_avi_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".avi"):
                avi_file_path = os.path.join(root, file_name)
                os.remove(avi_file_path)
