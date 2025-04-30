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

For the `input_tracking` folder, there is the red channel video and the `vert` folder containing the green channel video and an empty `frames` folder. They are examples videos for tracking purposes. Note that if you want to segment your own video, you must respect the structure mentionned before.
The two videos (red and green channels) come from the same microscopic analysis. The channels were separated using ImageJ. You can refer yourself to the [Materials and Methods](../README.md#materials-and-methods) for more details.


## TODO

* [ ] Link to an ImageJ (Fiji) tuto to hand-cut frames.
* [ ] explain how we create datasets (polygon)
* [ ]
