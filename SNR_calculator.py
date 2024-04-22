import os
import numpy as np
import librosa
import matplotlib.pyplot as plt

def calculate_power(audio):
    """Calculate the power of an audio signal."""
    return np.mean(np.square(audio))

def calculate_snr(clean_signal_path, noisy_signal_path):
    """Calculate the Signal-to-Noise Ratio (SNR) in dB."""
    clean_signal, sr_clean = librosa.load(clean_signal_path, sr=None)
    noisy_signal, sr_noisy = librosa.load(noisy_signal_path, sr=None)
    
    # Ensure the sample rates match
    if sr_clean != sr_noisy:
        raise ValueError("Sample rates do not match!")

    # Trimming the longer signal to match the shorter one
    min_length = min(len(clean_signal), len(noisy_signal))
    clean_signal = clean_signal[:min_length]
    noisy_signal = noisy_signal[:min_length]

    # Calculate the difference (noise or distortion)
    residual = noisy_signal - clean_signal
    
    # Calculate powers
    power_clean_signal = calculate_power(clean_signal)
    power_residual = calculate_power(residual)
    
    # Avoid division by zero or negative noise power
    if power_residual <= 0:
        print(f"Non-positive noise power encountered: {power_residual}")
        return 'Error: Non-positive noise power'

    # Calculate SNR
    snr_db = 10 * np.log10(power_clean_signal / power_residual)
    return snr_db

def calculate_all_snrs(clean_signal_path, noisy_signals_directory):
    clean_signal, sr_clean = librosa.load(clean_signal_path, sr=None)
    snrs = []
    filenames = []

    for filename in os.listdir(noisy_signals_directory):
        if filename.endswith(".wav"):
            full_path = os.path.join(noisy_signals_directory, filename)
            try:
                snr = calculate_snr(clean_signal_path, full_path)
                if isinstance(snr, str):
                    print(f"Error calculating SNR for {filename}: {snr}")
                else:
                    snrs.append(snr)
                    filenames.append(filename)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

    return snrs, filenames

def plot_snrs(snrs, filenames):
    plt.figure(figsize=(10, 6))
    plt.boxplot(snrs, vert=True, patch_artist=True)
    plt.title("SNR Distribution Across Different Noisy Audios")
    plt.ylabel("SNR (dB)")
    plt.xticks([1], ["Noisy Recordings"])
    plt.grid(True)

    # Calculating statistical data
    mean_snr = np.mean(snrs)
    std_snr = np.std(snrs)
    plt.text(1.1, mean_snr, f'Mean: {mean_snr:.2f} dB', verticalalignment='center')
    plt.text(1.1, mean_snr + 2 * std_snr, f'+2σ: {mean_snr + 2 * std_snr:.2f} dB', verticalalignment='center')
    plt.text(1.1, mean_snr - 2 * std_snr, f'-2σ: {mean_snr - 2 * std_snr:.2f} dB', verticalalignment='center')

    plt.show()

if __name__ == "__main__":
    clean_signal_path = 'path/to/your/clean_signal.wav'
    noisy_signals_directory = 'path/to/your/noisy_signals'
    snrs, filenames = calculate_all_snrs(clean_signal_path, noisy_signals_directory)
    plot_snrs(snrs, filenames)
