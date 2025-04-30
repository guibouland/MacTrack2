# MacTrack2's input folders

## Introduction

As you may have seen if you already looked up to the the two input folders (input_model and input_tracking), they are almost similar. It's because they are copies. We decided to provide you two separate folders to help you with the two main processes you can do with this project:

* Model building, training and testing
* Tracking: Segmentation and analysis of a video using a model

You can use them as examples. The module we mostly use in this project, `kartezio`, is quite restrictive when it comes to input formats. Hence, we will try to make it easier for you to understand.

## Input folders

### Tracking

The structure of the input_tracking is as follows :

```
input_tracking/
  ├── dataset
  ├── models
  ├── vert
      ├── frames #(empty)
      └── greenchannelvideo.avi
  └── redchannelvideo.avi
```

### Model building

The structure of the input_tracking is as follows :

```
input_model/
  ├── dataset
  ├── models
```

There is no longer the videos as they are not necessary to create a model.

## Contents

### Dataset

The `dataset` folder is arranged as follows :

```
dataset
├── test
    ├── test_x
    └── test_y
├── train
    ├── train_x
    └── train_y
├── dataset.csv
└── META.json
```

In order for `Kartezio` to function properly, this format is required. Without this structure, you will end up with an error.

We will now make a description of the contents of each subfolders. The `train` folder contains the images you selected in order to train your model. For instance in the example we provided, there are 25 microscopic images in the `train_x` folder. In the `train_y` folder, there is the different groundtruth masks that we made by hand using ImageJ (see [Materials and Methods](../README.md#materials-and-methods)). This training folder will be the same in the `input_tracking` or `input_model`, as it is only used for structure in the tracking process.
The test folder, however, will change depending on what you do. If you want to test the quality of your model (e.g. input_model folder), you will have to segment a few more images and store them as you did for the training set. But, and that's where a downside of kartezio resides, if you want to track and segment a video, the frames of your video will be stored replacing the test images that you used for model testing. That is why we provided two folder examples and recommend you to do the same (by copying them for instance). Store your model folders well and keep track of them.

The dataset.csv and META.json are also here for kartezio to read correctly the folder as the input folder. If you want to create your own model, either by retraining the one we provided or by creating your own dataset, you can do it following the [quickstart.py](../quickstart.py) file

### Models

The `models` folder contains a hash-type named folder with two json files inside:

* `elite.json` : a file containing the actual pipeline of the model
* `history.json` : a file containing all the history (e.g. the generations) of the training of the model.

### Specificities for tracking







As you may have seen, an `examples/input` folder already exists in this repository. It is an sample input folder to help you understand how it should look and what to put in it.

Now let's talk about what's inside of these folders.

---

The `dataset` folder is arranged as follows :

```
dataset
├── test
    ├── test_x
    └── test_y
├── train
    ├── train_x
    └── train_y
├── dataset.csv
└── META.json
```

The `train` folder consists of `train_x` which is a folder containing all the frames that served to train the model. They must be from the red channel (so macrophages). The `train_y` folder contains the "masks". Each frame in the `train_x` folder must be hand-cut in the ImageJ program. You must add "Regions of Interest" on each frame and then save it as a `.zip` file containing all the ROIs in a single frame. You must do it for all frames in the `train_x` folder. Thanks to the `kartezio` module and the methods it is using, you don't need a lot of frame to make a good `train` dataset. For instance, Axel used only 26 frames, which is a very small number for a learning set.

Then comes the `test` folder. You don't have to worry about the `test_x` folder, it will be added when you run the `gettingstarted_example` file. It contains the frames of your red channel video. The `test_y` is a bit special. It is only here for structure. In fact, the one we provided in the `examples/imput` folder consists of empty `.zip` files. The number depends on the length of your video (number of frames). The `Set_up/empty_zip.py` helps you create these files.

The `dataset.csv` file is a summary of the different paths of your dataset. It is possible to make it by running the `dataset_csv.py` file. Finally, the `META.json` file is linked to the `dataset.csv` file as you can see input and label. Input is an image with format hsv and label are ROI files with format polygon (this `META.json` file was made to match functions from the kartezio library).

---

The `models` folder consists of json files that characterize the model obtained from the `train_model.py` file in the `Set_up` folder. To set-up your model, I advice you to do it first and to add a few frames in the `test` folder (before you start segmenting your videos, you may delete them later on place them in a different folder). You need to hand-cut these frames as it was done in the `train` folder.

---

The `results` folder contains the performances of the model in the `results.csv` file that is obtained by the `eval_models.py` file after initializing your model. It has been tested on 6 additional hand-cut frames.

---

The `vert` folder contains a `frames` folder that is at first empty. You must place your green channel video in the `vert` folder. By running the `extract_frames.py` file in the `Set_up` folder (by correctly replacing the path of your green channel video), the `frames` folder will be filled with the frames of your green channel video.

Finally, you must put you red channel video in the `input/yourdatafolder/` folder.

---

You can execute the `convert.py` file in the `Set_up` folder to convert AVI files into MP4 as AVI is the preferred format for video extraction from ImageJ (as Python doesn't work well with 16-bit file formats such as TIFF, while MP4, an 8-bit format, is more compatible).

---

The `input` subfolder (in the `examples` folder) contains a full, ready to use, example dataset that you can use to execute Axel's **Mactrack** by running the `gettingstarted_example` file in the `mactrack` folder.

## TODO

* [ ] Link to an ImageJ (Fiji) tuto to hand-cut frames.
* [ ] explain how we create datasets (polygon)
* [ ]
