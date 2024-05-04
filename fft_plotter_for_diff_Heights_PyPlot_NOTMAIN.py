# from scipy.io import wavfile
# from scipy.signal import welch
# from scipy.stats import gmean
# import matplotlib.pyplot as plt
# import numpy as np

# # Function to calculate spectral flatness across the entire frequency range
# def calculate_spectral_flatness_full_range(file_paths):
#     spectral_flatness_measures = []

#     for file_path in file_paths:
#         sample_rate, data = wavfile.read(file_path)
        
#         # Normalize data
#         data = data / np.max(np.abs(data))
        
#         # Calculate power spectral density
#         frequencies, power_density = welch(data, sample_rate, nperseg=1024)
        
#         # Calculate spectral flatness
#         geometric_mean = gmean(power_density)
#         arithmetic_mean = np.mean(power_density)
#         spectral_flatness = geometric_mean / arithmetic_mean
        
#         spectral_flatness_measures.append(spectral_flatness)

#     return spectral_flatness_measures

# # Adjust the file paths to point to the correct folder
# file_folder = 'tempor/'  # Update this to your folder path
# file_paths = [f"{file_folder}height_{height:02}.wav" for height in range(0, 20, 2)]
# heights = list(range(0, 20, 2))

# # Calculate spectral flatness for each recording
# spectral_flatness_measures_full = calculate_spectral_flatness_full_range(file_paths)

# # Plotting the spectral flatness measures
# plt.figure(figsize=(10, 6))
# plt.plot(heights, spectral_flatness_measures_full, marker='o', color='r')
# plt.xlabel('Microphone Height (mm)')
# plt.ylabel('Spectral Flatness (Full Frequency Range)')
# plt.title('Spectral Flatness Across Full Frequency Range at Different Heights')
# plt.grid(True)
# plt.show()
#####################################################################################################
from scipy.io import wavfile
from scipy.signal import welch
from scipy.stats import gmean
import matplotlib.pyplot as plt
import numpy as np


from scipy.stats import gmean

# Function to calculate spectral flatness in the voice frequency band (300-3400 Hz)
def calculate_spectral_flatness(file_paths, voice_freq_range=(00, 10000)):
    spectral_flatness_measures = []

    for file_path in file_paths:
        sample_rate, data = wavfile.read(file_path)
        
        # Normalize data
        data = data / np.max(np.abs(data))
        
        # Calculate power spectral density
        frequencies, power_density = welch(data, sample_rate, nperseg=1024)
        
        # Extract power density in the voice frequency range
        voice_freq_indices = (frequencies >= voice_freq_range[0]) & (frequencies <= voice_freq_range[1])
        power_density_voice = power_density[voice_freq_indices]
        
        # Calculate spectral flatness
        geometric_mean = gmean(power_density_voice)
        arithmetic_mean = np.mean(power_density_voice)
        spectral_flatness = geometric_mean / arithmetic_mean
        
        spectral_flatness_measures.append(spectral_flatness)

    return spectral_flatness_measures

############
heights = [0.5, 1, 1.5, 2]# list(range(0, 20, 2))
#file_folder = "Recordings\23April_ScienceCentre\untouched" # 'tempor/'  # Update this to your folder path
file_paths = ["Recordings/23April_ScienceCentre/untouched/noise5h.1.wav", "Recordings/23April_ScienceCentre/untouched/noise1h.1.wav", "Recordings/23April_ScienceCentre/untouched/noise15h.1.wav", "Recordings/23April_ScienceCentre/untouched/noisemaxh.1.wav"] 
# [f"{file_folder}height_{height:02}.wav" for height in range(0, 20, 2)]
############


# Calculate the spectral flatness in the voice frequency band for each height
spectral_flatness_measures = calculate_spectral_flatness(file_paths)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(heights, spectral_flatness_measures, marker='o')
plt.xlabel('Microphone Height (mm)')
plt.ylabel('Spectral Flatness in Voice Band')
plt.title('Spectral Flatness in Voice Frequency Band at Different Heights')
plt.grid(True)
plt.show()

spectral_flatness_measures
