import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import path_config


class Mass:
    def __init__(self):
        self.Conv_fact_lbsHr = 0.0001259979
        self.Conv_fact_lbsKg = 0.453592
        self.Conv_fact_inM = 0.0254
        self.Conv_fact_inPNM = 0.113
        with open(path_config.data_dict_path, 'rb') as pickle_file:
            self.Data_Dict_loaded = pickle.load(pickle_file)
        self.time = self.Data_Dict_loaded["time"]
        self.Lmass_flow = self.Data_Dict_loaded["lh_engine_FMF"] * self.Conv_fact_lbsHr
        self.Rmass_flow = self.Data_Dict_loaded["rh_engine_FMF"] * self.Conv_fact_lbsHr
        self.EW = 9197 * self.Conv_fact_lbsKg#[kg]
        self.Pass_Weight_Array = np.array([93, 98, 68, 62.5, 66, 74, 73.5, 87.5, 79])
        self.Pass_Weight = 93 + 98 + 79 + 68 + 62.5 + 66 + 74 + 73.5 + 87.5
        self.Fuel_Weight = 2667 * self.Conv_fact_lbsKg
        self.TOT_Weight_init = self.Pass_Weight + self.EW + self.Fuel_Weight
        self.TOT_Weight_upd = np.zeros(self.Rmass_flow.shape)
        self.Fuel_Weight_upd = np.zeros(self.Rmass_flow.shape)
        self.TOT_Weight_upd[0] = self.TOT_Weight_init
        self.Fuel_Weight_upd[0] = self.Fuel_Weight
        self.Seat_Pos = np.array([131.0, 131.0, 214.0, 214.0, 251.0, 251.0, 288.0, 288.0, 170.0]) * self.Conv_fact_inM
        self.dt = 0.1
        self.R_H_Gear = [self.Conv_fact_lbsKg * 5280 * 9.81, 315.5 * self.Conv_fact_inM ] # 0 is weight 1 is arm
        self.L_H_Gear = [self.Conv_fact_lbsKg * 5222 * 9.81, 315.5 * self.Conv_fact_inM ]
        self.N_Gear = [self.Conv_fact_lbsKg * 1370 *9.81, 93.7 * self.Conv_fact_inM ]

        self.Fuel_Load = np.array(
            [100,
                             200,
                             300,
                             400,
                             500,
                             600,
                             700,
                             800,
                             900,
                             1000,
                             1100,
                             1200,
                             1300,
                             1400,
                             1500,
                             1600,
                             1700,
                             1800,
                             1900,
                             2000,
                             2100,
                             2200,
                             2300,
                             2400,
                             2500,
                             2600,
                             2700]
            ) * self.Conv_fact_lbsKg

        self.Fuel_Moment = np.array(            [298.16,
            591.18,
            879.08,
            1165.42,
            1448.40,
            1732.53,
            2014.80,
            2298.84,
            2581.92,
            2866.30,
            3150.18,
            3434.52,
            3718.52,
            4003.23,
            4287.76,
            4572.24,
            4856.56,
            5141.16,
            5425.64,
            5709.90,
            5994.04,
            6278.47,
            6562.82,
            6846.96,
            7131.00,
            7415.33,
            7699.60]
        ) * 10**2 * self.Conv_fact_inPNM
        self.inter = interp1d (self.Fuel_Load, self.Fuel_Moment )
    def NewMass_calculator(self):
        for i in range(1,self.Rmass_flow.shape[0]):
            self.TOT_Weight_upd[i] = self.TOT_Weight_upd [i-1] - self.Rmass_flow[i]*self.dt - self.Lmass_flow[i]*self.dt
            self.Fuel_Weight_upd[i] = self.Fuel_Weight_upd[i-1] -self.Rmass_flow[i]*self.dt - self.Lmass_flow[i]*self.dt
        return self.TOT_Weight_upd
    def EmptyCG(self): # fuel is in
        return (self.R_H_Gear[0]*self.R_H_Gear[1] + self.L_H_Gear[0]*self.L_H_Gear[1]+ self.N_Gear[0]*self.N_Gear[1] - 762856.5 * 0.1129848333) / (self.R_H_Gear[0]+ self.L_H_Gear[0] + self.N_Gear[0] - 2675.0*self.Conv_fact_lbsKg*9.81)
    def CGShift(self, weight, arm, totweight):
        return (weight * (arm-self.EmptyCG())) / (totweight)
    def CG_POS_PER_TIME(self):
        new_mass = self.NewMass_calculator()
        Pax_CG_shift = np.zeros(9)
        Weight = self.TOT_Weight_init
        # WEIGHT SHIFT DUE TO PASSENGERS SO NOW CAN CALCULATE THE ACTUAL INITIAL CG POS
        for i in range(0, self.Pass_Weight_Array.shape[0]):
            Weight = Weight + self.Pass_Weight_Array[i]
            Pax_CG_shift[i] = self.CGShift(self.Pass_Weight_Array[i] * 9.81, self.Seat_Pos[i], Weight * 9.81)
        CG_POS_INIT_FLIGHT = self.EmptyCG() + np.sum(Pax_CG_shift)

        FUEL_ARM_PER_TIME = np.zeros(self.Fuel_Weight_upd.shape[0])
        CG_SHIFT_PER_TIME = np.zeros(self.Fuel_Weight_upd.shape[0])
        NEW_CG_PER_TIME = np.zeros(self.Fuel_Weight_upd.shape[0])
        MOMENT_ARM_TIME = np.zeros(self.Fuel_Weight_upd.shape[0])
        smth = np.zeros(self.Fuel_Weight_upd.shape[0])
        for i in range(0, self.Fuel_Weight_upd.shape[0]):
            # FUEL_ARM_PER_TIME[i] = TEST_OBJ.inter(TEST_OBJ.Fuel_Weight_upd[i]) how much moment at everytimestep by fuel
            # CG_SHIFT_PER_TIME[i] = FUEL_ARM_PER_TIME [i] / TEST_OBJ.TOT_Weight_upd[i]
            # NEW_CG_PER_TIME[i] = NEW_CG_PER_TIME[i-1] + CG_SHIFT_PER_TIME
            if i == 0:
                FUEL_ARM_PER_TIME[i] = self.inter(self.Fuel_Weight_upd[i])
                MOMENT_ARM_TIME[i] = FUEL_ARM_PER_TIME[i] / (self.Fuel_Weight_upd[i] * 9.81)
                NEW_CG_PER_TIME[i] = ((self.Fuel_Weight_upd[i] * 9.81 * (
                            CG_POS_INIT_FLIGHT - MOMENT_ARM_TIME[i])) / (
                                              (Weight + self.Fuel_Weight_upd[i]) * 9.81)) + CG_POS_INIT_FLIGHT

            else:
                FUEL_ARM_PER_TIME[i] = self.inter(self.Fuel_Weight_upd[i])
                MOMENT_ARM_TIME[i] = FUEL_ARM_PER_TIME[i] / (self.Fuel_Weight_upd[i] * 9.81)
                if self.time[i] == 3000:

                    NEW_CG_PER_TIME[i] = ((self.Fuel_Weight_upd[i] - self.Fuel_Weight_upd[i - 1]) * 9.81 * (
                                NEW_CG_PER_TIME[i - 1] - MOMENT_ARM_TIME[i]) - (self.Pass_Weight_Array[7] * 9.81 * (
                            self.Seat_Pos[7] - 131 * self.Conv_fact_inM))) / (
                                                 (Weight + self.Fuel_Weight_upd[i]) * 9.81) + NEW_CG_PER_TIME[
                                             i - 1]
                else:
                    NEW_CG_PER_TIME[i] = ((self.Fuel_Weight_upd[i] - self.Fuel_Weight_upd[i - 1]) * 9.81 * (
                                NEW_CG_PER_TIME[i - 1] - MOMENT_ARM_TIME[i])) / (
                                                 (Weight + self.Fuel_Weight_upd[i]) * 9.81) + NEW_CG_PER_TIME[
                                             i - 1]
                smth[i] = NEW_CG_PER_TIME[i - 1] - MOMENT_ARM_TIME[i]
        for j in range(1, NEW_CG_PER_TIME.shape[0]):
            CG_SHIFT_PER_TIME[j] = NEW_CG_PER_TIME[j]-NEW_CG_PER_TIME[j-1]
        return NEW_CG_PER_TIME, CG_SHIFT_PER_TIME

