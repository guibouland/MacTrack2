import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def load_data(file_path):
    """
    Loads data from an Excel file.

    Parameters:
        file_path (str): Path to the Excel file.

    Returns:
        pd.DataFrame: Data loaded from the Excel file.
    """
    data = pd.read_excel(file_path, index_col=0)
    return data


def calculate_intensity_features(intensity_data):
    """
    Calculates intensity features such as the number of peaks, mean prominence,
    and mean distance between peaks for each row in the intensity data.

    Parameters
    ----------
    intensity_data : pd.DataFrame
        DataFrame containing intensity data, where each row represents a signal.

    Returns
    -------
    tuple
        A tuple containing:
        * **num_peaks** (*pd.Series*): Number of peaks for each row.
        * **mean_prominence** (*pd.Series*): Mean prominence of peaks for each row.
        * **mean_distance** (*pd.Series*): Mean distance between peaks for each row.
    """

    def find_peaks_and_prominences(row):
        peaks, properties = find_peaks(row, prominence=0.3)
        prominences = properties["prominences"]
        return peaks, prominences

    def mean_distance_between_peaks(peaks):
        if len(peaks) > 1:
            distances = np.diff(peaks)
            return distances.mean()
        return np.nan

    peaks_and_prominences = intensity_data.apply(
        lambda row: find_peaks_and_prominences(row), axis=1
    )
    peaks_list = peaks_and_prominences.apply(lambda x: x[0])
    prominences_list = peaks_and_prominences.apply(lambda x: x[1])
    num_peaks = peaks_list.apply(len)
    mean_prominence = prominences_list.apply(lambda x: x.mean() if len(x) > 0 else 0)
    mean_distance = peaks_list.apply(
        lambda peaks: mean_distance_between_peaks(peaks) if len(peaks) > 2 else np.nan
    )

    return num_peaks, mean_prominence, mean_distance


def calculate_mean(data):
    """
    Calculates the mean of each row in the given DataFrame.
    Parameters:
        data (pd.DataFrame): The input DataFrame to analyze.
    Returns:
        pd.Series: A series containing the mean of each row.
    """
    return data.mean(axis=1)


def count_valid_entries(data):
    """
    Counts the number of valid (non-NaN) entries in each row of the given DataFrame.

    Parameters:
        data (pd.DataFrame): The input DataFrame to analyze.

    Returns:
        pd.Series: A series containing the count of valid entries for each row.
    """
    num_valid_entries = data.notna().sum(axis=1)
    return num_valid_entries


def plot_intensity_curves(intensity_data, valid_entry_counts, threshold=10):
    """
    Plots intensity curves for each row in the DataFrame and saves them as PNG files.
    Parameters:
        intensity_data (pd.DataFrame): The DataFrame containing intensity data.
        valid_entry_counts (pd.Series): A series containing the count of valid entries for each row.
        threshold (int): The minimum number of valid entries required to plot the curve.
    """
    filtered_data = intensity_data[valid_entry_counts > threshold]
    output_folder = "output/plot"
    for index, row in filtered_data.iterrows():
        plt.plot(row)
        plt.xlabel("Temps")
        plt.ylabel("Intensité")
        plt.title(f"Courbe d'intensité pour l'entrée {index}")
        plt.savefig(f"{output_folder}/intensity_curve_{index}.png", format="png")
        plt.close()


def aggregate(distance_file, intensity_file, size_file, perimeter_file):
    """
    Aggregates data from multiple files and saves the results to an Excel file.
    Parameters:
        distance_file (str): Path to the distance data file.
        intensity_file (str): Path to the intensity data file.
        size_file (str): Path to the size data file.
        perimeter_file (str): Path to the perimeter data file.
    """
    output_file = "output/data/data.xlsx"
    distance_data = load_data(distance_file)
    intensity_data = load_data(intensity_file)
    size_data = load_data(size_file)
    perimeter_data = load_data(perimeter_file)

    num_peaks, mean_prominence, mean_freq = calculate_intensity_features(intensity_data)
    mean_distance = calculate_mean(distance_data)
    mean_size = calculate_mean(size_data)
    mean_perimeter = calculate_mean(perimeter_data)
    valid_entry_counts = count_valid_entries(intensity_data)

    aggregated_data = pd.DataFrame(
        {
            "peaks": num_peaks,
            "amplitude": mean_prominence,
            "frequence": mean_freq,
            "distance": mean_distance,
            "size": mean_size,
            "perimeter": mean_perimeter,
            "validity": valid_entry_counts,
        }
    )

    aggregated_data.to_excel(output_file, engine="openpyxl")
    print(f"Les données agrégées ont été enregistrées dans {output_file}")
    plot_intensity_curves(intensity_data, valid_entry_counts)
    print(f"Les courbes d'intensité ont été enregistrées pour les entrées valides")
