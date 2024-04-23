
import os
import numpy as np
import plotly.graph_objects as go
import soundfile as sf
from scipy.fft import fft
import re

def clean_title(filename):
    return re.sub(r'\(\d+\)$', '', filename)

def extract_height(filename):
    match = re.search(r'(\d+)mm', filename)
    if match:
        return int(match.group(1))
    return 0

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

def smooth_curve(data, window_size=10):
    window = np.ones(window_size) / window_size
    return np.convolve(data, window, mode='same')

def overlay_ffts_in_directory(directory, smooth_window=10):
    fig = go.Figure()
    filenames = sorted(os.listdir(directory), key=extract_height)
    colors = [f'hsl({i / len(filenames) * 360}, 50%, 50%)' for i in range(len(filenames))]  # Colormap colors
    for filename, color in zip(filenames, colors):
        if filename.endswith('.wav'):
            audioFilePath = os.path.join(directory, filename)
            
            if not os.path.exists(audioFilePath):
                print(f"File not found: {audioFilePath}")
                continue

            frequencies, magnitudeFFT_dB = read_and_fft(audioFilePath)
            smoothed_magnitudeFFT_dB = smooth_curve(magnitudeFFT_dB, window_size=smooth_window)
            fig.add_trace(go.Scatter(x=frequencies, y=smoothed_magnitudeFFT_dB, mode='lines', name=clean_title(filename), line=dict(color=color)))

    fig.update_layout(
        title='Comparison of FFTs',
        xaxis=dict(title='Frequency (Hz)'),
        yaxis=dict(title='Magnitude (dB)'),
        showlegend=True,
        width=800,
        height=500
    )

    fig.show()

# Example usage
<<<<<<< HEAD
directory = 'tempor/'#'files_to_plot/'  # Update with the path to your directory
=======
directory = 'overlay_noise_folder/'  # Update with the path to your directory
>>>>>>> 483c0825ef0cb8ffea460eea61e7b151e01b1c64
overlay_ffts_in_directory(directory, smooth_window=250)
