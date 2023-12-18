import os
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.fft import fft
import re

def clean_title(filename):
    return re.sub(r'\(\d+\)$', '', filename)

def read_and_fft(audioFilePath):
    audioData, sampleRate = sf.read(audioFilePath)
    if issubclass(audioData.dtype.type, np.integer):
        audioData = audioData / np.iinfo(audioData.dtype).max
    if len(audioData.shape) == 2:
        audioData = audioData.mean(axis=1)

    N = len(audioData)
    fftAudio = fft(audioData)
    frequencies = np.linspace(0, sampleRate, N)
    magnitudeFFT = np.abs(fftAudio) / N
    magnitudeFFT = magnitudeFFT[:N // 2]
    magnitudeFFT_dB = 20 * np.log10(magnitudeFFT)
    return frequencies[:N // 2], magnitudeFFT_dB

def overlay_ffts_in_directory(directory, save_filename='overlay_fft.png'):
    plt.figure(figsize=(10, 4))
    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            audioFilePath = os.path.join(directory, filename)
            
            if not os.path.exists(audioFilePath):
                print(f"File not found: {audioFilePath}")
                continue

            frequencies, magnitudeFFT_dB = read_and_fft(audioFilePath)
            plt.plot(frequencies, magnitudeFFT_dB, label=clean_title(filename), alpha=0.7)

    plt.title('Overlay of FFTs in ' + directory)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.grid()
    plt.xlim(0, 22000)
    plt.ylim(-150, 0)
    plt.legend()
    plt.savefig(os.path.join(directory, save_filename))
    plt.show()
    plt.close()

# Example usage
directory = 'files_to_plot/'  # Update with the path to your directory
overlay_ffts_in_directory(directory, 'fft_comparison.png')
