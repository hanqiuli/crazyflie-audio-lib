import unittest
from Mass_calculator import Mass
import matplotlib.pyplot as plt

class TestMassCalculator(unittest.TestCase):
    Mass_obj = Mass()
    def test_plot(self):
        self.Mass_obj.Lmass_flow = - self.Mass_obj.Lmass_flow
        self.Mass_obj.Rmass_flow = -self.Mass_obj.Rmass_flow
        self.Mass_obj.NewMass_calculator()
        plt.plot(self.Mass_obj.time, self.Mass_obj.TOT_Weight_upd)
        plt.xlabel("time [s]")
        plt.ylabel("Mass [Kg]")
        plt.show()
    def test_CG_pos(self):
        self.Mass_obj.NewMass_calculator()
        plt.plot(self.Mass_obj.time,self.Mass_obj.CG_POS_PER_TIME()[0])
        plt.xlabel("time [s]")
        plt.ylabel("CG position [m]")
        plt.show()
    def test_cgshift(self):
        print(self.Mass_obj.CG_POS_PER_TIME()[0][0])
        self.Mass_obj.Pass_Weight_Array[0] = 1000
        print(self.Mass_obj.CG_POS_PER_TIME()[0][0])
    def test_neg_fuel_flow(self):
        self.Mass_obj.Lmass_flow = - self.Mass_obj.Lmass_flow
        self.Mass_obj.Rmass_flow = - self.Mass_obj.Rmass_flow
        print(self.Mass_obj.Rmass_flow)
        mass = self.Mass_obj.NewMass_calculator()
        plt.plot(self.Mass_obj.time, mass)
        plt.xlabel("time [s]")
        plt.ylabel("Mass [jkKg]")
        plt.show()
if __name__ == '__main__':
    unittest.main()