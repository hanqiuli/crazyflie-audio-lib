# Citation 550 - Linear simulation
import math
import Cit_par24 as cp
from static_params import E, Cd0,CLa,Cma,Cmde





class Cit_Par:
    Cm0 = cp.Cm0
    Cmu = cp.Cmu
    Cmadot = cp.Cmadot
    Cmq = cp.Cmq
    CmTc = cp.CmTc

    CYb = cp.CYb
    CYbdot = cp.CYbdot
    CYp = cp.CYp
    CYr = cp.CYr
    CYda = cp.CYda
    CYdr = cp.CYdr

    Clb = cp.Clb
    Clp = cp.Clp
    Clr = cp.Clr
    Clda = cp.Clda
    Cldr = cp.Cldr

    Cnb = cp.Cnb
    Cnbdot = cp.Cnbdot
    Cnp = cp.Cnp
    Cnr = cp.Cnr
    Cnda = cp.Cnda
    Cndr = cp.Cndr

    # Aircraft geometry
    S = cp.S
    Sh = cp.Sh
    Sh_S = cp.Sh_S
    lh = cp.lh
    c = cp.c
    lh_c = cp.lh_c
    b = cp.b  # wing span [m]
    bh = cp.bh  # stabiliser span [m]
    A = cp.A
    Ah = cp.Ah
    Vh_V = cp.Vh_V
    ih = cp.ih

    # Constant values concerning atmosphere and gravity
    rho0 = cp.rho0
    p0 = cp.p0
    lamb = cp.lamb  # temperature gradient in ISA [K/m]
    Temp0 = cp.Temp0  # temperature at sea level in ISA [K]
    R = cp.R  # specific gas constant [m^2/sec^2K]
    g = cp.g  # [m/sec^2] (gravity constant)

    def __init__(self, hp0, V0, alpha0, th0, mass):
        pi = math.pi

        self.hp0 = hp0
        self.V0 = V0
        self.alpha0 = alpha0
        self.th0 = th0
        self.m = mass

        self.e = E
        self.CD0 = Cd0
        self.CLa = CLa

        self.Cma = Cma
        self.Cmde = Cmde

        # air density [kg/m^3]
        self.rho = self.rho0 * ((1 + (self.lamb *self.hp0 / self.Temp0))) ** (
            -((self.g / (self.lamb * self.R)) + 1))  # power( ((1+(lamb * hp0 / Temp0))), (-((g / (lamb*R)) + 1)))
        self.W = self.m * self.g  # [N]       (aircraft weight)

        # Constant values concerning aircraft inertia
        self.muc = self.m / (self.rho * self.S * self.c)
        self.mub = self.m / (self.rho * self.S * self.b)
        self.KX2 = 0.019
        self.KZ2 = 0.042
        self.KXZ = 0.002
        self.KY2 = 1.25 * 1.114

        # Aerodynamic constants
        self.Cmac = 0  # Moment coefficient about the aerodynamic centre [ ]
        self.CNwa = self.CLa  # Wing normal force slope [ ]
        self.CNha = 2 * pi * self.Ah / (self.Ah + 2)  # Stabiliser normal force slope [ ]
        self.depsda = 4 / (self.A + 2)  # Downwash gradient [ ]

        # Lift and drag coefficient
        self.CL = 2 * self.W / (self.rho * self.V0 ** 2 * self.S)  # Lift coefficient [ ]
        self.CD = self.CD0 + (self.CLa * self.alpha0) ** 2 / (pi * self.A * self.e)  # Drag coefficient [ ]

        # Stability derivatives
        self.CX0 = self.W * math.sin(self.th0) / (0.5 * self.rho * self.V0 ** 2 * self.S)
        self.CXu = -0.09500
        self.CXa = +0.47966  # Positive, see FD lecture notes)
        self.CXadot = +0.08330
        self.CXq = -0.28170
        self.CXde = -0.03728

        self.CZ0 = -self.W * math.cos(self.th0) / (0.5 * self.rho * self.V0 ** 2 * self.S)
        self.CZu = -0.37616
        self.CZa = -5.74340
        self.CZadot = -0.00350
        self.CZq = -5.66290
        self.CZde = -0.69612