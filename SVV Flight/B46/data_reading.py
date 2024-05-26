import scipy.io
import os

# Load the .mat file
cwd = os.getcwd()
print(cwd)
mat_file_path = 'C:\\Users\\moheb\\Desktop\\Y3\\SVV Flight\\FTISxprt-20210808_143959.mat'
mat_data = scipy.io.loadmat(mat_file_path, struct_as_record=False, squeeze_me=True)

# Extract the 'flightdata' struct which contains the data
flightdata = mat_data['flightdata']

# Define a function to print variable names and descriptions
def print_variable_details(flightdata_struct):
    # Iterate over the fields in the struct
    for field in flightdata_struct._fieldnames:
        nested_struct = getattr(flightdata_struct, field)
        # If the nested struct has a 'description' field, print it
        if 'description' in nested_struct._fieldnames:
            print(f"Variable Name: {field}, Description: {nested_struct.description}, Unit: {nested_struct.units}")
        else:
            print(f"Variable Name: {field}, Description: Not available")

# Call the function to print the details
print_variable_details(flightdata)