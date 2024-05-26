import librosa
import numpy as np
import matplotlib.pyplot as plt

def extract_mfcc(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return mfccs

def plot_mfcc(mfccs):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(mfccs, x_axis='time')
    plt.colorbar()
    plt.title('MFCC')
    plt.tight_layout()
    plt.show()

# Example usage
# audio_path = 'Recordings_DUMP/19_May_SwarmLab_RecordWhileFlying/denoised_audio_LEFT_trim1.wav'
audio_path = 'Recordings_DUMP/19_May_SwarmLab_RecordWhileFlying/Keyword_RISE_Clean.wav'
mfccs = extract_mfcc(audio_path)
plot_mfcc(mfccs)