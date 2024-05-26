import path_config
from Mass_calculator import Mass
import pickle
with open(path_config.data_dict_path, 'rb') as pickle_file:
    Data_Dict_loaded = pickle.load(pickle_file)

def weight_calculation(W0,F_right,F_left):
    obj = Mass()
    return obj.NewMass_calculator()

W0 = 6082.91    
F_right = Data_Dict_loaded['rh_engine_FU']
F_left = Data_Dict_loaded['lh_engine_FU']
Weights_list = weight_calculation(W0,F_right,F_left)
print(Weights_list)

time = Data_Dict_loaded['time']
print(len(time))