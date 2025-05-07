# MacTrack2

Derived from the work by [Axel de Montgolfier](https://github.com/Axeldmont/) during his time at the LPHI lab at the University of Montpellier. Our work aims at simplifying its use by adding different scripts. For instance, a `gettingstarted` file is here to help you with the analysis of your videos, based that we provide in the `examples` folder. You can also create your own model by running the `quickstart.py` file. Make sure to careffuly read the documentation of these two files. You can find them either in the files or in the website available [here](https://guibouland.github.io/MacTrack2/).

The goal of this project is then to accurately segment the macrophages. This segmentation will allow us to superimpose it on the green channel video to analyse the calcium flashes of the macrophages we have tracked. We then can retrieve informations on each macrophages conditionnally to the segmentation (such as amplitude of flashes, intensity...) without being hindered by the noise we often encounter in microscopic images.

## Installation

As my internship was following his work, I had to be acostumed to what he did during his time at LPHI. This repository consists of upgrades of the original work available via this [link](https://github.com/Axeldmont/Stage-LPHI-2024). We recommend you to clone this repository more than the other, as we worked on improving it.

```bash
git clone https://github.com/guibouland/MacTrack2.git
```

You can then download the packages in `requirements.txt`. We recommand you to create an environment.

If you use (micro)mamba :

```bash
micromamba create -n mactrack-env python=3.12 # Create virtual env using python 3.12
micromamba activate mactrack-env # Activate the environment
cd MacTrack2 # cd into the repository containing the requirements.txt file
pip install -r requirements.txt # Installing depedencies
```

If you use the `venv` (virtual env) Python module :

```bash
python3.12 -m venv mactrack-env # Create virtual environment
source mactrack-env/bin/activate # Activation on Linux/macOS
mactrack-env\Scripts\activate # Activation on Windows
cd MacTrack2
pip install -r requirements.txt # Installing dependencies
```

You are now set to go. If you want to try the module we provide, a `gettingstarted` python file is available. It uses a pre-trained model provided in the `examples` folder. If you want to train your own model, the `quickstart.py` file helps you to do so.

## Create your own dataset and model

If you want more details on how to create your own datasets in order to create, train and test your own model, and run your model on other videos that the one we provided, we recommend you to read [this](./examples/README.md).

## Materials and Methods

First, all the videos and frames we used for analysis and segmentation were taken using a spinning disk confocal microscope, which illuminates macrophages in red and calcium flashes in green, thanks to a zebrafish transgenic lineage. We cut the caudal fin fold of a zebrafish in order to study if there is a correlation between the macrophage polarization and calcium flashes.

## Contributors

* [Guillaume Bouland](https://github.com/guibouland) : Intern at the LPHI lab in 2025
* [Axel de Montgolfier](https://github.com/Axeldmont/) : Intern at the LPHI lab in 2024

## Aknowledgement

This project was made using mainly the [kartezio](https://github.com/KevinCortacero/Kartezio) Python package developped by [Kévin Cortacero](https://github.com/KevinCortacero).

## TODO


* [x] update readme fully
* [ ] Materials and Methods, doc on fiji
