import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata


def plot_snr_surface(all_snrs, heights, distances):
    """Plot a 3D surface of mean SNR values."""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Create data arrays for heights, distances, and mean SNRs
    X, Y, Z = [], [], []
    for dist in distances:
        for height in heights:
            X.append(dist)
            Y.append(height)
            Z.append(np.mean(all_snrs[dist][height]))

    # Convert lists to numpy arrays
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)

    # Create grid for surface plot
    xi = np.linspace(min(X), max(X), num=100)
    yi = np.linspace(min(Y), max(Y), num=100)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((X, Y), Z, (xi, yi), method='cubic')

    # Plot the surface
    surf = ax.plot_surface(xi, yi, zi, cmap='viridis', linewidth=0, antialiased=False)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

    ax.set_xlabel('In-plane Distance (m)')
    ax.set_ylabel('Height (y/R)')
    ax.set_zlabel('Mean SNR (dB)')
    plt.title("3D Surface Plot of Mean SNR across Heights and Distances")
    plt.show()

if __name__ == "__main__":
    heights = [0, 1, 2, 3, 4, 5, 6, 7]  # Heights to process
    distances = [0.1, 0.2, 0.3]  # Example in-plane distances

    # Generate random SNR data for each height and distance
    all_snrs = {dist: {height: generate_random_snr_data(10) for height in heights} for dist in distances}

    plot_snr_surface(all_snrs, heights, distances)
