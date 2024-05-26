import numpy as np
import matplotlib.pyplot as plt
import pickle

import path_config
from Mass_calculator import Mass
import Cit_par24 as params
from sklearn.linear_model import LinearRegression
from thrust_dir.thrust_calculator import calc_thrust
#dict_keys(['vane_AOA', 'elevator_dte', 'column_fe', 'lh_engine_FMF', 'rh_engine_FMF', 'lh_engine_itt', 'rh_engine_itt', 'lh_engine_OP', 'rh_engine_OP', 'column_Se', 'lh_engine_fan_N1', 'lh_engine_turbine_N2', 'rh_engine_fan_N1', 'rh_engine_turbine_N2', 'lh_engine_FU', 'rh_engine_FU', 'delta_a', 'delta_e', 'delta_r', 'Gps_date', 'Gps_utcSec', 'Ahrs1_Roll', 'Ahrs1_Pitch', 'Fms1_trueHeading', 'Gps_lat', 'Gps_long', 'Ahrs1_bRollRate', 'Ahrs1_bPitchRate', 'Ahrs1_bYawRate', 'Ahrs1_bLongAcc', 'Ahrs1_bLatAcc', 'Ahrs1_bNormAcc', 'Ahrs1_aHdgAcc', 'Ahrs1_xHdgAcc', 'Ahrs1_VertAcc', 'Dadc1_sat', 'Dadc1_tat', 'Dadc1_alt', 'Dadc1_bcAlt', 'Dadc1_bcAltMb', 'Dadc1_mach', 'Dadc1_cas', 'Dadc1_tas', 'Dadc1_altRate', 'measurement_running', 'measurement_n_rdy', 'display_graph_state', 'display_active_screen', 'time'])


