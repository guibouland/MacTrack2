MacTrack2's Input Folders Examples
==================================

Introduction
------------

As you may have seen if you already looked up the two input folders (`input_model` and `input_tracking`), they are almost identical — because they are copies. We decided to provide you with two separate folders to help you with the two main processes supported by this project:

- **Model building, training, and testing**
- **Tracking**: Segmentation and analysis of a video using a model

You can use them as examples. The module we primarily use in this project, `kartezio`, is quite restrictive regarding input formats. Hence, we aim to make it easier for you to understand.

Input Folders
-------------

Tracking
^^^^^^^^

The structure of the `input_tracking` folder is as follows:

::

    input_tracking/
      ├── dataset
      ├── models
      ├── vert
      │   ├── frames  # (empty)
      │   └── greenchannelvideo.avi
      └── redchannelvideo.avi

Model Building
^^^^^^^^^^^^^^

The structure of the `input_model` folder is as follows:

::

    input_model/
      ├── dataset
      ├── models

There are no videos here, as they are not necessary for model creation.

Contents
--------

Dataset
^^^^^^^

The `dataset` folder is organized as follows:

::

    dataset
    ├── test
    │   ├── test_x
    │   └── test_y
    ├── train
    │   ├── train_x
    │   └── train_y
    ├── dataset.csv
    └── META.json

In order for `kartezio` to function correctly, this structure is required. Without it, errors will occur.

We will now describe each subfolder:

- The `train` folder contains the images selected for model training.
  For instance, in the provided example, there are 25 microscopic images in `train_x`.
- The `train_y` folder contains corresponding ground truth masks, created manually using ImageJ (see the :ref:`Materials and Methods <mat_and_met>` section of the README).
- This training folder will remain the same in both `input_model` and `input_tracking`, as it is used for structure during tracking.

The `test` folder will change depending on your use case:

- For testing a model (i.e., in the `input_model` folder), segment a few images and store them just as with the training set.
- For tracking and video segmentation, the frames extracted from your video will replace the test images. This is a limitation of `kartezio`.

That is why we provide both folders and recommend creating your own by copying them. Be sure to store and track your model folders carefully.

- `dataset.csv` and `META.json` are also necessary for `kartezio` to properly interpret the input folder.

If you want to create your own model — by retraining the provided one or building from a new dataset — follow the steps in `quickstart.py`.

Models
^^^^^^

The `models` folder contains a hash-named directory with two JSON files:

- `elite.json`: Contains the final pipeline of the model
- `history.json`: Contains the training history (e.g., generations)

Specificities for Tracking
--------------------------

In the `input_tracking` folder, you will find:

- A **red channel video**
- A `vert/` folder containing:
  - A **green channel video**
  - An empty `frames/` folder

These are example videos for tracking. If you wish to segment your own video, **you must respect this structure**.

Both videos (red and green channels) originate from the same microscopic analysis, with channels separated using ImageJ. For more information, refer to the :ref:`Materials and Methods <mat_and_met>` section in the README.
