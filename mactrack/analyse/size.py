import os
import pandas as pd
import re
import cv2
import numpy as np
import matplotlib.pyplot as plt


def graph_size():
    """
    Plot the size of individuals over time.
    """
    file_path = "output/data/size.xlsx"
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
    plt.title("Courbes de taille des individus au cours du temps")
    plt.savefig("output/plot/courbes_taille_individus.png", format="png")
    plt.close()


def object_size(image_path):
    """
    Calculate the size of an object in an image.
    
    Parameters:
        image_path (str): Path to the input image.
    
    Returns:
        object_area (float): Area of the detected object in pixels.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("L'image n'a pas pu être chargée.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("Aucun contour n'a été détecté dans l'image.")
    contour = contours[0]
    object_area = cv2.contourArea(contour)

    return object_area


def size(n):
    """
    Calculate the size of objects in images and save the results to an Excel file. Uses the object_size function to calculate the size of each object in the images. Uses the graph_size function to plot the size of individuals over time.
    
    Parameters:
        n (int): Number of images to process.
    
    See also:
        object_size: Function to calculate the size of an object in an image.
        graph_size: Function to plot the size of individuals over time.
    """
    base_folder = "output/list_track"
    output_file = "output/data/size.xlsx"
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
                    input = os.path.join(folder_path, file)
                    x = object_size(input)
                    folder_result[f"{a}"] = x
                    break
            if not found:
                folder_result[f"{a}"] = "NA"

        results.append(folder_result)
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False, engine="openpyxl")
    print(f"Report saved to {output_file}")
    graph_size()
    return output_file
