import os.path
import pickle

abs_project_path = os.path.abspath(os.path.dirname(__file__))
data_dict_unfiltered_path = abs_project_path + "\Data_dict_SIunits.pkl"

#data_dict_path = abs_project_path + "\Data_dict_SIunits_filtered.pkl"

data_dict_path = abs_project_path + "\Data_dict_SIunits.pkl"

print(f'Data dictionary path = {data_dict_path}')



