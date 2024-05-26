from scipy.signal import butter, filtfilt
import numpy as np
import matplotlib.pyplot as plt
import path_config
import pickle


def butter_low_pass_filter(data, cutoff, nyq, order):
    normal_cutoff = cutoff/nyq
    b, a = butter(order, normal_cutoff, btype='low', output='ba', analog=False, fs=nyq*2)
    y = filtfilt(b,a,data)
    return y

def filter_func(data_dict_unfiltered : dict):

    time_key = 'time'
    sampling_f = 1/(data_dict_unfiltered[time_key][1]-data_dict_unfiltered[time_key][0])
    nyq = sampling_f/2


    data_dict = {}
    for key in data_dict_unfiltered.keys() :
        if key==time_key:
            data_dict[key] = data_dict_unfiltered[key]
            continue


        data_dict[key] = butter_low_pass_filter(data_dict_unfiltered[key], 1, nyq, 2)


    return data_dict




with open(path_config.data_dict_unfiltered_path, 'rb') as datafile_unfiltered:
    data_dict_unfiltered = pickle.load(datafile_unfiltered)

data_dict = filter_func(data_dict_unfiltered)

plt.plot(data_dict['time'][34200:34600], data_dict_unfiltered['vane_AOA'][34200:34600])
plt.plot(data_dict['time'][34200:34600], data_dict['vane_AOA'][34200:34600])
plt.show()




with open(path_config.data_dict_path, 'wb') as datafile:
    pickle.dump(data_dict, datafile, protocol=pickle.HIGHEST_PROTOCOL)

