import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
from scipy.ndimage import uniform_filter1d

def smooth_fft(fft_data, window_size=100):
    """Smooth the FFT data using a moving average filter."""
    return uniform_filter1d(fft_data, size=window_size)

# Generate or load your data
sample_rate = 44100  # Sample rate in Hz
duration = 1.0  # seconds
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
heights = np.arange(0, 8)  # normalized heights x/R

# Store FFT results
fft_results = []
frequencies = np.fft.fftfreq(t.size, 1/sample_rate)

for height in heights:
    # Generate a noise signal or load your noise recording
    signal = np.random.normal(0, 1, size=t.size)
    # Compute the FFT
    fft_result = np.abs(fft(signal))
    # Smooth the FFT
    smoothed_fft = smooth_fft(fft_result)
    fft_results.append(smoothed_fft)

# 3D Plot
from mpl_toolkits.mplot3d import Axes3D
X, Y = np.meshgrid(frequencies[frequencies >= 0], heights)  # Frequency and heights grid
Z = np.array(fft_results)[:, frequencies >= 0]  # Smoothed magnitude of FFT

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for i in range(len(heights)):
    ax.plot(X[i], Y[i], Z[i])

ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Normalized Height (x/R)')
ax.set_zlabel('Magnitude')
plt.show()
