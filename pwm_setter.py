import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
import keyboard

uri = 'radio://0/80/2M/E7E7E7E7E7'

#use "sudo -E python3 pwm_setter.py" to run this script

motorvar = 5000
latest_value = motorvar
running = True
motor_on = False

def increase_motorvar(e):
    global motorvar
    if not motorvar >= 65000:
        motorvar += 2500
    print(motorvar)

def decrease_motorvar(e):
    global motorvar
    if not motorvar <= 0:
        motorvar -= 2500
    print(motorvar)

def toggle_motorvar(e):
    global motorvar, latest_value, motor_on
    if motor_on:
        latest_value = motorvar
        motorvar = 0
        print("Motor off")
    else:
        motorvar = latest_value
        print("Motor on at: ", latest_value)
    motor_on = not motor_on

def quit_loop(e):
    global running
    running = False

keyboard.on_press_key("up", increase_motorvar)
keyboard.on_press_key("down", decrease_motorvar)
keyboard.on_press_key("o", toggle_motorvar)
keyboard.on_press_key("n", quit_loop)

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

        print("CONNECTED! Press up/down to increase/decrease motor power, o to toggle motor on/off, n to quit")

        while running:
            time.sleep(0.5)
            if motor_on:
                set_motor_power(scf, 1, motorvar)
                set_motor_power(scf, 2, motorvar)
                set_motor_power(scf, 3, motorvar)
                set_motor_power(scf, 4, motorvar)
            else:
                set_motor_power(scf, 1, 0)
                set_motor_power(scf, 2, 0)
                set_motor_power(scf, 3, 0)
                set_motor_power(scf, 4, 0)
        
        time.sleep(0.5)

        set_motor_power(scf, 1, 0)
        set_motor_power(scf, 2, 0)
        set_motor_power(scf, 3, 0)
        set_motor_power(scf, 4, 0)

        time.sleep(0.5)

        print("QUIT!")
            