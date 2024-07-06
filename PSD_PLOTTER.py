import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import welch

# Set the input and output directories
input_dir = 'individual_plotting/soundfiles/'
output_dir = 'individual_plotting/psd_figs/'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Create a new figure for the PSD plot
plt.figure(figsize=(15, 6))

# Plot each PSD
for filename in os.listdir(input_dir):
    if filename.endswith('.wav'):
        sample_rate, data = wavfile.read(os.path.join(input_dir, filename))
        
        data = data - np.mean(data)
        
        # Calculate PSD using Welch's method
        f, Pxx = welch(data, sample_rate, nperseg=1024)
        
        # Plot the PSD
        plt.semilogy(f, Pxx, label=filename)

# Customize the plot
plt.title('Power Spectral Density of Audio Files')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Power/Frequency [dB/Hz]')
plt.legend()
plt.grid(True)

# Save the figure
output_path = os.path.join(output_dir, 'combined_psd_plot.png')
plt.savefig(output_path, dpi=300)
plt.close()

print('PSD plot has been saved successfully.')
