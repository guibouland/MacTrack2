from mactrack.locate.locate import locate
from mactrack.locate.list_sep import segmentation
from mactrack.locate.defuse import defuse, invdefuse
from mactrack.track.track import track
from mactrack.video.inputconfig import inputconfig
from mactrack.video.result import video, result, videocomp
import os
from mactrack.analyse.intensity import intensity, intensitymed
from mactrack.analyse.distance import distance
from mactrack.analyse.size import size
from mactrack.analyse.perimeter import perimeter
from mactrack.analyse.recap import aggregate
import shutil
from mactrack.track.filtre import supprimer_petit

from Set_up.count import get_frame_count
from Set_up.convert import convert_avi_to_mp4
from Set_up.empty_zip import empty_dataset_testy_zip
from Set_up.dataset_csv import create_dataset_csv

# We need the path to the folder you will use as input, containing the pretrained model we provided as an example, the dataset used for training the model, and the example video we are going to track and analyse.
current_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(current_dir, "examples", "input_tracking")
video_path = os.path.join(input_folder, "redchannel.avi")
video_path_v = os.path.join(input_folder, r"vert", "greenchannel.avi")

# If your video, as it is often the case with microscopic videos, is in `avi` format, you can convert it to `mp4` format.
if video_path.endswith(".avi"):
    convert_avi_to_mp4(video_path)
    video_path = video_path.replace(".avi", ".mp4")

############################################
# Do the same for the green channel video
if video_path_v.endswith(".avi"):
    convert_avi_to_mp4(video_path_v)
    video_path_v = video_path_v.replace(".avi", ".mp4")

##############################################
# .. note:: If you already have a `mp4` video, you can skip this step and put directly the path to the `mp4` video in the `video_path` variable.


# Now, your video is a `mp4` file and you can use it in the package.
n = get_frame_count(video_path)  # Number of frame in the initial video
p = 10  # Minimal number of frame where you can track your macrophage, if it is present in less or equal p frames, it will not be tracked

# We will then cut the videos into frames and store them in the `input_folder` directory. The red channel frames will be stored in `input_folder/dataset/test/test_x`, and the green channel frames will be stored in `input_folder/vert/frames`. That is why we used the `input_tracking` folder as input, as the following function erase the contents inside the `dataset` folder, meaning that the frames that helped you build the model may be gone.

# That is why we recommend to either store the frames you used to build the model in a different folder, or to use a different folder as input, creating a copy of the one used to build the model.
frame = inputconfig(input_folder)


# Delete the list_sep and list_comp folder if they already exist (to not have a differnet size in the folder than the one you mentionned: 'n'). As the output folder is common to all the different inputs you can add :
if os.path.exists("output/list_sep"):
    shutil.rmtree("output/list_sep")
if os.path.exists("output/list_comp"):
    shutil.rmtree("output/list_comp")

# The package `kartezio` has special needs for the data's structure. In fact the *test_x* and *test_y* folders must be of the same size with the latter containing masks (in a zip format). However, it does not check the contents inside those files, so we will artificially create empty zip files in the `test_y` folder.
testy_folder = os.path.join(input_folder, "dataset/test/test_y/")
empty_dataset_testy_zip(testy_folder=testy_folder, video_path=video_path)

# `kartezio` also needs a csv file that sums up the contents of the dataset.
create_dataset_csv(
    os.path.join(input_folder, r"dataset"),
    os.path.join(input_folder, "dataset", "dataset.csv"),
)

#############################################################
# We can now begin the tracking of the macrophages in the red channel video. The following function will create a folder called `output` in the current directory, and inside it, two folders : `list_comp` and `list_sep`. The first one contains the segmentation of each frame, and the second one contains each object in separate picture file at each frame. They will have a role in the next steps of the tracking process.
locate(input_folder)


# This will save all the picture in a python class in order to accelerate the program
output_path = os.path.join(current_dir, r"output")
image_storage = segmentation(os.path.join(output_path, "list_sep"))
image_storage.load_images()


# This will prevent and separate the merging macrophage. In fact, two nearby macrophages can be detected as one object. This function will separate them and create a new folder called `list_def` in the `output` folder, containing the separated objects.
image_storage = defuse(n, image_storage)
image_storage = invdefuse(n, image_storage)
# Then, we obtain a "definitive" list of segmented macrophages, which is stored in the `output/list_def` folder. This list is used to track the macrophages in the next step.

# This will do the tracking of every macrophage and filter if you detect a macrophage on enough frame
track(n, threshold_iou=0.5, image_storage=image_storage)
supprimer_petit(p)

# This will create in the output folder two video which show the results of the tracking
result(input_folder)

# We finally can merge all the fully segmented frames in a single video. We will obtain two videos : `result.mp4` and `resultv.mp4`. The first one contains the tracking of the segmented macrophages on the red channel video, and the second one contains the tracking of the segmented macrophages on the green channel video. Both videos are stored in the `output` folder.
video()

# This is for deleting non necessary folder to liberate some place. You can add a '#' before the lines below if you want to keep the folders.
shutil.rmtree("output/list_def")
shutil.rmtree("output/list_sep")
shutil.rmtree("output/result")
shutil.rmtree("output/resultv")

# This is to create folder who will contain the data
if not os.path.exists("output/data"):
    os.makedirs("output/data")
if not os.path.exists("output/plot"):
    os.makedirs("output/plot")

# These will collect the data and stock them in dataframe
intmed = intensitymed(n, frame, input_folder)  # Data on the intensity of macrophage
dis = distance(n)  # data of distance to the right border
siz = size(n)  # data of the size of the macrophage
per = perimeter(n)  # data of the perimeter of the macrophage
recap = aggregate(
    dis, intmed, siz, per
)  # summary of each data for each macrophage in a movie
