import os
import numpy as np
import librosa
import matplotlib.pyplot as plt

def calculate_power(audio):
    """Calculate the power of an audio signal."""
    return np.mean(np.square(audio))

def calculate_snr(noise_path, signal_with_noise_path):
    """Calculate the Signal-to-Noise Ratio (SNR) in dB."""
    # Load the noise and signal with noise recordings
    noise, sr_noise = librosa.load(noise_path, sr=None)
    signal_with_noise, sr_sw_noise = librosa.load(signal_with_noise_path, sr=None)
    
    # Ensure the sample rates match
    if sr_noise != sr_sw_noise:
        raise ValueError("Sample rates do not match!")

    # Trimming to match the shortest recording
    min_length = min(len(noise), len(signal_with_noise))
    noise = noise[:min_length]
    signal_with_noise = signal_with_noise[:min_length]

    # Calculate power for noise and signal with noise
    power_noise = calculate_power(noise)
    power_signal_with_noise = calculate_power(signal_with_noise)

    # Estimate the power of the signal alone
    power_signal = power_signal_with_noise - power_noise
    
    # Avoid division by zero or negative signal power
    if power_signal <= 0:
        print(f"Non-positive signal power encountered: {power_signal}")
        return 'Error: Non-positive signal power'

    # Calculate SNR
    snr_db = 10 * np.log10(power_signal / power_noise)
    return snr_db

def calculate_all_snrs(noise_path, signal_with_noises_directory):
    snrs = []
    filenames = []

    for filename in os.listdir(signal_with_noises_directory):
        if filename.endswith(".wav"):
            full_path = os.path.join(signal_with_noises_directory, filename)
            try:
                snr = calculate_snr(noise_path, full_path)
                if isinstance(snr, str):
                    print(f"Error calculating SNR for {filename}: {snr}")
                else:
                    snrs.append(snr)
                    filenames.append(filename)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

    return snrs, filenames, signal_with_noises_directory

def plot_snrs(snrs, signal_with_noises_directory):
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

    plt.savefig("SNR_Calc/" + signal_with_noises_directory + "snr_distribution.png")

if __name__ == "__main__":
    for i in [5, 10, 15, 20]:
        noise_path = f'SNR_Calc/noise_{i}.wav'
        signal_with_noises_directory = f'SNR_Calc/go_{i}/'
        snrs, filenames, signal_with_noises_dir = calculate_all_snrs(noise_path, signal_with_noises_directory)
        plot_snrs(snrs, signal_with_noises_dir)
