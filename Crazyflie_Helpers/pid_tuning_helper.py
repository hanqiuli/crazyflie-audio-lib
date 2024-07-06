import math
import time
import matplotlib.pyplot as plt

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

# Desired roll, pitch, yaw, and thrust values
roll = 0 # deg
pitch = 0 # deg
yawrate = 0 # deg/s
thrust = 20000 # 10001 to 60000?



if __name__ == "__main__":

    # Initialize low level drivers
    cflib.crtp.init_drivers()

    # Log states from Kalman estimator
    log_config_state = LogConfig(name="State", period_in_ms=10)
    log_config_state.add_variable('stabilizer.roll', 'float')
    log_config_state.add_variable('stabilizer.pitch', 'float')
    log_config_state.add_variable('stabilizer.yaw', 'float')
    log_config_state.add_variable('controller.roll', 'float') # controller setpoint roll
    log_config_state.add_variable('controller.pitch', 'float') # controller setpoint pitch
    log_config_state.add_variable('controller.yaw', 'float') # controller setpoint yaw
    log_config_state.add_variable('controller.yawRate', 'float') # controller setpoint yawrate

    roll_history = []
    pitch_history = []
    yaw_history = []
    ref_roll_history = []
    ref_pitch_history = []
    ref_yaw_history = []

    # Connect to the Crazyflie
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as scf:
        print("CONNECTED!")
        print("Sending setpoint commands...")
        scf.cf.commander.send_setpoint(0, 0, 0, 0)

        #Tweak PID values here (only pitch and roll for now)
        scf.cf.param.set_value('pid_attitude.pitch_kp', '6')
        scf.cf.param.set_value('pid_attitude.pitch_ki', '3')
        scf.cf.param.set_value('pid_attitude.pitch_kd', '0')
        scf.cf.param.set_value('pid_attitude.roll_kp', '6')
        scf.cf.param.set_value('pid_attitude.roll_ki', '3')
        scf.cf.param.set_value('pid_attitude.roll_kd', '0')


        # Reset the estimator
        scf.cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        scf.cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2)

        startTime = time.time()

        with SyncLogger(scf, log_config_state) as logger_state:
            for log_entry in logger_state:
                currTime = time.time()
                timestamp = log_entry[0]
                data = log_entry[1]
                if currTime - startTime > 10:
                    scf.cf.commander.send_setpoint(0, 0, 0, 0)
                    scf.cf.close_link()
                    break
                scf.cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
                time.sleep(10/1000)
                print('\'time\': %d, %s ,\'ref_gx\':%f,\'ref_gy\': %f, \'ref_gz\': %f #' % (timestamp, data, roll, pitch, yawrate))
                roll_history.append(data['stabilizer.roll'])
                pitch_history.append(data['stabilizer.pitch'])
                yaw_history.append(data['stabilizer.yaw'])
                ref_roll_history.append(data['controller.roll'])
                ref_pitch_history.append(data['controller.pitch'])
                ref_yaw_history.append(data['controller.yaw'])
        print("DONE!")

        plt.figure()
        plt.plot(roll_history, label='roll')
        plt.plot(pitch_history, label='pitch')
        plt.plot(yaw_history, label='yaw')
        plt.plot(ref_roll_history, label='ref_roll')
        plt.plot(ref_pitch_history, label='ref_pitch')
        plt.plot(ref_yaw_history, label='ref_yaw')
        plt.legend()
        plt.show()

        print("DISCONNECTED!")

    








