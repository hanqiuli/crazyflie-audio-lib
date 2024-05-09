import os
import numpy as np
import librosa
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def calculate_power_spectra(signal):
    """Calculate the power spectrum of a signal using FFT."""
    fft_signal = np.fft.fft(signal)
    power_spectrum = np.abs(fft_signal) ** 2
    return power_spectrum

def calculate_snr(clean_signal, noisy_signal):
    """Calculate the average spectral SNR."""
    min_length = min(len(clean_signal), len(noisy_signal))
    clean_signal = clean_signal[:min_length]
    noisy_signal = noisy_signal[:min_length]
    
    power_spectrum_clean = calculate_power_spectra(clean_signal)
    power_spectrum_noisy = calculate_power_spectra(noisy_signal)

    # Avoid division by zero and negative values in SNR computation
    power_spectrum_noisy[power_spectrum_noisy <= 0] = 1e-10
    power_spectrum_clean[power_spectrum_clean <= 0] = 1e-10

    snr_spectrum = 10 * np.log10(power_spectrum_clean / power_spectrum_noisy)
    mean_snr = np.mean(snr_spectrum)
    return mean_snr

def calculate_all_snrs(clean_signal_path, noisy_signals_directory):
    """Calculate SNRs for all .wav files in a given directory."""
    snrs = []
    filenames = []

    clean_signal, sr_clean = librosa.load(clean_signal_path, sr=None)
    for filename in os.listdir(noisy_signals_directory):
        if filename.endswith(".wav"):
            full_path = os.path.join(noisy_signals_directory, filename)
            try:
                noisy_signal, sr_noisy = librosa.load(full_path, sr=None)
                snr = calculate_snr(clean_signal, noisy_signal)
                snrs.append(snr)
                filenames.append(filename)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
    return snrs, filenames

def plot_all_snrs(all_snrs, labels, title, show_plot=False):
    """Plot all SNR distributions on a single axis with custom x-axis labels."""
    plt.figure(figsize=(12, 6))  # Adjust size as needed
    # Plot all SNRs on the same axes
    positions = range(1, len(all_snrs) + 1)  # Position each box plot
    plt.boxplot(all_snrs, vert=True, patch_artist=True, positions=positions)
    
    # Set x-axis labels
    plt.xticks(positions, labels)  # Set custom labels for each boxplot
    plt.title(title)
    plt.ylabel("SNR (dB)")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("SNR_Plots/" + title.replace(' ', '_').replace('/', '-') + ".png")
    if show_plot:
        plt.show()
    plt.close()

def plot_snr_contour(snr_dict, title, show_plot=False):
    """Plot a 2D contour map of mean SNR values with smooth interpolation."""
    # Create sorted lists of heights and custom mapping for distances with 'orig' represented by a specific value
    heights = sorted(snr_dict['orig'].keys())
    distances = sorted([key for key in snr_dict.keys() if key != 'orig'])
    distance_values = [1.7647] + [float(d) for d in distances]  # Replace distances with numerical values as needed

    # Preparing data for interpolation
    points = []  # (distance, height) pairs
    values = []  # SNR values
    for i, distance in enumerate(['orig'] + distances):
        for j, height in enumerate(heights):
            if snr_dict[distance][height]:
                mean_snr = np.mean(snr_dict[distance][height])
                points.append((distance_values[i], height))
                values.append(mean_snr)

    # Converting lists to numpy arrays
    points = np.array(points)
    values = np.array(values)

    # Create grid data for interpolation
    grid_x, grid_y = np.meshgrid(
        np.linspace(min(distance_values), max(distance_values), 100),
        np.linspace(min(heights), max(heights), 100)
    )

    # Interpolate using griddata
    grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

    # Plotting the contour plot
    plt.figure(figsize=(10, 8))
    contourf = plt.contourf(grid_x, grid_y, grid_z, levels=20, cmap='plasma')
    plt.colorbar(contourf, label='Mean SNR (dB)')
    plt.title(title)
    plt.xlabel('Arm Length [x/R]')
    plt.ylabel('Height [y/R]')
    plt.grid(True)

    # Optional: Add contour lines to highlight levels
    plt.contour(grid_x, grid_y, grid_z, levels=20, colors='k', linestyles='solid', linewidths=0.3)
    
    plt.savefig("SNR_Plots/contour_plot.png")
    if show_plot:
        plt.show()
    plt.close()


