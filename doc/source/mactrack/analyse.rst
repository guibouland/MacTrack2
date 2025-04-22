Analyse Module
==============

This module contains functions for analyzing data, generating graphs, and calculating distances from images.

.. code-block:: python

    import os
    import pandas as pd
    import re
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt

    # Function to count valid (non-NA) entries in a DataFrame
    def count_valid_entries(data):
        num_valid_entries = data.notna().sum(axis=1)
        return num_valid_entries

    # Function to generate a graph of distances over time
    def graph():
        file_path = 'output/data/distance.xlsx'
        data = pd.read_excel(file_path)
        data = data.fillna(0)  # Replace NaN values with 0
        individus = data.iloc[:, 0]  # First column contains individual identifiers
        intensites = data.iloc[:, 1:]  # Remaining columns contain intensity values
        threshold = 0
        for i, individu in enumerate(individus):
            y = intensites.iloc[i]
            x = intensites.columns
            y_masked = np.where(y == threshold, np.nan, y)  # Mask threshold values with NaN
        
            plt.plot(x, y_masked, label=individu)
        step = 5
        plt.xticks(intensites.columns[::step], rotation=45)
        plt.xlabel('Temps')
        plt.ylabel('distance')
        plt.title('Courbes de distance des individus au cours du temps')
        plt.savefig('output/plot/courbes_distance_individus.png', format='png')
        plt.close()

    # Function to calculate the distance of an object to the right edge of an image
    def distance_to_right_edge(image_path):
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("L'image n'a pas pu être chargée.")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            raise ValueError("Aucun contour n'a été détecté dans l'image.")
        
        contour = contours[0]
        M = cv2.moments(contour)

        if M["m00"] == 0:
            raise ValueError("Le moment du contour est zéro, le centre ne peut pas être calculé.")
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        image_width = image.shape[1]
        distance = image_width - cX

        return distance

    # Function to calculate distances for multiple images and save results to an Excel file
    def distance(n):
        base_folder = 'output/list_track'
        output_file = 'output/data/distance.xlsx'
        if not output_file.endswith('.xlsx'):
            raise ValueError("Output file must have an .xlsx extension")

        folders = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d)) and d.startswith('macrophage_')]
        folders.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
        results = []
        for folder in folders:
            folder_path = os.path.join(base_folder, folder)
            folder_result = {'Time': folder}
            print(folder_path)
            for a in range(0, n):
                found = False

                for file in os.listdir(folder_path):
                    if re.match(rf'{a}_\d+\.png', file):
                        found = True
                        input = os.path.join(folder_path, file)
                        x = distance_to_right_edge(input)
                        folder_result[f'{a}'] = x
                        break
                if not found:
                    folder_result[f'{a}'] = 'NA'
            
            results.append(folder_result)
        df = pd.DataFrame(results)
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Report saved to {output_file}")
        graph()
        return output_file