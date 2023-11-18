import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft

# Replace 'your_audio_file.wav' with the path to your audio file
audioFilePath = 'Recordins/10 Nov at RSA/52500(1).wav'

# Read the audio file
sampleRate, audioData = wavfile.read(audioFilePath)

# If stereo, convert to mono by averaging the two channels
if len(audioData.shape) == 2:
    audioData = audioData.mean(axis=1)

# Plot Spectrogram
plt.figure(figsize=(10, 4))
plt.specgram(audioData, Fs=sampleRate, vmin=-20, vmax=50)
plt.title('Spectrogram')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.colorbar(label='Intensity [dB]')
plt.show()

# FFT Analysis
N = len(audioData)
fftAudio = fft(audioData)
frequencies = np.linspace(0, sampleRate, N)
magnitudeFFT = np.abs(fftAudio) / N
magnitudeFFT = magnitudeFFT[:N // 2]  # Keep only the positive frequencies

# Plot FFT
plt.figure(figsize=(10, 4))
plt.plot(frequencies[:N // 2], magnitudeFFT)
plt.title('Magnitude Spectrum (FFT)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.grid()
plt.show()