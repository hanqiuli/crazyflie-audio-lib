from pydub import AudioSegment
import os

def split_audio(file_path, output_folder, segment_length=1000):
    # Load the audio file
    audio = AudioSegment.from_file(file_path)
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Split the audio into segments
    for i in range(0, len(audio), segment_length):
        segment = audio[i:i + segment_length]
        segment_name = os.path.join(output_folder, f"segment_{int(i/segment_length)}_noise.wav")
        segment.export(segment_name, format="wav")
        print(f"Exported {segment_name}")

# Example usage
file_path = "Recordings_DUMP/26_May_SwarmLab/NOISE_Trimmed.1.wav"  # Replace with your audio file path
output_folder = "Recordings_DUMP/26_May_SwarmLab/noise_split/"  # Replace with your desired output folder

split_audio(file_path, output_folder)