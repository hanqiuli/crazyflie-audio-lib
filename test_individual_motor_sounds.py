import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

uri = 'radio://0/80/2M/E7E7E7E7E8'
pwm_value = 45000

def set_motor_power(scf, motor_index, pwm_value):
    # Enable motor power
    scf.cf.param.set_value("motorPowerSet.enable", 1)
    
    # Set motor power
    motor_name = f"motorPowerSet.m{motor_index}"
    scf.cf.param.set_value(motor_name, pwm_value)

if __name__ == "__main__":
    # Initialize low level drivers
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as scf:
        print("CONNECTED!")

        for motor_index in range(1, 5):
            print(f"Turning on motor {motor_index} at PWM {pwm_value}")
            set_motor_power(scf, motor_index, pwm_value)
            time.sleep(3)
            print(f"Turning off motor {motor_index}")
            set_motor_power(scf, motor_index, 0)
            time.sleep(1)

        print("DISCONNECTED!")