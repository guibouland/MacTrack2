# Post processing for Mactrack2 segmentation
import os
import cv2
import numpy as np
import pandas as pd
import inspect
import shutil


def merge_two(macro1, macro2):
    """Merge the segmentation results of Mactrack2.

    As sometimes the segmentation loses one macrophage, it is asigned with another ID. But we want to renconstruct the full temporal series of the macrophage, so we need to merge the IDs.
    We assume that you have checked the video so that the macrophages you are willing to merge are the same.

    We can encounter differnet cases:
        #. If for instance, macro_1 is tracked during the first 4 frames, and then it is lost for 1 frame, and then it is tracked again as macro_12. So we have 1 empty frame -> either full black image or copy the last one.
        #. Same but instead of having a missing one, we have a doubled one. either choose one of the two or try to merge the rois
        # Two distinct for the first few frames come in contact and merge into one : Double merge?

    Args:
        macro1 (int): Number of the first macrophage
        macro2 (int): Number of the second macrophage to be merged to the first one
    """

    print(f"\n\n[Merging] macrophage_{macro1} and macrophage_{macro2}\n")
    called_path = os.path.dirname(os.path.abspath(inspect.stack()[-1].filename))
    output = os.path.join(called_path, "output")
    list_track = os.path.join(output, "list_track")

    macro1_folder = os.path.join(list_track, str("macrophage_" + str(macro1)))
    macro2_folder = os.path.join(list_track, str("macrophage_" + str(macro2)))

    # contents
    contents1 = sorted(os.listdir(macro1_folder), key=lambda x: int(x.split("_")[0]))
    contents2 = sorted(os.listdir(macro2_folder), key=lambda x: int(x.split("_")[0]))

    # dict with frame number as key and file name as value
    frames1 = {int(f.split("_")[0]): f for f in contents1}
    frames2 = {int(f.split("_")[0]): f for f in contents2}

    all_frame_indices = sorted(set(frames1.keys()) | set(frames2.keys()))

    # full expected range of frames
    full_range = list(range(min(all_frame_indices), max(all_frame_indices) + 1))

    # Reference image for the size
    ref_img_path = os.path.join(macro1_folder, contents1[0])
    ref_img = cv2.imread(ref_img_path, cv2.IMREAD_UNCHANGED)
    height, width = ref_img.shape[:2]
    missing = []
    dup = []
    for idx in full_range:
        in1 = idx in frames1
        in2 = idx in frames2
        if in1 and in2:
            print(
                f"[Duplicate] Frame {idx}: we keep {frames1[idx]} and we remove {frames2[idx]}"
            )
            dup.append(idx)
            os.remove(os.path.join(macro2_folder, frames2[idx]))
        elif in2:
            # Move to the first folder
            src = os.path.join(macro2_folder, frames2[idx])
            dst = os.path.join(macro1_folder, frames2[idx])
            print(f"[Moving] {src} → {dst}")
            os.rename(src, dst)
        elif not in1 and not in2:
            # Missing frame → create a black image
            black_img = np.zeros((height, width), dtype=ref_img.dtype)
            new_filename = f"{idx}_0.png"
            dst = os.path.join(macro1_folder, new_filename)
            print(f"[Missing] Frame {idx} → Black frame: {dst}")
            missing.append(idx)
            cv2.imwrite(dst, black_img)

    # Remove the second folder
    print(f"[Removing] {macro2_folder} folder\n\n")
    os.rmdir(macro2_folder)
    return missing, dup


def merge(macro_list):
    """Merge the segmentation results of Mactrack2.

    As sometimes the segmentation loses one macrophage, it is asigned with another ID. But we want to renconstruct the full temporal series of the macrophage, so we need to merge the IDs.
    We assume that you have checked the video so that the macrophages you are willing to merge are the same.

    We can encounter differnet cases:
        #. If for instance, macro_1 is tracked during the first 4 frames, and then it is lost for 1 frame, and then it is tracked again as macro_12. So we have 1 empty frame -> either full black image or copy the last one.
        #. Same but instead of having a missing one, we have a doubled one. either choose one of the two or try to merge the rois
        # Two distinct for the first few frames come in contact and merge into one : Double merge?

    Args:
        macro_list (list): List of macrophages to be merged
    """
    called_path = os.path.dirname(os.path.abspath(inspect.stack()[-1].filename))
    output = os.path.join(called_path, "output")

    # Merge the first in the list with everyone else one by one
    for i in range(1, len(macro_list)):
        merge_two(macro_list[0], macro_list[i])


