Macrophage Tracking
===================

This page will help you get started with MacTrack2 and the analysis of macrophage videos.

Imports
-------

.. code-block:: python

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

Setup
-----

We need the path to the folder you will use as input, containing:

- The pretrained model
- The dataset used for training
- The example video for tracking and analysis

.. code-block:: python

    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(current_dir, "input_tracking")
    video_path = os.path.join(input_folder, "redchannel.avi")
    video_path_v = os.path.join(input_folder, r"vert", "greenchannel.avi")

If your video is in ``.avi`` format (as is often the case with microscopic videos), you can convert it to ``.mp4``:

.. code-block:: python

    if video_path.endswith(".avi"):
        convert_avi_to_mp4(video_path)
        video_path = video_path.replace(".avi", ".mp4")

You can do the same for the green channel video:
.. code-block:: python

    if video_path_v.endswith(".avi"):
        convert_avi_to_mp4(video_path_v)
        video_path_v = video_path_v.replace(".avi", ".mp4")

.. note::

    If you already have a `mp4` video, you can skip this step and put directly the path to the `mp4` video in the `video_path` variable.

Now, your video is a ``.mp4`` file and can be used in the pipeline.

.. code-block:: python

    n = get_frame_count(video_path)  # Number of frames in the initial video
    p = 10  # Minimal number of frames in which a macrophage must appear to be tracked

Frame Extraction
----------------

We will cut the video into frames and store them in ``input_folder``.

- Red channel frames: ``input_folder/dataset/test/test_x``
- Green channel frames: ``input_folder/vert/frames``


.. note::

    We recommand you to store the frames that served for model building carefully in another folder, as the tracking will cause changes in the dataset (see :doc:`quickstart` for more details). That is why we used ``input_tracking`` as the input folder and not ``input_model``.

.. code-block:: python

    frame = inputconfig(input_folder)

Cleanup
-------

Delete the ``list_sep`` and ``list_comp`` folders if they already exist to avoid inconsistencies in frame count:

.. code-block:: python

    if os.path.exists("output/list_sep"):
        shutil.rmtree("output/list_sep")
    if os.path.exists("output/list_comp"):
        shutil.rmtree("output/list_comp")

You can add a '**#**' if you want to keep them.

Dataset structure
-----------------
The ``inputconfig`` function cut both videos (red ans green channels) in frames stored in the ``test_y`` and ``vert/frames`` folders. The ``kartezio`` package has special needs to properly function. The ``test_x`` (red channel frames) and ``test_y`` folders must have the same length with the latter containing masks (in a zip format). However, it does not check the contents inside those files, so we will artificially create empty zip files in the ``test_y`` folder.

.. code-block:: python

    testy_folder = os.path.join(input_folder, "dataset/test/test_y/")
    empty_dataset_testy_zip(testy_folder=testy_folder, video_path=video_path)

It also needs a csv file that sums up the contents of the dataset.

.. code-block:: python

    create_dataset_csv(
        os.path.join(input_folder, r"dataset"),
        os.path.join(input_folder, "dataset", "dataset.csv"),
    )

Segmentation
------------

We begin tracking macrophages in the red channel video. This function:

- Creates an ``output`` folder
- Generates ``list_comp``: full-frame segmentations subfolder
- Generates ``list_sep``: individual macrophages per frame subfolder

.. code-block:: python

    locate(input_folder)

Then we load all the images into memory to accelerate further processing:

.. code-block:: python

    output_path = os.path.join(current_dir, r"output")
    image_storage = segmentation(os.path.join(output_path, "list_sep"))
    image_storage.load_images()

Defusion
--------

This step separates merged macrophages, as nearby cells might be detected as a single object.

Creates ``output/list_def`` containing the corrected segmentation:

.. code-block:: python

    image_storage = defuse(n, image_storage)
    image_storage = invdefuse(n, image_storage)

Tracking
--------

Track all macrophages across frames. Only keep those present in more than ``p`` frames.

.. code-block:: python

    track(n, threshold_iou=0.5, image_storage=image_storage)
    supprimer_petit(p)

Video Generation
----------------

Generate two videos showing tracking results:

- ``result.mp4``: red channel
- ``resultv.mp4``: green channel

Stored in the ``output`` folder.

.. code-block:: python

    result(input_folder)
    video()

Optional Cleanup
----------------

Free up disk space by removing intermediate folders. Comment out the lines if you want to keep them:

.. code-block:: python

    shutil.rmtree("output/list_def")
    shutil.rmtree("output/list_sep")
    shutil.rmtree("output/result")
    shutil.rmtree("output/resultv")

Create Output Folders
---------------------

.. code-block:: python

    if not os.path.exists("output/data"):
        os.makedirs("output/data")
    if not os.path.exists("output/plot"):
        os.makedirs("output/plot")

Feature Extraction
------------------

Extract and store features in DataFrames:

.. code-block:: python

    intmed = intensitymed(n, frame, input_folder)  # Intensity of macrophages
    dis = distance(n)  # Distance to the right border
    siz = size(n)  # Macrophage size
    per = perimeter(n)  # Macrophage perimeter

Aggregate results in a recap:

.. code-block:: python

    recap = aggregate(dis, intmed, siz, per)  # Summary of all features per macrophage

Conclusion
----------

You now have:

- Tracked macrophages through time
- Segmented images and result videos
- DataFrames of physical and intensity metrics
- Aggregated summaries ready for analysis
