class VideoFrames:
    """
    A class to hold video frames and their corresponding visualizations.

    Parameters
    ----------
    frames : list
        A list to store the video frames.
    frames_v : list
        A list to store the visualizations of the video frames.

    Methods
    -------
    add_frame(frame)
        Adds a video frame to the ``frames`` list.
    add_frame_v(frame)
        Adds a video frame from the green channel video to the ``frames_v`` list
    """
    def __init__(self):
        """
        Initializes the VideoFrames class with empty lists for ``frames`` and ``frames_v``.
        """
        self.frames = []
        self.frames_v = []

    def add_frame(self, frame):
        """
        Adds a video frame to the ``frames`` list.

        Parameters
        ----------
        frame : object
            The video frame to be added.
        """
        self.frames.append(frame)

    def add_frame_v(self, frame):
        """
        Adds a video frame from the green channel video to the ``frames_v`` list.
        
        Parameters
        ----------
        frame : object
            The green channel video frame to be added.
        """
        self.frames_v.append(frame)
