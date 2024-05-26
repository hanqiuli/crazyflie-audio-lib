import pickle

import numpy as np
import control
import control.matlab as ml
import Cit_Par_Dynamic
import matplotlib.pyplot as plt

import path_config


def calc_AB_sym(par : Cit_Par_Dynamic.Cit_Par):
    """
    Computes A and B matrices for linear system of symmetric aircraft motion
    :return: A, B
    """
    #TODO: not so sure about V=V0??
    c_v = par.c/par.V0

    #premultiplied with c_v, so no need for it inside mat
    #print(par.muc.shape)
    P_sym = c_v * np.array(
        [[-2*par.muc, 0                     , 0 , 0                     ],
         [0         , par.CZadot-2*par.muc  , 0 , 0                     ],
         [0         , 0                     , -1, 0                     ],
         [0         , par.Cmadot            , 0 , -2*par.muc * par.KY2  ]])


    #premultiplied with negative, so no need for negative inside
    Q_sym = - np.array(
        [[par.CXu   , par.CXa   , par.CZ0   , 0                     ],
         [par.CZu   , par.CZa   , -par.CX0  , par.CZq + 2*par.muc   ],
         [0         , 0         , 0         , 1                     ],
         [par.Cmu   , par.Cma   , 0         , par.Cmq               ]])

    #premultiplied with negative, so no need for negative inside matrix
    R_sym = - np.array(
        [[par.CXde  ],
         [par.CZde  ],
         [0         ],
         [par.Cmde  ]])

    P_sym_inv = np.linalg.inv(P_sym)

    A_sym = P_sym_inv @ Q_sym
    B_sym = P_sym_inv @ R_sym

    return A_sym, B_sym

def calc_AB_asym(par : Cit_Par_Dynamic.Cit_Par):
    """
    Computes A and B matrices for linear system of asymmetric aircraft motion
    :return: A, B
    """
    # TODO: not so sure about V=V0??
    b_v = par.b / par.V0

    # premultiplied with c_v, so no need for it inside mat
    P_asym = b_v * np.array(
        [[par.CYbdot - 2 * par.mub  , 0     , 0                     , 0                     ],
         [0                         , -0.5  , 0                     , 0                     ],
         [0                         , 0     , -4 * par.mub * par.KX2, 4 * par.mub * par.KXZ ],
         [par.Cnbdot                , 0     , 4 * par.mub * par.KXZ , -4 * par.mub * par.KZ2]])


    # premultiplied with negative, so no need for negative inside
    Q_asym = - np.array(
        [[par.CYb   , par.CL, par.CYp   , par.CYr - 4*par.mub   ],
         [0         , 0     , 1        , 0                      ],
         [par.Clb   , 0     , par.Clp   , par.Clr               ],
         [par.Cnb   , 0     , par.Cnp   , par.Cnr               ]])



    # premultiplied with negative, so no need for negative inside matrix
    R_asym = - np.array(
        [[par.CYda  , par.CYdr  ],
         [0         , 0         ],
         [par.Clda  , par.Cldr  ],
         [par.Cnda  , par.Cndr  ]])

    P_asym_inv = np.linalg.inv(P_asym)

    A_asym = P_asym_inv @ Q_asym
    B_asym = P_asym_inv @ R_asym

    return A_asym, B_asym

def calc_CD(A : np.ndarray,B : np.ndarray):
    """
    Computes and returns C and D output matrices for linear system with output vector:
    y = [x^T, x'^T]^T       in other words the state vector stacked on top of the derivative of the state vector
    :param A: A matrix of system (for state)
    :param B: B matrix of system (for input)
    :return: C, D matrices for computing output
    """
    C = np.vstack((np.eye(A.shape[0]), A))
    D = np.vstack((np.zeros_like(B), B))

    return C, D

def ss_sym(par : Cit_Par_Dynamic.Cit_Par):
    #symmetric state space model
    A_sym, B_sym = calc_AB_sym(par)
    C_sym, D_sym = calc_CD(A_sym,B_sym)
    ss_sym = control.matlab.ss(A_sym, B_sym, C_sym, D_sym)
    return ss_sym

def ss_asym(par : Cit_Par_Dynamic.Cit_Par):
    #asymmetric state space model
    A_asym, B_asym = calc_AB_asym(par)
    C_asym, D_asym = calc_CD(A_asym,B_asym)
    ss_asym = control.matlab.ss(A_asym, B_asym, C_asym, D_asym)
    return ss_asym






if __name__ == "__main__":

    ss_sym(Cit_Par_Dynamic.Cit_Par(1,1,1,1))
    ss_asym(Cit_Par_Dynamic.Cit_Par(1,1,1,1))

    filename = path_config.data_dict_path
    with open(filename, 'rb') as picklefile:
        data_dict = pickle.load(picklefile)

    phugoid_times = (57*60, 61*60)

    #io = dyn_data.Get_Input_Output(phugoid_times, data_dict)
    #U = io.get_delta_e().reshape(1,-1)
    #T = io.get_times()

    #alpha0 = io.get_alpha()[0]


    #T=np.linspace(0,10,500)
    #U=np.ones([B_sym.shape[1], 500])
    #X0=np.zeros(A_sym.shape[0])

    ts, Ys = control.input_output_response(ss_sym, T, U, X0)


    print(Ys.shape)
    for i, ys in enumerate(Ys[:4]):
        y_max = np.abs(ys.reshape(-1,)).max()
        print(y_max)
        plt.plot(ts, ys.reshape(-1,)/y_max, label=f'{i}')
    plt.legend()
    plt.xlabel('t [s]')
    plt.ylabel(r'$\frac{x}{x_{max}}$ [-]')
    plt.show()

    for i, ys in enumerate(Ys[4:]):
        y_max = np.abs(ys.reshape(-1,)).max()
        plt.plot(ts, ys.reshape(-1,)/y_max, label=f'{i}')
    plt.legend()
    plt.xlabel('t [s]')
    plt.ylabel(r'$\frac{d}{dt}\frac{x}{x_{max}}$ [-]')
    plt.show()