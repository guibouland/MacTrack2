import cv2


def get_frame_count(video_path):
    """
    Get the number of frames in a video file.
    Parameters:
        video_path (str): Path to the video file.
    Returns:
        frame_count (int): Number of frames in the video.
    """
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frame_count
