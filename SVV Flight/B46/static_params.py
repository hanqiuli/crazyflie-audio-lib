import CL_CD_curve as clcd
import elevator_trim_curve as eltrim
import numpy as np

import path_config

#CL CD
E =     clcd.e
Cd0 =   clcd.y_intercept
CLa =   clcd.CLa



#TODO change these times when switching to new data!!!!!
#ref data:

EQUILIBRIUM_TIMES = np.array([35, 37, 39, 41, 43, 44, 46]) * 60 #seconds
CG_SHIFT_TIMES = (48 * 60, 50 * 60)                             #seconds
'''
#our data
EQUILIBRIUM_TIMES = np.array([27*60+30, 29*60+10, 30*60+55, 32*60+25, 34*60+10, 35*60+19, 36*60+11, 37*60+24])  #seconds
CG_SHIFT_TIMES = (37*60+25, 40 * 60+25)                             #seconds
'''

#elevator trim curve
calculator = eltrim.Trim_Curve(data_file=path_config.data_dict_path)
dde_dalpha = calculator.calc_meas_elTrim(equilibrium_times = EQUILIBRIUM_TIMES, plot=False)

Cmde = calculator.calc_Cmde(times=CG_SHIFT_TIMES)
Cma = calculator.calc_Cmalpha(Cmde=Cmde, dde_dalpha=dde_dalpha)


#calculator.plot_reduced_elTrim(Cmde=Cmde, equilibrium_times=EQUILIBRIUM_TIMES)
#print(f'trim curve slope: dde_dalpha = {dde_dalpha}, elevator effectiveness: Cmde = {Cmde}, static stability: dCm/dalpha = {Cma}')