if __name__ == "__main__":
    g = 9.81
    self = Mass()
    self.NewMass_calculator()
    plt.plot(self.time, self.TOT_Weight_upd)
    plt.xlabel("time [s]")
    plt.ylabel("Total Mass [Kg]")
    plt.title("Total Mass with time")
    plt.show()
    plt.plot(self.time, self.Fuel_Weight_upd)
    plt.xlabel("time [s]")
    plt.ylabel("Fuel Mass [Kg]")
    plt.title("Fuel with time")
    plt.show()
    Pax_CG_shift = np.zeros(9)
    Weight = self.TOT_Weight_init
    # WEIGHT SHIFT DUE TO PASSENGERS SO NOW CAN CALCULATE THE ACTUAL INITIAL CG POS
    for i in range(0, self.Pass_Weight_Array.shape[0]):
        Weight = Weight + self.Pass_Weight_Array[i]
        Pax_CG_shift[i] = self.CGShift(self.Pass_Weight_Array[i] * 9.81, self.Seat_Pos[i], Weight * g)
    CG_POS_INIT_FLIGHT = self.EmptyCG() + np.sum(Pax_CG_shift)

    FUEL_ARM_PER_TIME = np.zeros(self.Fuel_Weight_upd.shape[0])
    CG_SHIFT_PER_TIME = np.zeros(self.Fuel_Weight_upd.shape[0])
    NEW_CG_PER_TIME = np.zeros(self.Fuel_Weight_upd.shape[0])
    MOMENT_ARM_TIME = np.zeros(self.Fuel_Weight_upd.shape[0])
    smth = np.zeros(self.Fuel_Weight_upd.shape[0])

    for i in range(0, self.Fuel_Weight_upd.shape[0]):
        #FUEL_ARM_PER_TIME[i] = TEST_OBJ.inter(TEST_OBJ.Fuel_Weight_upd[i]) how much moment at everytimestep by fuel
        #CG_SHIFT_PER_TIME[i] = FUEL_ARM_PER_TIME [i] / TEST_OBJ.TOT_Weight_upd[i]
        #NEW_CG_PER_TIME[i] = NEW_CG_PER_TIME[i-1] + CG_SHIFT_PER_TIME
        if i == 0:
            FUEL_ARM_PER_TIME[i] = self.inter(self.Fuel_Weight_upd[i])
            MOMENT_ARM_TIME[i] = FUEL_ARM_PER_TIME[i] / (self.Fuel_Weight_upd[i] * 9.81)
            NEW_CG_PER_TIME[i] = ((self.Fuel_Weight_upd[i] * 9.81 * (CG_POS_INIT_FLIGHT - MOMENT_ARM_TIME[i])) / ((Weight + self.Fuel_Weight_upd[i]) * 9.81)) + CG_POS_INIT_FLIGHT

        else:
            FUEL_ARM_PER_TIME[i] = self.inter(self.Fuel_Weight_upd[i])
            MOMENT_ARM_TIME[i] = FUEL_ARM_PER_TIME[i] / (self.Fuel_Weight_upd[i] * 9.81)
            if self.time[i] == 2880:
                NEW_CG_PER_TIME[i] = ((self.Fuel_Weight_upd[i] - self.Fuel_Weight_upd[i - 1]) * 9.81 * (NEW_CG_PER_TIME[i - 1] - MOMENT_ARM_TIME[i]) + (self.Pass_Weight_Array[7] * 9.81 * (self.Seat_Pos[7] - 151 * self.Conv_fact_inM))) / ((Weight + self.Fuel_Weight_upd[i]) * 9.81) + NEW_CG_PER_TIME[i - 1]
            else:
                NEW_CG_PER_TIME[i] = ((self.Fuel_Weight_upd[i] - self.Fuel_Weight_upd[i - 1]) * 9.81 * (NEW_CG_PER_TIME[i - 1] - MOMENT_ARM_TIME[i])) / ((Weight + self.Fuel_Weight_upd[i]) * 9.81) + NEW_CG_PER_TIME[i - 1]
            smth[i] = NEW_CG_PER_TIME[i-1]- MOMENT_ARM_TIME[i]
    plt.plot(self.time, self.CG_POS_PER_TIME()[1])
    self.NewMass_calculator()
    print(self.CG_POS_PER_TIME()[0])
    plt.show()

