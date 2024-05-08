import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata


def calculate_power_spectra(signal):
    """Calculate the power spectrum of a signal using FFT."""
    fft_signal = np.fft.fft(signal)
    power_spectrum = np.abs(fft_signal) ** 2
    return power_spectrum

def calculate_snr(clean_signal, noisy_signal):
    """Calculate the average spectral SNR."""
    min_length = min(len(clean_signal), len(noisy_signal))
    clean_signal = clean_signal[:min_length]
    noisy_signal = noisy_signal[:min_length]
    
    power_spectrum_clean = calculate_power_spectra(clean_signal)
    power_spectrum_noisy = calculate_power_spectra(noisy_signal)

    # Avoid division by zero and negative values in SNR computation
    power_spectrum_noisy[power_spectrum_noisy <= 0] = 1e-10
    power_spectrum_clean[power_spectrum_clean <= 0] = 1e-10

    snr_spectrum = 10 * np.log10(power_spectrum_clean / power_spectrum_noisy)
    mean_snr = np.mean(snr_spectrum)
    return mean_snr

def calculate_all_snrs(clean_signal_path, noisy_signals_directory):
    """Calculate SNRs for all .wav files in a given directory."""
    snrs = []
    filenames = []

    clean_signal, sr_clean = librosa.load(clean_signal_path, sr=None)
    for filename in os.listdir(noisy_signals_directory):
        if filename.endswith(".wav"):
            full_path = os.path.join(noisy_signals_directory, filename)
            try:
                noisy_signal, sr_noisy = librosa.load(full_path, sr=None)
                snr = calculate_snr(clean_signal, noisy_signal)
                snrs.append(snr)
                filenames.append(filename)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
    return snrs, filenames

def plot_all_snrs(all_snrs, labels, title):
    """Plot all SNR distributions on a single axis with custom x-axis labels."""
    plt.figure(figsize=(12, 6))  # Adjust size as needed
    # Plot all SNRs on the same axes
    positions = range(1, len(all_snrs) + 1)  # Position each box plot
    plt.boxplot(all_snrs, vert=True, patch_artist=True, positions=positions)
    
    # Set x-axis labels
    plt.xticks(positions, labels)  # Set custom labels for each boxplot
    plt.title(title)
    plt.ylabel("SNR (dB)")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("snr_distribution.png")
    plt.show()
    plt.close()

def plot_snr_surface(snr_dict, title):
    """Plot a 3D surface of mean SNR values from a dictionary of SNRs indexed by distance and height."""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Flatten the data for surface plotting
    X, Y, Z = [], [], []
    for dist in snr_dict:
        for height in snr_dict[dist]:
            X.append(dist)
            Y.append(height)
            Z.append(np.mean(snr_dict[dist][height]))

    # Convert lists to numpy arrays
    X, Y, Z = np.array(X), np.array(Y), np.array(Z)

    # Create grid for surface plot
    xi, yi = np.meshgrid(np.linspace(min(X), max(X), num=100), np.linspace(min(Y), max(Y), num=100))
    zi = griddata((X, Y), Z, (xi, yi), method='cubic')

    # Plot the surface
    surf = ax.plot_surface(xi, yi, zi, cmap='viridis', linewidth=0, antialiased=False)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

    ax.set_xlabel('Height (y/R)')
    ax.set_ylabel('Inplane Distance (x/R)')
    ax.set_zlabel('Mean SNR (dB)')
    plt.title(title)
    plt.show()


if __name__ == "__main__":
    heights = [0, 1, 2, 3, 4, 5, 6, 7]  # Heights to process
    distances = [2, 3, 4]
    labels_heights = [f"{height} [y/R]" for height in heights]  # Custom labels for each boxplot
    labels_distances = ['orig'] + [f"{distance} [x/R]" for distance in distances]


    # only varying heights
    all_snrs = []

    clean_signal_path = 'Recordings/3_May_SwarmLab_with_NewSetup/ORGANIZED/Clean/Clean.clean.1.wav.4t42velb.ingestion-54fbc688b-qbw86.s7.wav'  # Path to the clean signal
    for height in heights:
        noisy_signals_directory = f'Recordings/3_May_SwarmLab_with_NewSetup/ORGANIZED/Height_{height}/'
        snrs, _ = calculate_all_snrs(clean_signal_path, noisy_signals_directory)
        all_snrs.append(snrs)

    plot_all_snrs(all_snrs, labels_heights, "SNR across multiple microphone heights, normalised to propeller radius")

    # only varying distances for the original height
    all_snrs = []

    clean_signal_path = 'Recordings/3_May_SwarmLab_with_NewSetup/ORGANIZED/Clean/Clean.clean.1.wav.4t42velb.ingestion-54fbc688b-qbw86.s7.wav'  # Path to the clean signal
    # do the original arm
    snrs, _ = calculate_all_snrs(clean_signal_path, 'Recordings/3_May_SwarmLab_with_NewSetup/ORGANIZED/Height_0/')
    all_snrs.append(snrs)
    for distance in distances:
        noisy_signals_directory = f'Recordings/6_May_SwarmLb_DifferentArms/ORGANIZED/Height_0/Arm_{distance}_Height_0/'
        snrs, _ = calculate_all_snrs(clean_signal_path, noisy_signals_directory)
        all_snrs.append(snrs)

    plot_all_snrs(all_snrs, labels_distances, "SNR across multiple arm lengths, normalised to propeller radius")


    # varying heights and distances
    all_snrs = {}
    for height in heights:
        all_snrs[height] = {}

        all_snrs[height][0] = calculate_all_snrs(clean_signal_path, f'Recordings/3_May_SwarmLab_with_NewSetup/ORGANIZED/Height_{height}/')[0]
        for distance in distances:
            try:
                noisy_signals_directory = f'Recordings/6_May_SwarmLb_DifferentArms/ORGANIZED/Height_{height}/Arm_{distance}_Height_{height}/'
                snrs, _ = calculate_all_snrs(clean_signal_path, noisy_signals_directory)
                all_snrs[height][distance] = snrs
            except Exception as e:
                pass

    # plot_snr_surface(all_snrs, "SNR across multiple microphone heights and arm lengths, normalised to propeller radius")


    # # Shroud vs no shroud
    # all_snrs = []
    # clean_signal_path = 'Recordings/3_May_SwarmLab_with_NewSetup/ORGANIZED/Clean/Clean.clean.1.wav.4t42velb.ingestion-54fbc688b-qbw86.s7.wav'  # Path to the clean signal