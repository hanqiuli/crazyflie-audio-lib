import time
import keyboard
import speech_recognition as sr

running = True

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say 'go up' to increase motor power or 'z' to quit.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio).lower()
        return text
    except sr.UnknownValueError:
        return ""

def increase_motorvar():
    global running
    print("Go up")
    # Add your motor power adjustment logic here

def quit_loop():
    global running
    print("Quitting...")
    running = False

keyboard.on_press_key("z", quit_loop)

if __name__ == "__main__":
    while running:
        spoken_text = recognize_speech()
        
        if "up" in spoken_text:
            increase_motorvar()
            print("######################### INCREASED POWER! #########################")
        else:
            print(f"!!!!You said \' {spoken_text} \'which is not a command! Try again!!!")

        time.sleep(0.1)
