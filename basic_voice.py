import time
import keyboard
import speech_recognition as sr
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

running = True

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say 'take off' to take off or press 'z' to quit.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio).lower()
        return text
    except sr.UnknownValueError:
        return ""

def set_motor_power(scf, motor_index, pwm_value):
    
    # Enable motor power
    scf.cf.param.set_value("motorPowerSet.enable", 1)

    # Set motor power
    motor_name = f"motorPowerSet.m{motor_index}"
    scf.cf.param.set_value(motor_name, pwm_value)


def quit_loop():
    global running
    print("Quitting...")
    running = False

keyboard.on_press_key("z", quit_loop)

if __name__ == "__main__":
    # Initialize low level drivers
    cflib.crtp.init_drivers()

    uri = 'radio://0/80/2M/E7E7E7E7E7'
    motorvar = 30000

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as scf:
        print("CONNECTED!")
        while running:
            spoken_text = recognize_speech()

            if "take off" in spoken_text:
                print("######################### TAKING OFF! #########################")
                #set 4 motors to 30000 for 3 seconds
                set_motor_power(scf, 1, motorvar)
                set_motor_power(scf, 2, motorvar)
                set_motor_power(scf, 3, motorvar)
                set_motor_power(scf, 4, motorvar)
                time.sleep(3)
                #set 4 motors to 0
                set_motor_power(scf, 1, 0)
                set_motor_power(scf, 2, 0)
                set_motor_power(scf, 3, 0)
                set_motor_power(scf, 4, 0)
            
            elif "stop" in spoken_text:
                running = False
                break
            else:
                print(f"!!!!You said \' {spoken_text} \'which is not a command! Try again!!!")

            time.sleep(0.1)
        set_motor_power(scf, 1, 0)
        set_motor_power(scf, 2, 0)
        set_motor_power(scf, 3, 0)
        set_motor_power(scf, 4, 0)