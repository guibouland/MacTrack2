import os
import cv2
import numpy as np
from scipy.sparse import csr_matrix


class segmentation:
    """
    Class to handle the loading and processing of images for segmentation.
    """
    def __init__(self, root_folder):
        """
        Initialize the segmentation class.
        Parameters:
            root_folder (str): Path to the root folder containing images.
        """
        self.root_folder = root_folder
        self.images = []

    def load_images(self):
        """
        Load images from the root folder and store them in a list.
        The images are expected to be in subdirectories named "heatmap_test_<number>".
        Each subdirectory should contain images named "object_<number>.png".
        """
        for dir_name in os.listdir(self.root_folder):
            dir_path = os.path.join(self.root_folder, dir_name)
            if os.path.isdir(dir_path) and dir_name.startswith("heatmap_test_"):
                objects_list = []
                for file_name in os.listdir(dir_path):
                    if file_name.endswith(".png") and file_name.startswith("object_"):
                        file_path = os.path.join(dir_path, file_name)
                        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                        print(file_path)
                        if image is not None:
                            sparse_image = csr_matrix(image)
                            objects_list.append((file_name, sparse_image))
                self.images.append((dir_name, objects_list))

    def get_image(self, heatmap_test_name, object_name):
        """
        Get a specific image from the loaded images.
        Parameters:
            heatmap_test_name (str): Name of the heatmap test directory.
            object_name (str): Name of the object image file.
        Returns:
            sparse_image (scipy.sparse.csr_matrix): Sparse matrix representation of the image.
        """
        for dir_name, objects_list in self.images:
            if dir_name == heatmap_test_name:
                for file_name, sparse_image in objects_list:
                    if file_name == object_name:
                        return sparse_image

    def get_list(self, heatmap_test_name):
        """
        Get a list of images from a specific heatmap test directory.
        Parameters:
            heatmap_test_name (str): Name of the heatmap test directory.
        Returns:
            list: List of sparse matrix representations of images.
        """
        for dir_name, objects_list in self.images:
            if dir_name == heatmap_test_name:
                return [sparse_image for _, sparse_image in objects_list]
        return None

    def add_image(self, heatmap_test_name, object_name, image):
        """
        Add a new image to the specified heatmap test directory.
        Parameters:
            heatmap_test_name (str): Name of the heatmap test directory.
            object_name (str): Name of the object image file.
            image (numpy.ndarray): Image to be added.
        """
        if image is None:
            print(f"Failed to load image")
            return
        sparse_image = csr_matrix(image)

        for dir_name, objects_list in self.images:
            if dir_name == heatmap_test_name:
                objects_list.append((object_name, sparse_image))
                return

    def replace_image(self, heatmap_test_name, object_name, new_image):
        """
        Replace an existing image in the specified heatmap test directory.
        Parameters:
            heatmap_test_name (str): Name of the heatmap test directory.
            object_name (str): Name of the object image file.
            new_image (numpy.ndarray): New image to replace the existing one.
        """
        if new_image is None:
            print(f"Failed to load new image")
            return
        new_sparse_image = csr_matrix(new_image)

        for dir_name, objects_list in self.images:
            if dir_name == heatmap_test_name:
                for i, (file_name, _) in enumerate(objects_list):
                    if file_name == object_name:
                        objects_list[i] = (object_name, new_sparse_image)
                        return
