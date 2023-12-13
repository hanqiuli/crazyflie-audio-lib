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
    print(sampleRate, audioFilePath)
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

def overlay_ffts(directory, filenames, save_filename='overlay_fft.png'):
    plt.figure(figsize=(10, 4))
    for filename in filenames:
        audioFilePath = os.path.join(directory, filename)
        
        # Check if the file exists
        if not os.path.exists(audioFilePath):
            print(f"File not found: {audioFilePath}")
            continue

        frequencies, magnitudeFFT_dB = read_and_fft(audioFilePath)
        plt.plot(frequencies, magnitudeFFT_dB, label=clean_title(filename))

    plt.title('Overlay of FFTs')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.grid()
    plt.xlim(0, 22000)
    plt.ylim(-150, 0)
    plt.legend()
    plt.savefig(os.path.join(directory, save_filename))
    plt.close()

#Plotting
directory = 'Recordings'
filenames = ['7 Dec 2023 - Penguin Lab/Medium/medium47500.1.wav', '7 Dec 2023 - Penguin Lab/Small/smallredo47500.1.wav', '10 Nov 2023 - RSA/47500(1).wav']
overlay_ffts(directory, filenames, 'fft_comparison.png')
