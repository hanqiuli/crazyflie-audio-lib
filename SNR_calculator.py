import os
import numpy as np
import librosa
import matplotlib.pyplot as plt

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

def plot_all_snrs(all_snrs, labels):
    """Plot all SNR distributions on a single axis with custom x-axis labels."""
    plt.figure(figsize=(12, 6))  # Adjust size as needed
    # Plot all SNRs on the same axes
    positions = range(1, len(all_snrs) + 1)  # Position each box plot
    plt.boxplot(all_snrs, vert=True, patch_artist=True, positions=positions)
    
    # Set x-axis labels
    plt.xticks(positions, labels)  # Set custom labels for each boxplot
    plt.title("SNR across multiple microphone heights, normalised to propeller radius")
    plt.ylabel("SNR (dB)")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("snr_distribution.png")
    plt.show()
    plt.close()

if __name__ == "__main__":
    heights = [0, 1, 2, 3, 4, 5, 6, 7]  # Heights to process
    labels = [f"{height} [y/R]" for height in heights]  # Custom labels for each boxplot
    all_snrs = []

    clean_signal_path = 'Recordings/3_May_SwarmLab_with_NewSetup/ORGANIZED/Clean/Clean.clean.1.wav.4t42velb.ingestion-54fbc688b-qbw86.s7.wav'  # Path to the clean signal
    for height in heights:
        noisy_signals_directory = f'Recordings/3_May_SwarmLab_with_NewSetup/ORGANIZED/Height_{height}/'
        snrs, _ = calculate_all_snrs(clean_signal_path, noisy_signals_directory)
        all_snrs.append(snrs)

    plot_all_snrs(all_snrs, labels)