def plot_snr_surface(snr_dict, title, show_plot=False):
    """Plot a 3D surface map of mean SNR values with smooth interpolation."""
    # Create sorted lists of heights and custom mapping for distances with 'orig' represented by a specific value
    heights = sorted(snr_dict['orig'].keys())
    distances = sorted([key for key in snr_dict.keys() if key != 'orig'])
    distance_values = [1.7647] + [float(d) for d in distances]  # Replace distances with numerical values as needed

    # Preparing data for interpolation
    points = []  # (distance, height) pairs
    values = []  # SNR values
    for i, distance in enumerate(['orig'] + distances):
        for j, height in enumerate(heights):
            if snr_dict[distance][height]:
                mean_snr = np.mean(snr_dict[distance][height])
                points.append((distance_values[i], height))
                values.append(mean_snr)

    # Converting lists to numpy arrays
    points = np.array(points)
    values = np.array(values)

    # Create grid data for interpolation
    grid_x, grid_y = np.meshgrid(
        np.linspace(min(distance_values), max(distance_values), 100),
        np.linspace(min(heights), max(heights), 100)
    )

    # Interpolate using griddata
    grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')

    # Set up a 3D plot
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(grid_x, grid_y, grid_z, cmap='plasma', edgecolor='none')
    fig.colorbar(surf, ax=ax, label='Mean SNR (dB)', shrink=0.5, aspect=5)

    ax.set_title(title)
    ax.set_xlabel('Arm Length [x/R]')
    ax.set_ylabel('Height [y/R]')
    ax.set_zlabel('Mean SNR (dB)')

    plt.savefig("SNR_Plots/3D_surface_plot.png")
    if show_plot:
        plt.show()
    plt.close()

if __name__ == "__main__":
    heights = [0, 1, 2, 3, 4, 5, 6, 7]  # Heights to process
    distances = [2, 3, 4]
    labels_heights = [f"{height} [y/R]" for height in heights]  # Custom labels for each boxplot
    labels_distances = ['orig'] + [f"{distance} [x/R]" for distance in distances]

    snr_dict = {distance: {height: [] for height in heights} for distance in distances}
    snr_dict['orig'] = {height: [] for height in heights}

    clean_signal_path = "Final_RECORDINGS/Clean_Keywords/No_Shroud/Clean.clean.1.wav.4t42velb.ingestion-54fbc688b-qbw86.s9.wav"

    for height in heights:
        # first process original arm length
        noisy_signals_directory = f"Final_RECORDINGS/Height_{height}/Original_Arm/"
        snrs, filenames = calculate_all_snrs(clean_signal_path, noisy_signals_directory)
        snr_dict['orig'][height] = snrs
        print(f"Processed {len(snrs)} files for height {height} and original arm length")
        for distance in distances:
            try:
                noisy_signals_directory = f"Final_RECORDINGS/Height_{height}/Arm_{distance}_Height_{height}/"
                snrs, filenames = calculate_all_snrs(clean_signal_path, noisy_signals_directory)
                snr_dict[distance][height] = snrs
                print(f"Processed {len(snrs)} files for height {height} and arm length {distance}")
            except Exception as e:
                print(f"Failed to process height {height} and arm length {distance}: {e}")

    # Now we plot the SNR distributions
    # First, plot the SNR distributions for each height, varying arm length

    for height in heights:
        snrs = [snr_dict['orig'][height]] + [snr_dict[distance][height] for distance in distances]
        plot_all_snrs(snrs, labels_distances, f"SNR Distribution for Height {height} [y/R]")
    
    # Next, plot the SNR distributions for each arm length, varying height
    # first the original arm length
    snrs = [snr_dict['orig'][height] for height in heights]
    plot_all_snrs(snrs, labels_heights, f"SNR Distribution for Original Arm Length x/R")
    for distance in distances:
        snrs = [snr_dict[distance][height] for height in heights]
        plot_all_snrs(snrs, labels_heights, f"SNR Distribution for Arm Length {distance} [x/R]")

    # Finally, plot a heatmap of mean SNR values
    plot_snr_contour(snr_dict, "Mean SNR Values for Different Arm Lengths and Heights")
    plot_snr_surface(snr_dict, "Mean SNR Values for Different Arm Lengths and Heights", show_plot=True)