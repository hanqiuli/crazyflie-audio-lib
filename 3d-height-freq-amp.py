import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft
from collections import defaultdict
from matplotlib import cm

# Define the folder path
folder_path = 'overlay_noise_folder'

# Initialize dictionaries to store data based on the prefix
categories = defaultdict(lambda: {'heights': [], 'freqs_list': [], 'amplitudes_list': []})

# Function to aggregate frequency bins
def aggregate_bins(frequencies, amplitudes, bin_size, cutoff=None):
    if cutoff is not None:
        cutoff_indices = frequencies <= cutoff
        frequencies = frequencies[cutoff_indices]
        amplitudes = amplitudes[:, cutoff_indices]
    
    max_freq = frequencies[-1]
    binned_freqs = np.arange(0, max_freq + bin_size, bin_size)
    binned_amplitudes = np.zeros((len(amplitudes), len(binned_freqs) - 1))
    
    for i in range(len(binned_freqs) - 1):
        indices = np.where((frequencies >= binned_freqs[i]) & (frequencies < binned_freqs[i + 1]))[0]
        if indices.size > 0:
            binned_amplitudes[:, i] = np.mean(amplitudes[:, indices], axis=1)
    
    return binned_freqs[:-1], binned_amplitudes

# Function to convert amplitude to decibels
def amplitude_to_decibels(amplitude):
    amplitude[amplitude < 1e-7] = 1e-7  # Prevent log(0)
    return 20 * np.log10(amplitude)

# Read each file and perform FFT
files = sorted(os.listdir(folder_path))
for file in files:
    if not file.endswith('.wav'):
        continue
    prefix = file.split('_')[0]
    height = float(file.split('_')[1].replace('.wav', ''))
    
    sample_rate, data = wavfile.read(os.path.join(folder_path, file))
    n = len(data)
    fft_values = fft(data)
    amplitude = 2/n * np.abs(fft_values[:n//2])
    freqs = np.fft.fftfreq(n, d=1/sample_rate)[:n//2]
    
    categories[prefix]['heights'].append(height)
    categories[prefix]['freqs_list'].append(freqs)
    categories[prefix]['amplitudes_list'].append(amplitude)

bin_size = 500  # Hz

for prefix, data in categories.items():

    # Sort the heights for consistent plotting
    sorted_indices = np.argsort(data['heights'])
    sorted_heights = np.array(data['heights'])[sorted_indices]

    # Create a colormap for the heights
    norm = plt.Normalize(sorted_heights.min(), sorted_heights.max())
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
    sm.set_array([])

    # Overlayed FFTs for each height in Amplitude
    fig, ax = plt.subplots(figsize=(12, 8))
    for index in sorted_indices:
        freqs = data['freqs_list'][index]
        amplitudes = data['amplitudes_list'][index]
        label = f'Height: {data["heights"][index]}mm'
        ax.plot(freqs, amplitudes, label=label, color=sm.to_rgba(data['heights'][index]))
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'{prefix} - Overlayed FFTs (Amplitude)')
    ax.legend()
    plt.colorbar(sm, ax=ax, label='Height (mm)')
    plt.show()

    # Overlayed FFTs for each height in Decibels
    fig, ax = plt.subplots(figsize=(12, 8))
    for index in sorted_indices:
        freqs = data['freqs_list'][index]
        decibels = amplitude_to_decibels(data['amplitudes_list'][index])  # Convert to decibels
        label = f'Height: {data["heights"][index]}mm'
        ax.plot(freqs, decibels, label=label, color=sm.to_rgba(data['heights'][index]))
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Decibels (dB)')
    ax.set_title(f'{prefix} - Overlayed FFTs (Decibels)')
    ax.legend()
    plt.colorbar(sm, ax=ax, label='Height (mm)')
    plt.show()

    unique_heights = sorted(np.unique(data['heights']))
    original_freqs = np.array(data['freqs_list'][0])

    all_amplitudes = np.stack(data['amplitudes_list'], axis=0)
    all_decibels = amplitude_to_decibels(all_amplitudes)

    # Aggregate the frequency bins without any cutoff
    binned_freqs, binned_amplitudes = aggregate_bins(original_freqs, all_amplitudes, bin_size)
    _, binned_decibels = aggregate_bins(original_freqs, all_decibels, bin_size)

    # Aggregate the frequency bins with a 5kHz cutoff
    binned_freqs_cutoff, binned_amplitudes_cutoff = aggregate_bins(original_freqs, all_amplitudes, bin_size, cutoff=5000)
    _, binned_decibels_cutoff = aggregate_bins(original_freqs, all_decibels, bin_size, cutoff=5000)

    # Plot amplitude and decibel heat maps
    for binned_data, title_suffix in [(binned_amplitudes, "Amplitude"), (binned_decibels, "Decibels")]:
        fig, ax = plt.subplots(figsize=(12, 8))
        c = ax.pcolormesh(binned_freqs, unique_heights, binned_data, shading='auto', cmap='Reds_r')
        ax.set_title(f'{prefix} - {title_suffix} Heat Map with Aggregated Frequency Bins')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Height (mm)')
        fig.colorbar(c, ax=ax, label=title_suffix)
        plt.show()

    # Plot cutoff amplitude and decibel heat maps
    for binned_data, title_suffix in [(binned_amplitudes_cutoff, "Amplitude (Cutoff 5kHz)"), (binned_decibels_cutoff, "Decibels (Cutoff 5kHz)")]:
        fig, ax = plt.subplots(figsize=(12, 8))
        c = ax.pcolormesh(binned_freqs_cutoff, unique_heights, binned_data, shading='auto', cmap='Reds_r')
        ax.set_title(f'{prefix} - {title_suffix} Heat Map with Aggregated Frequency Bins')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Height (mm)')
        fig.colorbar(c, ax=ax, label=title_suffix)
        plt.show()
