import matplotlib.pyplot as plt
import numpy as np
import pickle
from model import Manoeuvre

with open('Data_Dict_SIunits.pkl', 'rb') as pickle_file:
    Data_Dict = pickle.load(pickle_file)

def plot_phugoid_comparison(data_dict):
    phugoid = Manoeuvre(times=(3420, 3567), data_dict=Data_Dict)
    t = phugoid.get_times()
    q_phug = phugoid.get_q()
    #changee
    alpha_phug = phugoid.get_alpha()
    V_phug = phugoid.get_tas()
    theta_phug = phugoid.get_theta()

    y_sym, _ = phugoid(isPlot=True)
    print(y_sym.shape)


    fig, axs = plt.subplots(2, 2, figsize=(10, 10), sharey=False, sharex=False, layout='constrained')

    axs[0,0].plot(t, q_phug)

    plt.show()
plot_phugoid_comparison(data_dict=Data_Dict)

## Start of phugoid manoeuvre is t = 57 min
## P = 41.8 sec
## T_half = 192.259 sec
## Phugoid ends at index 35670


#35670
time = []
Theta = []
Max_thetas_index =[]
for i in range(34200,35670):
    Theta.append(Data_Dict['Ahrs1_Pitch'][i])
    time.append(i*0.1)
    if Data_Dict['Ahrs1_Pitch'][i] > Data_Dict['Ahrs1_Pitch'][i+1]:
        if Data_Dict['Ahrs1_Pitch'][i] > Data_Dict['Ahrs1_Pitch'][i-1]:
            Max_thetas_index.append(i)


Max_thetas_index.remove(Max_thetas_index[0])
print(Max_thetas_index)
P = (Max_thetas_index[1]-Max_thetas_index[0])*0.1
print(P)
decay_coeff = (Data_Dict['Ahrs1_Pitch'][Max_thetas_index[1]]-Data_Dict['Ahrs1_Pitch'][Max_thetas_index[0]])/P
T_half = -0.5*Data_Dict['Ahrs1_Pitch'][Max_thetas_index[0]]/decay_coeff
print(T_half)
plt.plot(time,Theta)
plt.show()



plt.plot(time,Theta)
plt.show()