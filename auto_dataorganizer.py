import os
import shutil

# Define the source directory
source_dir = 'Final_RECORDINGS/Final_Recordings_4Jun/SPLIT/'
target_dir = 'Final_RECORDINGS/Final_SNR_Recordings/Shroud/'

heights = [0, 0.3, 0.6, 1, 1.3, 1.6, 2, 2.3, 2.6, 3, 3.3, 3.6, 4, 4.3, 4.6, 5]  # Heights to process
distances = [1, 2, 2.3, 2.6, 3, 3.3, 3.6, 4] # distances to process

destination_paths = {}

# Create destination directories for each combination of height and distance
for height in heights:
    for distance in distances:
        heightstring = str(height).replace('.', ',')
        distancestring = str(distance).replace('.', ',')
        prefix = f'{distancestring}_{heightstring}'
        if distance == 1:
            # original arm length
            destination_paths[prefix] = target_dir + f'Height_{height}/ArmOrig'
        else:
            destination_paths[prefix] = target_dir + f'Height_{height}/Arm{distance}'


# Ensure all destination directories exist
for path in destination_paths.values():
    os.makedirs(path, exist_ok=True)

# Loop through all files in the source directory
for filename in os.listdir(source_dir):
    if os.path.isfile(os.path.join(source_dir, filename)):
        # Get the prefix of the filename up to the first dot
        prefix = filename.split('.')[0]
        
        # if prefix starts with s_, then it is a shroud file
        if prefix.startswith('s_'):
            prefix = prefix[2:]
        else:
            continue

        # Check if the prefix is in the destination_paths dictionary
        if prefix in destination_paths:
            # Define the full source and destination paths
            source_file = os.path.join(source_dir, filename)
            destination_file = os.path.join(destination_paths[prefix], filename)

            # Print to check the paths
            print(f'Moving {source_file} to {destination_file}')
            
            # Move the file to the corresponding directory
            shutil.move(source_file, destination_file)
            print(f'Moved {filename} to {destination_paths[prefix]}')

print('File moving process completed.')
