import os
import pandas as pd
import re
import cv2
import numpy as np
import matplotlib.pyplot as plt


def graphmed_perimeter():
    """
    Generates a plot of the perimeter of individuals over time (frames).
    Reads data from an Excel file, processes it, and saves the plot as a PNG image.
    """

    file_path = "output/data/perimeter.xlsx"
    data = pd.read_excel(file_path)
    data = data.fillna(0)
    individus = data.iloc[:, 0]
    intensites = data.iloc[:, 1:]
    threshold = 0

    for i, individu in enumerate(individus):
        y = intensites.iloc[i]
        x = intensites.columns
        y_masked = np.where(y == threshold, np.nan, y)

        plt.plot(x, y_masked, label=individu)
    step = 5
    plt.xticks(intensites.columns[::step], rotation=45)
    plt.xlabel("Temps")
    plt.ylabel("taille")
    plt.title("Courbes de périmetre des individus au cours du temps")
    plt.savefig("output/plot/courbes_perimetre_individus.png", format="png")
    plt.close()


def object_size(image_path):
    """
    Calculate the perimeter of a contour in an image.

    Parameters:
        image_path (str): Path to the input image.

    Returns:
        float: Perimeter of the largest contour in the image.

    Raises:
        ValueError: If the image cannot be loaded or if no contours are found.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("L'image n'a pas pu être chargée.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return 0
    contour = contours[0]
    object_perimeter = cv2.arcLength(contour, True)

    return object_perimeter


def perimeter(n):
    """
    Calculate the perimeter of objects in images and save the results to an Excel file.
    The images are expected to be organized in folders named 'macrophage_<number>'.
    Each folder contains images named '<number>_<index>.png'.
    The results are saved in an Excel file named 'perimeter.xlsx'.

    Parameters:
        n (int): The number of images to process in each folder.

    Returns:
        str: The path to the output Excel file.

    Raises:
        ValueError: If the output file does not have an .xlsx extension.
    """
    base_folder = "output/list_track"
    output_file = "output/data/perimeter.xlsx"
    if not output_file.endswith(".xlsx"):
        raise ValueError("Output file must have an .xlsx extension")

    folders = [
        d
        for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d)) and d.startswith("macrophage_")
    ]
    folders.sort(key=lambda x: int(re.findall(r"\d+", x)[0]))
    results = []
    for folder in folders:
        folder_path = os.path.join(base_folder, folder)
        folder_result = {"Time": folder}
        print(folder_path)
        for a in range(0, n):
            found = False

            for file in os.listdir(folder_path):
                if re.match(rf"{a}_\d+\.png", file):
                    found = True
                    input_ = os.path.join(folder_path, file)
                    x = object_size(input_)
                    folder_result[f"{a}"] = x
                    break
            if not found:
                folder_result[f"{a}"] = "NA"

        results.append(folder_result)
    df = pd.DataFrame(results)

    # Replace the 0 values (if merge) by the mean of the 5 previous and the 5 next values of the row they belong to
    for i in range(len(df)):
        for j in range(1, len(df.columns)):
            if df.iloc[i, j] == 0:
                # idx of the row
                # list of the 5 previous in the same row (i)
                prev = df.iloc[i, j - 5 : j].tolist()
                # list of the 5 next in the same row (i)
                next_ = df.iloc[i, j + 1 : j + 6].tolist()
                mean_value = (sum(prev) + sum(next_)) / (len(prev) + len(next_))
                df.iloc[i, j] = mean_value

    df.to_excel(output_file, index=False, engine="openpyxl")
    print(f"Report saved to {output_file}")
    graphmed_perimeter()
    return output_file