def add_part(macro, keep, missing):
    """Take a merged macrophage and change the newly added part (missing segmentation) to the one of the macrophage to be kept.
    Args:
        macro (int): Number of the macrophage to be modified
        keep_object (int): Number of the macrophage to be kept
        missing (list): List of the missing frames (from the merge_two function)
    """
    called_path = os.path.dirname(os.path.abspath(inspect.stack()[-1].filename))
    output = os.path.join(called_path, "output")
    list_track = os.path.join(output, "list_track")

    # Get the folder of the macrophage to be modified
    macro_folder = os.path.join(list_track, str("macrophage_" + str(macro)))
    keep_folder = os.path.join(list_track, str("macrophage_" + str(keep)))

    # Get the contents of the folders
    contents_macro = sorted(
        os.listdir(macro_folder), key=lambda x: int(x.split("_")[0])
    )
    contents_keep = sorted(os.listdir(keep_folder), key=lambda x: int(x.split("_")[0]))

    # dict with frame number as key and file name as value
    frames_macro = {int(f.split("_")[0]): f for f in contents_macro}
    frames_keep = {int(f.split("_")[0]): f for f in contents_keep}

    # Iterate over the missing frames and replace them with the corresponding frames from the keep object
    for idx in missing:
        if idx in frames_keep:
            src = os.path.join(keep_folder, frames_keep[idx])
            dst = os.path.join(macro_folder, frames_macro[idx])
            print(f"[Replacing] {dst} with {src}")
            shutil.copy(src, dst)


def merge_and_keep(macro_list, keep):
    """Merge the segmentation results of macrophages.

    Use if you have a macrophage that cross another one and you want to both add the segmentation of the latter to the first one and keep the second one.
    Args:
        macro_list (list): List of macrophages to be merged
        keep (list): List of macrophages to be kept.
    """
    called_path = os.path.dirname(os.path.abspath(inspect.stack()[-1].filename))
    output = os.path.join(called_path, "output")
    list_track = os.path.join(output, "list_track")
    # Create a copy of the macrophage folder to be kept
    for i in keep:
        keep_folder = os.path.join(list_track, str("macrophage_" + str(i)))
        keep_copy = os.path.join(list_track, str("macrophage_" + str(i) + "_copy"))
        os.makedirs(keep_copy, exist_ok=True)
        # Copy the contents of the keep folder to the copy folder
        for file in os.listdir(keep_folder):
            src = os.path.join(keep_folder, file)
            dst = os.path.join(keep_copy, file)
            shutil.copy(src, dst)

    keep_ = keep.copy()
    # macro list without the elements of keep
    clean_list = [x for x in macro_list if x not in keep]
    for i in range(1, len(clean_list)):
        print(i)
        print(len(clean_list))
        print(macro_list)
        if macro_list == []:
            break

        add = False
        start = clean_list[0]
        end = clean_list[i]

        idx_start = macro_list.index(start)
        idx_end = macro_list.index(end)
        print(idx_start < idx_end)
        # Check if the two elements are separated by a keep element
        if idx_start + 1 < idx_end:
            in_between = macro_list[idx_start + 1 : idx_end]
            add = True
        else:
            in_between = macro_list[idx_end + 1 : idx_start]
            add = False
        print(idx_start, idx_end, in_between)

        missing, dup = merge_two(start, end)

        if add:
            add_part(start, in_between[0], missing)

        # delete in_between and cleant_list[i] from macro_list
        macro_list.remove(end)
        for j in in_between:
            if j in keep:
                keep_.remove(j)
            if j in macro_list:
                macro_list.remove(j)
        print(macro_list)

    # Replacing the copied folders
    for i in keep:
        keep_copy = os.path.join(list_track, str("macrophage_" + str(i) + "_copy"))
        keep_folder = os.path.join(list_track, str("macrophage_" + str(i)))
        # Copy the contents of the copy folder to the keep folder
        for file in os.listdir(keep_copy):
            src = os.path.join(keep_copy, file)
            dst = os.path.join(keep_folder, file)
            shutil.copy(src, dst)
        print(f"[Replacing] {keep_folder} with {keep_copy}")
        # Remove the copied folder
        shutil.rmtree(keep_copy)
        print(f"[Removing] {keep_copy} folder")
