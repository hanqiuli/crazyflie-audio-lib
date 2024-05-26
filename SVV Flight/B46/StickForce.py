
import numpy as np
import matplotlib.pyplot as plt
import pickle
from Mass_calculator import Mass
import Cit_par24 as params
from sklearn.linear_model import LinearRegression



class StickForce:
    def __init__(self, data_file: str, time_interval: tuple):
        '''
        :param data_file: name of the data file to read into dict
        :param time_interval: start and end times
        '''
        with open(data_file, 'rb') as pickle_file:
            Data_Dict_loaded = pickle.load(pickle_file)
        print(Data_Dict_loaded.keys())

        self.T_0 = params.Temp0 #[K]
        self.lam = params.lamb # [K m^-1]
        self.p_0 = params.p0 # [Pa]
        self.g_0 = params.g # [m s^-2]
        self.R = params.R #[J kg^-1 K^-1]
        self.rho_0 = params.rho0 #[kg m^-3]
        self.W_s = 60500 #[n]
        self.gamma = 1.4 #[]
        self.mfs = 0.048 # [kg s^-1]
        self.CmTc = params.CmTc

        self.t_start, self.t_end = time_interval
        self.mass = Mass().NewMass_calculator()                        # [kg]

        self.time = Data_Dict_loaded['time']                           # [s]
        self.Mach_meas = Data_Dict_loaded['Dadc1_mach']                # [-]
        self.V_c = Data_Dict_loaded['Dadc1_cas']# * 0.514444444         # [m s^-1]
        self.V_t = Data_Dict_loaded['Dadc1_tas']# * 0.514444444         # [m s^-1]
        self.T_m = Data_Dict_loaded['Dadc1_tat']#+274.15                # [K]
        self.h_p = Data_Dict_loaded['Dadc1_alt']#*.3048                 # [m]
        self.T_stat = Data_Dict_loaded['Dadc1_sat']#+274.15             # [K]
        self.delta_e = Data_Dict_loaded['delta_e']#*np.pi/180           # [rad]
        self.AOA = Data_Dict_loaded['vane_AOA']#*np.pi/180              # [rad]
        self.lff = Data_Dict_loaded['lh_engine_FMF']#*.453592/3600      # [kg s^-1]
        self.rff = Data_Dict_loaded['rh_engine_FMF']#*.453592/3600      # [kg s^-1]

    @staticmethod
    def sort_array(array_to_sort, value_array):
        idx_sort = value_array.argsort()
        return array_to_sort[idx_sort[::-1]]

    @staticmethod
    def calc_grad(x, y):
        ' Calculate gradient of linear regression (x,y)'
        model = LinearRegression().fit(x, y)
        return model.coef_

    def calc_rho(self, p: np.array, T: np.array):
        '''
        :param p: static pressure
        :param T: static temperature
        :return: density from ideal gas law
        '''
        rho = p / (self.R * T)
        return rho

    def calc_pressure(self, h_p: np.array):
        '''
        :param h_p: pressure altitude
        :return: static pressure
        '''
        p = self.p_0 * (1 + self.lam * h_p / self.T_0) ** (-self.g_0 / (self.lam * self.R))
        return p

    def calc_V_e_direct(self):
        '''
        :return: equivalent airspeed from measured TAS
        '''
        p = self.calc_pressure(h_p = self.h_p)
        rho = self.calc_rho(p=p, T = self.T_stat)
        V_e = self.V_t*np.sqrt(rho/self.rho_0)
        # print(f"Pressure => {p}")
        # print(10*"-")
        # print(f"rho is {rho}")
        # print(10*"-")
        # print(f"self.T_stat => {self.T_stat}")
        # print(10*"-")
        # print(f"Ve => {V_e}")
        # print(10*"-")
        # print(f"Ve => {self.V_t}")
        return V_e

    def reduce_V_e(self, V_e: np.array):
        '''
        :param V_e: equivalent airspeed
        :param Mass: aircraft mass
        :return:
        '''
        W = self.mass * self.g_0
        print(f"Wieght is {W}")
        return V_e * np.sqrt(self.W_s/W)

    

    def plot_checks(self):
        'manually recorded data:'
        time_man_arr = np.array([35, 37, 39, 41, 43, 44, 46]) * 60  # [s]
        h_p_man_arr = np.array([13070, 13400, 13770, 14176, 13512, 13184, 12454]) * .3048  # [m]
        T_m_man_arr = np.array([-11.5, -12.5, -13.8, -15.2, -12, -10.5, -8.2]) + 274.15  # [K]
        V_c_man_arr = np.array([157.8, 148, 138, 132, 170.4, 179, 189.6]) * 0.514444444  # [m s^-1]
        delta_e_man_arr = np.array([0.1, -0.233333333, -0.7, -1, 0.6, 0.8, 1.1])*np.pi/180   #[rad]

        'plot checks:'
        plt.plot(self.time, self.delta_e)
        plt.plot(time_man_arr, delta_e_man_arr)
        plt.show()

        plt.plot(time_man_arr, h_p_man_arr)
        plt.plot(self.time, self.h_p)
        plt.show()

        plt.plot(time_man_arr, T_m_man_arr)
        plt.plot(self.time, self.T_m)
        plt.show()

        plt.plot(time_man_arr, V_c_man_arr)
        plt.plot(self.time, self.V_c)
        plt.show()


mTimes = np.array([35, 37, 39, 41, 43, 44, 46]) * 60.
Fe = np.array([-1, -13.5, -31.5, -38, 29, 47.5, 75.5])
calculator = StickForce(data_file='Data_Dict_SIunits.pkl', time_interval=(35*60, 46*60))


Ve = calculator.calc_V_e_direct()
print(f"Equivalent airspeed => {Ve[10000:50000]}")
reduced_ve = calculator.reduce_V_e(Ve)
print(f"Reduced Equivalent airspeed => {reduced_ve[10000:50000]}")
weights = calculator.mass



with open('Data_Dict_SIunits.pkl', 'rb') as pickle_file:
    Data_Dict_loaded = pickle.load(pickle_file)



timestamps = [35*60, 37*60, 39*60, 41*60, 43*60, 44*60, 46*60]
list_of_indexes = []
for i in timestamps:
    one_index = np.where(i == Data_Dict_loaded['time'])
    one_index = one_index[0][0] #+ 1
    list_of_indexes.append(one_index)





weights_in_timestamps = []



for index in list_of_indexes:
    weights_in_timestamps.append(weights[index])



weights_in_timestamps = [weight * 9.80665 for weight in weights_in_timestamps]


reduced_ve_in_timestamps = [] 


for index in list_of_indexes:
    reduced_ve_in_timestamps.append(reduced_ve[index]) 




W_s = calculator.W_s

def Fe_aero_reduced():
    F_red = Fe*([W_s] * 7)/weights_in_timestamps
    return F_red


#plotting
F_red = Fe_aero_reduced()


F_red


reduced_ve_in_timestamps


# plt.plot(reduced_ve_in_timestamps, F_red)
# plt.show()

reduced_ve_in_timestamps = np.array(reduced_ve_in_timestamps)
F_red = np.array(F_red)

# Sort the data by the independent variable (x data)
sorted_indices = np.argsort(reduced_ve_in_timestamps)
sorted_x = reduced_ve_in_timestamps[sorted_indices]
sorted_y = F_red[sorted_indices]

# Plot the sorted data
plt.plot(sorted_x, sorted_y, marker='o')
plt.xlabel('Reduced Equivalent Airspeed (m/s)')
plt.ylabel('Reduced Control Force (N)')

plt.show()



