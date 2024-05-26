import control
import path_config
import numpy as np
import matplotlib.pyplot as plt
from Cit_Par_Dynamic import Cit_Par as par_dyn
from Mass_calculator import Mass
import statespace as sim
import pickle


class Manoeuvre:
    def __init__(self, times: tuple, data_dict : dict):
        """
        :param times: to slice the data_dict
        :param data_dict: dictionary containing data with keys ['vane_AOA', 'elevator_dte', 'column_fe', 'column_Se', 'delta_a', 'delta_e', 'delta_r', 'Gps_date', 'Gps_utcSec', 'Ahrs1_Roll', 'Ahrs1_Pitch', 'Fms1_trueHeading', 'Gps_lat', 'Gps_long', 'Ahrs1_bRollRate', 'Ahrs1_bPitchRate', 'Ahrs1_bYawRate', 'Ahrs1_bLongAcc', 'Ahrs1_bLatAcc', 'Ahrs1_bNormAcc', 'Ahrs1_aHdgAcc', 'Ahrs1_xHdgAcc', 'Ahrs1_VertAcc', 'Dadc1_sat', 'Dadc1_tat', 'Dadc1_alt', 'Dadc1_bcAlt', 'Dadc1_bcAltMb', 'Dadc1_mach', 'Dadc1_cas', 'Dadc1_tas', 'Dadc1_altRate', 'measurement_running', 'measurement_n_rdy', 'display_graph_state', 'display_active_screen', 'time'])
        """
        self.t_0, self.t_1 = times
        indices = (data_dict['time']>=self.t_0) & (data_dict['time']<=self.t_1)

        self.data = {key : data_dict[key][indices] for key in data_dict.keys()}

        self.mass = Mass().NewMass_calculator()[indices]

        self.hp0 = self.data['Dadc1_alt'][0]
        self.V0 = self.get_tas()[0]
        self.alpha0 = self.get_alpha()[0]
        self.th0 = self.get_theta()[0]
        self.mass0 = self.mass[0]

        self.dynamic_params = par_dyn(hp0 = self.hp0, V0 = self.V0, alpha0=self.alpha0, th0=self.th0, mass=self.mass0)

        self.ss_sym = sim.ss_sym(par = self.dynamic_params)
        self.ss_asym = sim.ss_asym(par = self.dynamic_params)

    def get_times(self):
        return self.data['time']

    def get_delta_e(self):
        return self.data['delta_e']

    def get_delta_a(self):
        return self.data['delta_a']

    def get_delta_r(self):
        return self.data['delta_r']

    def get_tas(self):
        return self.data['Dadc1_tas']

    def get_alpha(self):
        return self.data['vane_AOA']

    def get_theta(self):
        return self.data['Ahrs1_Pitch']

    def get_q(self):
        return self.data['Ahrs1_bPitchRate']

    def get_beta(self):
        return self.data['Fms1_trueHeading']

    def get_phi(self):
        return self.data['Ahrs1_Roll']

    def get_p(self):
        return self.data['Ahrs1_bRollRate']

    def get_r(self):
        return self.data['Ahrs1_bYawRate']

    def get_pb_2V(self):
        return self.get_p() * self.dynamic_params.b/(2*self.get_tas()[0])

    def get_rb_2V(self):
        return  self.get_r() * self.dynamic_params.b/(2*self.get_tas()[0])

    def get_qc_v(self):
        return self.get_q() * self.dynamic_params.c / self.get_tas()[0]

    def get_u_hat(self):
        return (self.get_tas()-self.V0)/self.V0

    def get_sym_states(self):
        return np.array([self.get_u_hat(), self.get_alpha(), self.get_theta(), self.get_qc_v()])

    def get_asym_states(self):
        return np.array([self.get_beta(), self.get_phi(), self.get_pb_2V(), self.get_rb_2V()])


    @staticmethod
    def plot(ts, Ys, name="fig"):
        for i, ys in enumerate(Ys[:4]):
            y_max = np.abs(ys.reshape(-1, )).max()
            plt.plot(ts, ys.reshape(-1, ) / y_max, label=f'{i}')
        plt.legend()
        plt.xlabel('t [s]')
        plt.ylabel(r'$\frac{x}{x_{max}}$ [-]')
        plt.title(name)
        plt.show()

        for i, ys in enumerate(Ys[4:]):
            y_max = np.abs(ys.reshape(-1, )).max()
            plt.plot(ts, ys.reshape(-1, ) / y_max, label=f'{i}')
        plt.legend()
        plt.xlabel('t [s]')
        plt.ylabel(r'$\frac{d}{dt}\frac{x}{x_{max}}$ [-]')
        plt.title(name)
        plt.show()

    @staticmethod
    def plot_symmetric(ts, y_sim, y_meas=np.zeros([4,0]), savename=None):
        'get state arrays: [uhat, alpha, theta, qcV]'

        simcol = 'b'
        meascol = 'k'
        simline = '-'
        measline = '--'

        fig, axs = plt.subplots(2, 2, figsize=(10, 10), sharey=False, sharex=True, layout='constrained', )

        locs = [[0, 0], [0, 1], [1, 0], [1, 1]]
        y_labels=[r'speed $\hat{u}$ [-]', r'AoA $\alpha$ [rad]', r'pitch $\theta$ [rad]', r'pitch rate $\frac{qc}{V}$ [-]']
        x_labels=['', '', r'time $t$ [s]', r'time $t$ [s]']

        for i,loc in enumerate(locs):
            axs[loc[0], loc[1]].plot(ts, y_sim[i,:].reshape(ts.shape), color=simcol, linestyle=simline, linewidth=1., label='simulated')
            if np.shape(y_meas)[1] == y_sim.shape[1]:
                #axs[loc[0], loc[1]].plot(ts, y_meas[i, :].reshape(ts.shape), color=meascol, linestyle=measline, linewidth=1., label='measured')
                axs[loc[0], loc[1]].plot(ts, y_meas[i, :].reshape(ts.shape), color='r', linestyle=measline, linewidth=1., label='measured')

                ##############
                # axs[loc[0], loc[1]].plot(ts, y_meas[i, :].reshape(ts.shape), color=meascol, linestyle=measline, linewidth=1., label='measured')
                # # Calculate and plot the ±10% region around the measured data for amplitude
                # lower_bound_amp = y_meas[i, :] * 0.9
                # upper_bound_amp = y_meas[i, :] * 1.1
                
                # # Calculate and plot the ±10% region around the measured data for period
                # period_tolerance = 0.1 * (ts[-1] - ts[0])  # Assuming linear spacing for simplicity
                # ts_lower = np.maximum(ts - period_tolerance, ts[0])
                # ts_upper = np.minimum(ts + period_tolerance, ts[-1])

                # # For simplicity in visualization, just expand the bounds rather than shifting the entire curve
                # axs[loc[0], loc[1]].fill_betweenx(lower_bound_amp, ts_lower, ts_upper, color=meascol, alpha=0.1)
                # axs[loc[0], loc[1]].fill_betweenx(upper_bound_amp, ts_lower, ts_upper, color=meascol, alpha=0.1)


                ##############
                # lower_bound = y_meas[i, :] * 0.9  # 90% of measured data # y_meas[i, :] + (y_meas[i, :].max() -y_meas[i, :].min())*0.3 # y_meas[i, :] + sum(y_meas[i, :])/len(y_meas[i, :]) * 0.1   
                # upper_bound =  y_meas[i, :] * 1.1  # 110% of measured data y_meas[i, :] - (y_meas[i, :].max() -y_meas[i, :].min())*0.3 # y_meas[i, :] - sum(y_meas[i, :])/len(y_meas[i, :]) * 0.1  
                # axs[loc[0], loc[1]].fill_between(ts, lower_bound, upper_bound, color=meascol, alpha=0.2)
                ##############varying boundary
                scale_factor = (ts - ts.min()) / (ts.max() - ts.min())
                
                for i, loc in enumerate(locs):
                    axs[loc[0], loc[1]].plot(ts, y_sim[i,:].reshape(ts.shape), color=simcol, linestyle=simline, linewidth=1., label='simulated')
                    
                    if np.shape(y_meas)[1] == y_sim.shape[1]:
                        # Plot measured data
                        axs[loc[0], loc[1]].plot(ts, y_meas[i, :].reshape(ts.shape), color=meascol, linestyle=measline, linewidth=1., label='measured')
                        
                        # Adjust the amplitude tolerance over time
                        # Initial tolerance at the start of the time series
                        initial_tolerance = 0.1  # 10%
                        # Increase the tolerance linearly over time
                        tolerance_increase = initial_tolerance + scale_factor * 0.2  # Up to 30% at the end
                        
                        lower_bound = y_meas[i, :] * (1 - tolerance_increase)
                        upper_bound = y_meas[i, :] * (1 + tolerance_increase)
                        
                        axs[loc[0], loc[1]].fill_between(ts, lower_bound, upper_bound, color=meascol, alpha=0.1)

                ############ varying boundary + timeshift (gives two seperate regions for the time shift)
                # scale_factor = (ts - ts.min()) / (ts.max() - ts.min())
                # time_shift_factor = np.linspace(0, 0.1, len(ts))  # Linear increase in time shift

                # for i, loc in enumerate(locs):
                #     axs[loc[0], loc[1]].plot(ts, y_sim[i,:].reshape(ts.shape), color=simcol, linestyle=simline, linewidth=1., label='simulated')
                    
                #     if np.shape(y_meas)[1] == y_sim.shape[1]:
                #         # Plot measured data
                #         axs[loc[0], loc[1]].plot(ts, y_meas[i, :].reshape(ts.shape), color=meascol, linestyle=measline, linewidth=1., label='measured')
                        
                #         # Adjust the amplitude tolerance over time
                #         initial_tolerance = 0.1  # 10%
                #         tolerance_increase = initial_tolerance + scale_factor * 0.1  # Up to 20% at the end
                        
                #         lower_bound = y_meas[i, :] * (1 - tolerance_increase)
                #         upper_bound = y_meas[i, :] * (1 + tolerance_increase)
                        
                #         axs[loc[0], loc[1]].fill_between(ts, lower_bound, upper_bound, color=meascol, alpha=0.2)
                        
                #         # Apply time shift
                #         ts_shift_positive = ts + 10 #ts + time_shift_factor * ts.max()
                #         ts_shift_negative = ts - 10 #ts - time_shift_factor * ts.max()
                #         shiftcol = 'r'
                        
                #         # Plot the regions for positive and negative time shifts
                #         axs[loc[0], loc[1]].fill_between(ts_shift_positive, lower_bound, upper_bound, color=shiftcol, alpha=0.1, label='positive time shift')
                #         axs[loc[0], loc[1]].fill_between(ts_shift_negative, lower_bound, upper_bound, color=shiftcol, alpha=0.1, label='negative time shift')

                ############# same as before..but trying to make the tie shift one single area
                        # Scale factor for tolerance - this will determine how much the bounds increase over time
                scale_factor = (ts - ts.min()) / (ts.max() - ts.min())
                time_shift_factor = np.linspace(0, 0.1, len(ts))  # Linear increase in time shift
                shiftcol = 'r'
                for i, loc in enumerate(locs):
                    axs[loc[0], loc[1]].plot(ts, y_sim[i,:].reshape(ts.shape), color=simcol, linestyle=simline, linewidth=1., label='simulated')
                    
                    if np.shape(y_meas)[1] == y_sim.shape[1]:
                        # Plot measured data
                        axs[loc[0], loc[1]].plot(ts, y_meas[i, :].reshape(ts.shape), color=meascol, linestyle=measline, linewidth=1., label='measured')
                        
                        # Adjust the amplitude tolerance over time
                        initial_tolerance = 0.1  # 10%
                        tolerance_increase = initial_tolerance + scale_factor * 0.1  # Up to 20% at the end
                        
                        lower_bound = y_meas[i, :] * (1 - tolerance_increase)
                        upper_bound = y_meas[i, :] * (1 + tolerance_increase)
                        
                        # Original amplitude tolerance region
                        axs[loc[0], loc[1]].fill_between(ts, lower_bound, upper_bound, color=meascol, alpha=0.2)
                        
                        # Apply time shift
                        ts_shift_positive = ts + time_shift_factor * ts.max()
                        ts_shift_negative = ts - time_shift_factor * ts.max()
                        
                        # For the single region covering both time shifts, find the min and max bounds across shifts
                        # The idea is to stretch the amplitude bounds across the shifted time series
                        lower_bound_stretch = np.interp(ts_shift_negative, ts, lower_bound, left=np.nan, right=np.nan)
                        upper_bound_stretch = np.interp(ts_shift_positive, ts, upper_bound, left=np.nan, right=np.nan)

                        # Fill the region between the negative and positive time shifts
                        axs[loc[0], loc[1]].fill_betweenx(y_meas[i, :], ts_shift_negative, ts_shift_positive, where=(ts_shift_positive >= ts_shift_negative), color=shiftcol, alpha=0.2, label='time shift region')


                ##############
                # period_tolerance = 5 # seconds
                # if period_tolerance != 0:
                #     ts_shifted_left = ts - period_tolerance
                #     ts_shifted_right = ts + period_tolerance
                #     # Ensure shifted time series starts at 0 or later
                #     ts_shifted_left = np.maximum(ts_shifted_left, 0)
                #     axs[loc[0], loc[1]].plot(ts_shifted_left, y_meas[i, :].reshape(ts.shape), color=meascol, linestyle=':', linewidth=0.5, alpha=0.7, label='measured (left shift)')
                #     axs[loc[0], loc[1]].plot(ts_shifted_right, y_meas[i, :].reshape(ts.shape), color=meascol, linestyle=':', linewidth=0.5, alpha=0.7, label='measured (right shift)')
                #############

            axs[loc[0], loc[1]].set_xlabel(x_labels[i])
            axs[loc[0], loc[1]].set_ylabel(y_labels[i])

            axs[loc[0], loc[1]].legend()

        if savename is not None:
            fig.savefig(savename, dpi=500, bbox_inches='tight')
        plt.show()

    @staticmethod
    def plot_asymmetric(ts, y_sim, y_meas=np.zeros([4,0]), savename=None):
        'get state arrays: [beta, phi, pb/2v, rb/2v]'

        simcol = 'b'
        meascol = 'k'
        simline = '-'
        measline = '--'

        fig, axs = plt.subplots(2, 2, figsize=(10, 10), sharey=False, sharex=True, layout='constrained', )

        locs = [[0, 0], [0, 1], [1, 0], [1, 1]]
        y_labels = [r'yaw $\beta$ [rad]', r'roll $\phi$ [rad]', r'roll rate $\frac{pb}{2V}$ [-]', r'yaw rate $\frac{rb}{2V}$ [-]']
        x_labels = ['', '', r'time $t$ [s]' , r'time $t$ [s]']

        for i, loc in enumerate(locs):
            axs[loc[0], loc[1]].plot(ts, y_sim[i, :].reshape(ts.shape), color=simcol, linestyle=simline, linewidth=1., label='simulated')
            if np.shape(y_meas)[1] == y_sim.shape[1]:
                axs[loc[0], loc[1]].plot(ts, y_meas[i, :].reshape(ts.shape), color=meascol, linestyle=measline, linewidth=1., label='measured')

            axs[loc[0], loc[1]].set_xlabel(x_labels[i])
            axs[loc[0], loc[1]].set_ylabel(y_labels[i])

            axs[loc[0], loc[1]].legend()

        if savename is not None:
            fig.savefig(savename, dpi=500, bbox_inches='tight')
        plt.show()

    def __call__(self, isPlot=False):
        #TODO
        T = self.get_times()


        U_sym = self.get_delta_e().reshape(1, -1)
        U_asym = np.vstack([self.get_delta_a(), self.get_delta_r()])

        X0_sym = self.get_sym_states()[:,0]
        X0_asym = self.get_asym_states()[:,0]

        #TODO
        X_initial_sym = np.zeros([4,]) #np.array([0,0,0,X0_sym[3]])
        X_initial_asym = np.zeros([4,]) #np.array([0,0,X0_asym[2],X0_asym[3]])

        refinement = 1
        T_refined = np.linspace(T[0], T[-1], T.shape[0] * refinement)
        U_sym_refined = np.repeat(U_sym, refinement, axis=1)
        U_asym_refined = np.repeat(U_asym, refinement, axis=1)

        _, Y_sym = control.forced_response(self.ss_sym, T_refined, U_sym_refined - U_sym[:, 0:1], X_initial_sym)
        _, Y_asym = control.forced_response(self.ss_asym, T_refined, U_asym_refined - U_asym[:, 0:1], X_initial_asym)

        plt.plot(T, (U_sym - U_sym[:, 0:1]).reshape(-1,))
        plt.show()

        print(Y_sym.shape, X0_sym.shape, X_initial_sym.shape)
        Y_sym[:4,:] += (X0_sym-X_initial_sym)[:, np.newaxis]
        Y_asym[:4,:] += (X0_asym-X_initial_asym)[:, np.newaxis]

        if isPlot:
            self.plot_symmetric(T, Y_sym[:,::refinement], self.get_sym_states())
            self.plot_asymmetric(T, Y_asym[:,::refinement], self.get_asym_states())

        return Y_sym, Y_asym

    def theoretical_phugoid(self):
        #impulse response on elevator
        T = self.get_times()
        X0_sym = self.get_sym_states()[:, 0]
        T, Y_sym = control.impulse_response(self.ss_sym, T=T, X0=np.zeros([4,1]), input=0)

        Y_sym[:4,0,:] += X0_sym[:, np.newaxis]
        return T, Y_sym

    def theoretical_dutch_roll(self):
        #impulse response on rudder
        T = self.get_times()
        X0_asym = self.get_sym_states()[:, 0]
        T, Y_asym = control.impulse_response(self.ss_asym, T=T, X0=np.zeros([4,1]), input=1)

        Y_asym[:4, 0,:] += X0_asym[:, np.newaxis]
        return T, Y_asym

    def theoretical_spiral(self):
        #impulse response on alieron
        T = self.get_times()
        X0_asym = self.get_sym_states()[:, 0]
        T, Y_asym = control.impulse_response(self.ss_sym, T=T, X0=np.zeros([4,1]), input=0)

        Y_asym[:4,0,:] += X0_asym[:, np.newaxis]
        return T, Y_asym

    def theoretical_aperiodic_roll(self):
        #step on alieron
        T = self.get_times()
        X0_asym = self.get_sym_states()[:, 0]
        T, Y_asym = control.step_response(self.ss_sym, T=T, X0=np.zeros([4,1]), input=0)

        Y_asym[:4,0,:] += X0_asym[:, np.newaxis]
        return T, Y_asym

    def get_sym_eigs(self):
        return np.linalg.eigvals(self.ss_sym.A)

    def get_asym_eigs(self):
        return np.linalg.eigvals(self.ss_asym.A)

    def plot_sym_eigenvalues(self):
        sym_eigs = self.get_sym_eigs()

        fig, ax = plt.subplots(1, 1, figsize=(5, 5), layout='constrained', )
        for idx, eig in enumerate(sym_eigs):
            ax.plot(np.real(eig), np.imag(eig), linestyle='', marker='x', color='k', )
            ax.annotate(f'$\lambda_{idx}$', (np.real(eig), np.imag(eig)+.075),)
            ax.axhline(0, color='k', linewidth=.5)
            ax.axvline(0, color='k', linewidth=.5)

        ax.set_xlabel(r'$\Re(\lambda_c)$')
        ax.set_ylabel(r'$\Im(\lambda_c)$')
        plt.show()

    def plot_asym_eigenvalues(self):
        asym_eigs = self.get_asym_eigs()

        fig, ax = plt.subplots(1, 1, figsize=(5, 5), layout='constrained', )
        for idx, eig in enumerate(asym_eigs):
            ax.plot(np.real(eig), np.imag(eig), linestyle='', marker='x', color='k',)
            ax.annotate(f'$\lambda_{idx}$', (np.real(eig), np.imag(eig) + .075), )
            ax.axhline(0, color='k', linewidth=.5)
            ax.axvline(0, color='k', linewidth=.5)
        ax.set_xlabel(r'$\Re(\lambda_c)$')
        ax.set_ylabel(r'$\Im(\lambda_c)$')
        plt.show()


if __name__ == "__main__":
    data_file = path_config.data_dict_path
    with open(data_file, 'rb') as my_file:
        data_dict = pickle.load(my_file)

    'From the excel'
    times_phugoid = (3380, 3420) #61 * 60)
    times_short_per = (54 * 60, 57 * 60)
    times_dutch_roll = (61 * 60, 60 * 60 + 4 * 60)
    times_dutch_roll_yd = (61 * 60, 60 * 60 + 4 * 60)
    times_aper_roll = (52 * 60, 54 * 60)
    times_spiral = (60 * 60 + 4 * 60, 60 * 60 + 8 * 60)

    manoeuvre = Manoeuvre(times = times_phugoid, data_dict=data_dict)
    manoeuvre(True)#manoeuvre(True)

    T,Y_sym = manoeuvre.theoretical_phugoid()
    manoeuvre.plot_symmetric(T, Y_sym)


    time = manoeuvre.get_times()
    delta_e = manoeuvre.get_delta_e()
    theta = manoeuvre.get_theta()

    #print(f'sym eigenvalues : {manoeuvre.get_sym_eigs()}, asym eigenvalues : {manoeuvre.get_asym_eigs()}')