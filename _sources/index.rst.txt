Welcome to MacTrack2's documentation!
======================================

Derived from the work by `Axel de Montgolfier <https://github.com/Axeldmont/>`_ during his time at the LPHI lab at the University of Montpellier. Our work aims to simplify its use by adding various scripts. For instance, a ``gettingstarted`` file helps with the analysis of your videos, based on examples we provide in the ``examples`` folder. You can also create your own model by running the ``quickstart.py`` file. 

Make sure to carefully read the documentation for both files. You can find it either in the source files or on the website available `here <https://guibouland.github.io/MacTrack2/>`_.

The goal of this project is to **accurately segment macrophages**. This segmentation enables superimposing results on the green channel video to analyze calcium flashes of the tracked macrophages. This way, we can retrieve information about each macrophage — such as flash amplitude and intensity — without being hindered by the noise commonly present in microscopic images.

Installation
------------

As my internship followed Axel's work, I had to familiarize myself with his original project. This repository contains upgrades to the original work, available `here <https://github.com/Axeldmont/Stage-LPHI-2024>`_. We recommend cloning **this repository** as it includes various improvements.

Clone the repository:

.. code-block:: bash

    git clone https://github.com/guibouland/MacTrack2.git

You can then install the dependencies listed in ``requirements.txt``. We recommend creating a virtual environment.

If you use (micro)mamba:

.. code-block:: bash

    micromamba create -n mactrack-env python=3.12   # Create virtual env using Python 3.12
    micromamba activate mactrack-env                # Activate the environment
    cd MacTrack2                                    # Enter the project directory
    pip install -r requirements.txt                 # Install dependencies

If you use Python's `venv` module:

.. code-block:: bash

    python3.12 -m venv mactrack-env                  # Create virtual environment
    source mactrack-env/bin/activate                 # Activate on Linux/macOS
    mactrack-env\Scripts\activate                    # Activate on Windows
    cd MacTrack2
    pip install -r requirements.txt                  # Install dependencies

You're now ready to go!

To try the module we provide, run the ``gettingstarted`` file. It uses a pre-trained model found in the ``examples`` folder. If you want to train your own model, use ``quickstart.py``.

Create Your Own Dataset and Model
---------------------------------

For more details on how to create your own dataset, train and test a model, and apply it to videos beyond those provided, refer to the documentation available `here <./examples/README.md>`_.

.. mat_and_met:
Materials and Methods
---------------------

All videos and frames used for analysis and segmentation were acquired using a **spinning disk confocal microscope**. It illuminates **macrophages in red** and **calcium flashes in green**, using a **zebrafish transgenic lineage**.

We amputated the caudal fin fold of a zebrafish to study potential correlations between **macrophage polarization** and **calcium flashes**.

Contributors
------------

- `Guillaume Bouland <https://github.com/guibouland>`_: Intern at the LPHI lab in 2025
- `Axel de Montgolfier <https://github.com/Axeldmont/>`_: Intern at the LPHI lab in 2024

Acknowledgement
---------------

This project relies mainly on the `kartezio <https://github.com/KevinCortacero/Kartezio>`_ Python package, developed by `Kévin Cortacero <https://github.com/KevinCortacero>`_.



.. toctree::
    :maxdepth: 1
    :caption: Contents:
    
    index
    quickstart
    gettingstarted
    examples
    mactrack
