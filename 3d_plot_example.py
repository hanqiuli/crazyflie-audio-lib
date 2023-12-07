import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def plot_3d_spectrum(file_paths, x_values):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    for i, file_path in enumerate(file_paths):
        # Load the audio file
        y, sr = librosa.load(file_path)

        # Compute the Short-Time Fourier Transform (STFT)
        D = np.abs(librosa.stft(y))

        # Extract frequency and time axes
        freqs = librosa.fft_frequencies(sr=sr)
        
        # Use the provided x_values as the x-axis
        x = x_values[i]

        # Create a meshgrid for 3D plot
        X, F = np.meshgrid(np.linspace(x, x, num=D.shape[1]), freqs)

        # Plot the magnitude spectrum
        ax.plot_surface(X, F, 20 * np.log10(D), cmap='viridis', alpha=0.8, label=f'File {i + 1}')

    ax.set_xlabel('WPM Values')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_zlabel('Magnitude (dB)')
    ax.set_title('3D Frequency Spectrum')
    ax.legend()

    plt.show()

# Replace these paths with the actual paths to your WAV files
file_paths = ['recordins/7 Dec 2023 - Penguin Lab\medium15000.1.wav','recordins/7 Dec 2023 - Penguin Lab\medium30000.1.wav','recordins/7 Dec 2023 - Penguin Lab\medium40000.1.wav', 'recordins/7 Dec 2023 - Penguin Lab\medium42500.1.wav', 'recordins/7 Dec 2023 - Penguin Lab\medium45000.1.wav', 'recordins/7 Dec 2023 - Penguin Lab\medium47500.1.wav', 'recordins/7 Dec 2023 - Penguin Lab\medium50000.1.wav', 'recordins/7 Dec 2023 - Penguin Lab\medium55000.1.wav']

# Replace these values with your set of 5 numbers for each file
x_values = [15000, 30000, 40000,42500, 45000, 47500, 50000, 55000]

plot_3d_spectrum(file_paths, x_values)
