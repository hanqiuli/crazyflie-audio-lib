import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram

# Set the input and output directories
input_dir = 'individual_plotting/soundfiles/'
output_dir = 'individual_plotting/spectrogram_figs/'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Manually set the dB cutoff levels
db_min = -50  # Minimum dB level
db_max = 50     # Maximum dB level

# Plot and save each spectrogram with consistent scaling
for filename in os.listdir(input_dir):
    if filename.endswith('.wav'):
        sample_rate, data = wavfile.read(os.path.join(input_dir, filename))
        f, t, Sxx = spectrogram(data, sample_rate)
        
        plt.figure(figsize=(15, 6))
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), vmin=db_min, vmax=db_max)
        plt.title(f'Spectrogram of {filename}')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.colorbar(label='Intensity [dB]')
        
        # Save the figure
        output_path = os.path.join(output_dir, f'{filename}_spectrogram.png')
        plt.savefig(output_path, dpi=300)
        plt.close()

print('Spectrograms have been saved successfully.')