class Trim_Curve:
    def __init__(self, data_file: str):
        '''
        :param data_file: name of the data file to read into dict
        :param time_interval: start and end times
        '''
        with open(data_file, 'rb') as pickle_file:
            Data_Dict_loaded = pickle.load(pickle_file)


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

        self.mass = Mass().NewMass_calculator()                        # [kg]
        self.cg_pos, _ = Mass().CG_POS_PER_TIME()


        self.time = Data_Dict_loaded['time']                           # [s]

        self.Mach_meas = Data_Dict_loaded['Dadc1_mach']                # [-]
        self.V_c = Data_Dict_loaded['Dadc1_cas']                       # [m s^-1]
        self.V_t = Data_Dict_loaded['Dadc1_tas']                       # [m s^-1]
        self.T_m = Data_Dict_loaded['Dadc1_tat']                       # [K]
        self.h_p = Data_Dict_loaded['Dadc1_alt']                       # [m]
        self.T_stat = Data_Dict_loaded['Dadc1_sat']                    # [K]
        self.delta_e = Data_Dict_loaded['delta_e']                     # [rad]
        self.AOA = Data_Dict_loaded['vane_AOA']                        # [rad]
        self.lff = Data_Dict_loaded['lh_engine_FMF']                   # [kg s^-1]
        self.rff = Data_Dict_loaded['rh_engine_FMF']                   # [kg s^-1]

    @staticmethod
    def sort_array(array_to_sort, value_array):
        idx_sort = value_array.argsort()
        return array_to_sort[idx_sort[::-1]]

    @staticmethod
    def calc_grad(x, y):
        ' Calculate gradient of linear regression (x,y)'
        model = LinearRegression().fit(x, y)
        return model.coef_

    def calc_mach(self, p, V_c):
        '''
        Calculates mach number using that long thermodynamics equation
        :param p: stat. pressure
        :param V_c: calibrated a/s
        :return: mach number
        '''
        gamma = self.gamma

        inner_1 = (1 + (gamma - 1) / (2 * gamma) * self.rho_0 / self.p_0 * V_c ** 2) ** (gamma / (gamma - 1))
        inner_2 = (1 + (self.p_0 / p) * ((inner_1) - 1)) ** (0.4 / 1.4)
        M = np.sqrt(2 / (gamma - 1) * (inner_2 - 1))

        return M

    def calc_T(self, T_m, M):
        '''
        :param T_m: (measured) total Temp.
        :param M: mach number
        :return: static temp.
        '''
        T = T_m / (1 + (self.gamma - 1) / 2 * M * M)
        return T

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

        return V_e

    def reduce_V_e(self, V_e: np.array):
        '''
        :param V_e: equivalent airspeed
        :param Mass: aircraft mass
        :return:
        '''
        W = self.mass * self.g_0
        return V_e * np.sqrt(self.W_s/W)

    def plot_reduced_elTrim(self, equilibrium_times: np.ndarray, Cmde: float):

        sort_times = self.time.searchsorted(equilibrium_times)

        alpha = self.AOA[sort_times]
        d_e = self.delta_e[sort_times]
        T_stat = self.T_stat[sort_times]
        mach = self.Mach_meas[sort_times]
        lff = self.lff[sort_times]
        rff = self.rff[sort_times]
        h_p = self.h_p[sort_times]
        V_tas = self.V_t[sort_times]

        p = self.calc_pressure(h_p=h_p)
        rho = self.calc_rho(p=p, T=T_stat)

        T_isa = self.T_0 + self.lam*h_p
        dTemp = T_stat - T_isa

        data = {
            'h_p': h_p,
            'mach': mach,
            'T_difference': dTemp,
            'left_ff': lff,
            'right_ff': rff,
        }
        LT, RT = calc_thrust(data=data)
        T = LT+RT
        CT = T/(1/2*rho*V_tas*V_tas*params.S)

        data_s = {
            'h_p': h_p,
            'mach': mach,
            'T_difference': dTemp,
            'left_ff': self.mfs*np.ones_like(h_p),
            'right_ff': self.mfs*np.ones_like(h_p),
        }

        LTs, RTs = calc_thrust(data=data_s)
        Ts = LTs + RTs

        CTs = Ts / (1 / 2 * rho * V_tas * V_tas * params.S)

        delta_e_stars = d_e - 1/Cmde * self.CmTc * (CTs - CT)
        V_e = self.calc_V_e_direct()
        V_e_red = self.reduce_V_e(V_e=V_e)[sort_times]

        m = self.calc_grad(alpha[:,np.newaxis], delta_e_stars[:, np.newaxis])

        plt.plot(V_e_red, delta_e_stars, linestyle='', marker='o', markersize=3, color='k', label=f"m={m[0,0]:.5f}")

        plt.xlabel(r"$\tilde{V_e}\;\; [ms^{-1}]$")
        plt.ylabel(r"$\delta_e^*$ [rad]")
        plt.gca().invert_yaxis()
        plt.legend()
        plt.tight_layout()
        plt.show()

    def calc_meas_elTrim(self, equilibrium_times : np.ndarray, plot:bool = True):
        '''
        :return: d(delta_e) / d(alpha)
        '''
        alpha = self.AOA
        d_e = self.delta_e

        ordered_alpha = self.sort_array(array_to_sort=alpha, value_array=self.time)
        ordered_d_e = self.sort_array(array_to_sort=d_e, value_array=self.time)

        d_e_measTime = d_e[self.time.searchsorted(equilibrium_times)]
        alpha_measTime = alpha[self.time.searchsorted(equilibrium_times)]

        start_time, end_time = equilibrium_times[0], equilibrium_times[-1]
        indices = (self.time>=start_time) & (self.time<=end_time)

        m = self.calc_grad(ordered_alpha[indices][:, np.newaxis], ordered_d_e[indices][:, np.newaxis])[0][0]
        m_measTime = self.calc_grad(alpha_measTime[:, np.newaxis], d_e_measTime[:, np.newaxis])[0][0]
        if plot:
            plt.plot(ordered_alpha[indices], ordered_d_e[indices], linestyle='', marker='o', markersize=1, color='k', label=f"{m:.4f}")
            plt.plot(alpha_measTime, d_e_measTime, linestyle='-', marker='x', markersize=6, linewidth=.75, color='red',label=f"{m_measTime:.4f}")

            plt.xlabel(r"$\alpha$ [rad]")
            plt.ylabel(r"$\delta_e$ [rad]")
            plt.gca().invert_yaxis()
            plt.legend()
            plt.tight_layout()
            plt.show()

        return m_measTime

    def calc_Cmde(self, times: tuple):
        '''
        :param dxcg: cg excursion
        :return: Cm_delta
        '''

        start_time, end_time = times
        dxcg = (self.cg_pos[np.where(self.time==end_time)] - self.cg_pos[np.where(self.time==start_time)])[0]

        delta_start = self.delta_e[self.time.searchsorted(start_time)]
        delta_end = self.delta_e[self.time.searchsorted(end_time)]
        delta_d_e = delta_end-delta_start

        CN = self.calc_Cn(times[0])
        cBar = params.c
        Cmde = -1/delta_d_e * CN * dxcg/cBar

        return Cmde

    def calc_Cmalpha(self, Cmde, dde_dalpha):
        '''
        :param Cmde: Cm_delta
        :return: Cm_alpha
        '''
        Cmalpha = -Cmde*dde_dalpha
        return Cmalpha

    def calc_Cn(self, equilibrium_time : float):
        """
        Calculates the normal force coefficient (Cn) at a certain time, assuming aircraft is flying in equilibrium
        :param equilibrium_time: (float) time at which aircraft is in equilibrium and the (Cn) needs to be calculated
        :return: Cn (normal force coefficient)
        """

        index = self.time.searchsorted(equilibrium_time)
        rho = self.calc_rho(self.calc_pressure(self.h_p[index]), self.T_stat[index])

        return (self.mass[index] * self.g_0) / (0.5 * rho * self.V_t[index] * self.V_t[index] * params.S)

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


if __name__ == "__main__":
    mTimes = np.array([35, 37, 39, 41, 43, 44, 46]) * 60.
    calculator = Trim_Curve(data_file=path_config.data_dict_path)
    dde_dalpha = calculator.calc_meas_elTrim(equilibrium_times = mTimes)
    #TODO set dxcg to correct value
    Cmde = calculator.calc_Cmde(times=(48 * 60, 50 * 60))
    Cmalpha = calculator.calc_Cmalpha(Cmde=Cmde, dde_dalpha=dde_dalpha)
    calculator.plot_reduced_elTrim(Cmde=Cmde, equilibrium_times=mTimes)
    print(f'trim curve slope: dde_dalpha = {dde_dalpha}, elevator effectiveness: Cmde = {Cmde}, static stability: dCm/dalpha = {Cmalpha}')

