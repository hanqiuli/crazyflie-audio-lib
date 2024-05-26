import pickle
import path_config as pc
import matplotlib.pyplot as plt
from Mass_calculator import Mass
import numpy as np
from math import pi

with open(pc.data_dict_path, 'rb') as pickle_file:
    Data_Dict_loaded = pickle.load(pickle_file)
def rho_calculation(P,T,R):
    rho = P/(R*T)
    return rho
def weight_calculation(W0,F_right,F_left):
    obj = Mass()
    return obj.NewMass_calculator()
def CL_coefficient(mi,rho,S,V_TAS):
    CL = mi*9.81/(1/2*rho*S*(V_TAS)**2)
    return CL
def pressure(T0,h,a,R,T1,P0,g):
    P1 = P0*(T1/T0)**(-g/(a*R))
    return P1
def CD_coefficient(T,rho,S,V_TAS):
    CD = T / (1 / 2 * rho * S * (V_TAS) ** 2)
    return CD
m0 = 6082.91
S = 30.00
R = 287
a = -6.5*10**(-3)
g = 9.80665
T0 = 288.15
P0 = 101325
A = 8.43866
CL = []
CD = []
Alpha = []
T = [7765.58,6171.79,5115.55,4033.19,4120.28,4107.64]
timestamps = [19*60, 21*60 + 25, 24*60 + 22, 26 * 60 + 18, 27*60 + 59, 29*60 + 47 ]
list_of_indexes = []
for i in timestamps:
    one_index = np.where(i == Data_Dict_loaded['time'])
    one_index = one_index[0][0] #+ 1
    list_of_indexes.append(one_index)

for i in list_of_indexes:
    pass
    #print(Data_Dict_loaded['vane_AOA'][i]*180/pi)
    #print(Data_Dict_loaded['Dadc1_bcAlt'][i])
    #print(Data_Dict_loaded['Dadc1_mach'][i])
    #print(Data_Dict_loaded['Dadc1_sat'][i])
    #print(Data_Dict_loaded['Dadc1_tas'][i])
    #print(Data_Dict_loaded['rh_engine_FMF'][i])

j = 0
for i in list_of_indexes:

    h = Data_Dict_loaded['Dadc1_bcAlt'][i]
    T1 = Data_Dict_loaded['Dadc1_sat'][i]
    P1 = pressure(T0, h, a, R, T1, P0, g)
    rho = rho_calculation(P1, T1, R)
    F_right = Data_Dict_loaded['rh_engine_FU'][i]
    F_left = Data_Dict_loaded['lh_engine_FU'][i]
    Weights_list = weight_calculation(m0,F_right,F_left)
    Wi = Weights_list[i]

    V_TAS = Data_Dict_loaded['Dadc1_tas'][i]
    Cl = CL_coefficient(Wi,rho,S,V_TAS)
    Cd = CD_coefficient(T[j], rho, S, V_TAS)
    CL.append(Cl)
    CD.append(Cd)
    Alpha.append(Data_Dict_loaded['vane_AOA'][i]*180/pi)
    j = j + 1
#print(CD)
#print(CL)

slope_cl, y =  np.polyfit(Alpha, CL, 1)
#print(slope_cl)
CLa = slope_cl

#plt.plot(CD, Alpha)
#plt.scatter(CD, Alpha)
#plt.grid()
#plt.show()

CL_squared = []
for i in range(0,len(CL)):
    CL_squared.append((CL[i])**2)


slope, y_intercept = np.polyfit(CL_squared, CD, 1)
e = 1/(pi*A*slope)
#print("e is" ,e)
#print("C_DO is",y_intercept)

print(f"e is =========> {e}")

