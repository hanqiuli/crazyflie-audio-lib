from scipy.io import wavfile
from scipy.signal import welch
from scipy.stats import gmean
import matplotlib.pyplot as plt
import numpy as np

# Function to calculate spectral flatness across the entire frequency range
def calculate_spectral_flatness_full_range(file_paths):
    spectral_flatness_measures = []

    for file_path in file_paths:
        sample_rate, data = wavfile.read(file_path)
        
        # Normalize data
        data = data / np.max(np.abs(data))
        
        # Calculate power spectral density
        frequencies, power_density = welch(data, sample_rate, nperseg=1024)
        
        # Calculate spectral flatness
        geometric_mean = gmean(power_density)
        arithmetic_mean = np.mean(power_density)
        spectral_flatness = geometric_mean / arithmetic_mean
        
        spectral_flatness_measures.append(spectral_flatness)

    return spectral_flatness_measures

# Adjust the file paths to point to the correct folder
file_folder = 'tempor/'  # Update this to your folder path
file_paths = [f"{file_folder}height_{height:02}.wav" for height in range(0, 20, 2)]
heights = list(range(0, 20, 2))

# Calculate spectral flatness for each recording
spectral_flatness_measures_full = calculate_spectral_flatness_full_range(file_paths)

# Plotting the spectral flatness measures
plt.figure(figsize=(10, 6))
plt.plot(heights, spectral_flatness_measures_full, marker='o', color='r')
plt.xlabel('Microphone Height (mm)')
plt.ylabel('Spectral Flatness (Full Frequency Range)')
plt.title('Spectral Flatness Across Full Frequency Range at Different Heights')
plt.grid(True)
plt.show()
