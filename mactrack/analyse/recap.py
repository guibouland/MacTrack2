import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.signal import find_peaks, find_peaks_cwt, savgol_filter, detrend, peak_widths
from scipy.fft import fft
import pandas as pd
import pywt


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
        num_peaks : list
            Number of peaks for each row.
        mean_prominence : list
            Mean prominence of peaks for each row.
        mean_distance : list
            Mean distance between peaks for each row.
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





def minimum_peak_prominence(signal, peaks, properties, p=0.3):
    """Check if the peaks given by `find_peaks` are valid or not. A point is considered a peak if on either of its sides, there is reduction of > 0.1*p to the previous or next sample point. p is a percentage value of the difference between the maximum and the minimum of the normalized signal (HPA = max(F)-min(F))."""
    if p<=0 or p>=1:
        raise ValueError("p must be between 0 and 1 (exclusive)")
    hpa = np.max(signal) - np.min(signal)
    mpp = hpa * p
    valid_peaks = []
    rejects = []
    count=0
    for i, peak in enumerate(peaks):
        i = i - count
        if signal[peak] - signal[peak-1] > mpp or signal[peak] - signal[peak+1] > mpp:
            valid_peaks.append(peak)
        else:
            rejects.append(peak)
            properties['prominences'] = np.delete(properties['prominences'], i, axis=0)
            count += 1
    return valid_peaks, rejects, properties



def peaks(intensity_data):
    amplitude = []
    num_peaks = []
    peaks_ = []
    width_ = []
    for i in range(intensity_data.shape[0]):

        signal = intensity_data.iloc[i, :].values
        #remove NaN values
        signal = signal[~np.isnan(signal)]



        signal_d = detrend(signal)

        signal_d_smooth = savgol_filter(signal_d, window_length=5, polyorder=2)
        print(signal_d_smooth)
        peaks, properties = find_peaks(signal_d_smooth, prominence=0.3)
        width = peak_widths(signal_d_smooth, peaks, rel_height=0.5)[0]
        print(peaks)
        print(width)
        peaks_neg, properties_neg = find_peaks(-signal_d_smooth, prominence=0.3)

        num_peaks.append(len(peaks))
        peaks_.append(peaks)
        width_.append(np.mean(width))
        amplitude.append(np.mean(signal_d_smooth[peaks]) - np.mean(signal_d_smooth[peaks_neg]))

        #wavelet transform dicrete
        scales = np.arange(1, 128)
        coefficients, frequencies = pywt.cwt(signal_d_smooth, wavelet='morl', scales=scales)

        Fs = 1/9 # fréquence d'échantillonnage : 
        #  fourier transform
        N= len(signal_d_smooth)
        yf = np.fft.fft(signal_d_smooth)
        xf = np.fft.fftfreq(N, d=1/Fs)  # fréquence d'échantillonnage de 9 Hz

        power = np.abs(yf)**2 / N # Normalized power spectrum (a.u.)
        milli_xf = xf* 1e3  # Convert to mHz

        half_N = N // 2
        milli_xf = milli_xf[:half_N]  # Positive frequencies only
        power = power[:half_N]  # Corresponding power values



        # Plotting
        fig = plt.figure(figsize=(14, 10))
        gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])  # Ligne 1 plus haute

        # Grand graphe sur toute la première ligne
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(signal_d_smooth, label='Signal', color='blue')
        ax1.plot(peaks, signal_d_smooth[peaks], 'o', color='orange', label='Peaks')
        ax1.plot(peaks_neg, signal_d_smooth[peaks_neg], 'o', color='green', label='Negative Peaks')
        ax1.hlines(np.mean(signal_d_smooth), 0, len(signal_d_smooth), colors='red', linestyles='--', label='Mean')
        ax1.hlines(np.mean(signal_d_smooth[peaks]), 0, len(signal_d_smooth), colors='orange', linestyles='--', label='Positive Peaks Ave')
        ax1.hlines(np.mean(signal_d_smooth[peaks_neg]), 0, len(signal_d_smooth), colors='green', linestyles='--', label='Negative Peaks Ave')
        ax1.set_title(f'Signal Intensity for Row {i+1}\nDetrending + SavGolFilter | Amplitude = {amplitude[i]:.2f}')
        ax1.legend()
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Amplitude')

        # En bas à gauche : ondelettes
        ax2 = fig.add_subplot(gs[1, :])
        plt.imshow(np.abs(coefficients), extent = [0, len(signal_d_smooth), scales[-1], scales[0]], aspect='auto', cmap='inferno', 
                   vmax=np.percentile(np.abs(coefficients), 99), vmin=np.percentile(np.abs(coefficients), 1))
        #pcm = ax2.pcolormesh(np.arange(len(signal_d_smooth)), frequencies, np.abs(coefficients[:-1, :-1]),
        #                     shading='auto', cmap='inferno')
        ax2.set_title('Wavelet Transform (Time-Frequency Domain)')
        #plt.colorbar(label='Magnitude')
        #fig.colorbar(pcm, ax=ax2, label='Magnitude')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Scale')

        # En bas à droite : FFT
        #ax3 = fig.add_subplot(gs[1, 1])
        ##ax3.imshow(spect, aspect='auto', origin='lower', extent=[0, num_windows, fft_frequencies[0], fft_frequencies[-1]], cmap='inferno')
        ##ax3.plot(xf[:nyquist],np.abs(yf)[:nyquist], label='FFT', color='purple')
        #ax3.plot(milli_xf,power, label='FFT', color='purple')
        ##ax3.plot(f[1:int(np.floor(n/2))], power[1:int(np.floor(n/2))], label='FFT', color='purple')
        #ax3.set_title('Fourier Transform')
        #ax3.set_xlabel('Frequency (mHz)')
        #ax3.set_ylabel('Power (a.u.)')
        #ax3.legend()

        plt.tight_layout()
        plt.savefig(f'output/plot/intensity_curve_{i+1}.png', format='png')

    return num_peaks, amplitude, peaks_, width_

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
    #plot_intensity_curves(intensity_data, valid_entry_counts)
    print(f"Les courbes d'intensité ont été enregistrées pour les entrées valides")


def agg2(intensity_data):
    intensity = load_data(intensity_data)
    num_peaks, amplitude, peaks_, width = peaks(intensity)

    aggregated_data = pd.DataFrame({
        "peaks": num_peaks,
        "amplitude": amplitude,
        "width": width,
    })
    aggregated_data.to_excel("output/data/agg2.xlsx", engine="openpyxl")
    print("Les données agrégées ont été enregistrées dans output/data/agg2.xlsx")