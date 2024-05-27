import numpy as np
import soundfile as sf
import padasip as pa

# Function to calculate signal-to-noise ratio
def signaltonoise(a, axis=0, ddof=0):
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m / sd)

# Function to apply LMS filter on single audio file
def denoise_audio(noisy_audio_path, output_path):
    # Load the noisy audio
    noisy_audio, sr_noisy = sf.read(noisy_audio_path)
    
    # Ensure the audio is mono
    assert len(noisy_audio.shape) == 1, "Audio file is not mono"
    
    # Initialize the LMS filter
    n = 64  # Number of taps in the LMS filter
    lms_filter = pa.filters.FilterLMS(n=n, mu=0.01, w="zeros")
    
    # Prepare the input vector for the LMS filter
    N = len(noisy_audio) - n
    X = np.array([noisy_audio[i:i+n] for i in range(N)])
    d = noisy_audio[n:N+n]
    
    # Apply the LMS filter
    y, e, w = lms_filter.run(d, X)
    
    # 'e' contains the filtered signal (denoised audio)
    # Save the denoised audio
    enhanced_file_path = output_path
    sf.write(enhanced_file_path, e, sr_noisy)
    
    # Print SNR values
    print("Estimated Original SNR: ", signaltonoise(noisy_audio))
    print("Estimated Enhanced SNR: ", signaltonoise(e))

# Example usage
# noisy_audio_path = 'Recordings_DUMP/19_May_SwarmLab_RecordWhileFlying/Keyword_LEFT_Proper_clipped.wav'
noisy_audio_path = 'Recordings_DUMP/23_May_swarmingLab_3recordings/second_try.1.wav'
# output_path = 'Recordings_DUMP/19_May_SwarmLab_RecordWhileFlying/denoised_audio_LEFT_clipped.wav'
output_path = 'Recordings_DUMP/23_May_swarmingLab_3recordings/denoised_audio_second_try.1.wav'
denoise_audio(noisy_audio_path, output_path)