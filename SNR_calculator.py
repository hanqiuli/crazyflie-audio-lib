import os
import numpy as np
import librosa
import matplotlib.pyplot as plt

def calculate_power_spectra(signal):
    """Calculate the power spectrum of a signal using FFT."""
    fft_signal = np.fft.fft(signal)
    power_spectrum = np.abs(fft_signal) ** 2
    return power_spectrum

def calculate_snr(noise, noisy_signal):
    """Calculate the average spectral SNR after trimming the signals to the same length."""
    min_length = min(len(noise), len(noisy_signal))
    noise = noise[:min_length]
    noisy_signal = noisy_signal[:min_length]
    
    power_spectrum_noise = calculate_power_spectra(noise)
    power_spectrum_noisy_signal = calculate_power_spectra(noisy_signal)
    power_spectrum_signal = power_spectrum_noisy_signal - power_spectrum_noise
    power_spectrum_signal[power_spectrum_signal <= 0] = 1e-10  # Avoid log(0) and negative values
    
    snr_spectrum = 10 * np.log10(power_spectrum_signal / power_spectrum_noise)
    mean_snr = np.mean(snr_spectrum)
    return mean_snr

def calculate_all_snrs(noise_path, signal_with_noises_directory):
    """Calculate SNRs for all .wav files in a given directory."""
    snrs = []
    filenames = []

    noise, sr_noise = librosa.load(noise_path, sr=None)
    for filename in os.listdir(signal_with_noises_directory):
        if filename.endswith(".wav"):
            full_path = os.path.join(signal_with_noises_directory, filename)
            try:
                noisy_signal, sr_noisy = librosa.load(full_path, sr=None)
                min_length = min(len(noise), len(noisy_signal))
                noise = noise[:min_length]
                noisy_signal = noisy_signal[:min_length]

                snr = calculate_snr(noise, noisy_signal)
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
    heights = [5, 10, 15, 20]  # Different scenarios, such as microphone heights
    labels = ["5%", "10%", "15%", "20%"]  # Labels indicating the normalized heights
    all_snrs = []

    for height in heights:
        noise_path = f'SNR_Calc/noise_{height}.wav'
        signal_with_noises_directory = f'SNR_Calc/go_{height}/'
        snrs, _ = calculate_all_snrs(noise_path, signal_with_noises_directory)
        all_snrs.append(snrs)

    plot_all_snrs(all_snrs, labels)

