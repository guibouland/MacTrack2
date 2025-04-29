# MacTrack2

Derived from the work by [Axel de Montgolfier](https://github.com/Axeldmont/) during his time at the LPHI lab at the University of Montpellier. Our work aims at simplifying its use by adding different scripts. For instance, a `gettingstarted` file in the `mactrack` folder is here to help you with the analysis of your videos, based that we provide in the `examples` folder. You can also create your own model by running the `quickstart.py` file. Make sure to careffuly read the documentation of these two files. You can find them either in the files or in the website available [here](https://guibouland.github.io/MacTrack2/).

The goal of this project is then to accurately segment the macrophages. This segmentation will allow us to superimpose it on the green channel video to analyse the calcium flashes of the macrophages we have tracked. We then can retrieve informations on each macrophages conditionnally to the segmentation (such as amplitude of flashes, intensity...) without being hindered by the noise we often encounter in microscopic images.

## Installation

As my internship was following his work, I had to be acostumed to what he did during his time at LPHI. This repository consists of upgrades of the original work available via this [link](https://github.com/Axeldmont/Stage-LPHI-2024). We recommend you to clone this repository more than the other, as we worked on improving it.

```bash
git clone https://github.com/guibouland/MacTrack2.git
```

First, the packages you need in order to run this project are available in the `requirements.txt` file. For the `numena` library, you need to add this class in the  `/home/gbouland/micromamba/envs/sam-env/lib/python3.12/site-packages/numena/io/json.py` file (or wherever your *numena* module files is located). If you haven't set up an environment, find out where your `site-packages` folder is stored and add the class to the above file.

```python
class Serializable(ABC):
    """Python Interface to export Python objects to JSON format.

    The child class must implement 'dumps' property.
    """

    @abstractmethod
    def dumps(self) -> dict:
        """Property to generate the JSON formatted data of the current instance."""
        pass
```

Next, as Axel mentionned, your `input` folder needs to look like this:

```
input/yourdatafolder/
  ├── dataset
  ├── models
  ├── results
  ├── vert
      ├── frames #(empty)
      └── greenchannelvideo.mp4
  └── redchannelvideo.mp4
```

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

## Materials and Methods

First, all the videos and frames we used for analysis and segmentation were taken using a spinning disk confocal microscope, which illuminates macrophages in red and calcium flashes in green, thanks to a zebrafish transgenic lineage. We cut the caudal fin fold of a zebrafish in order to study if there is a correlation between the macrophage polarization and calcium flashes.

* [ ] Link to an ImageJ (Fiji) tuto to hand-cut frames.
* [ ] update readme fully
* [ ] update requirments
