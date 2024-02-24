
from speech_loop2 import *
from ss import *
import sys
import speech_recognition as sr
import pyttsx3
import time
import threading
import openai
from dotenv import load_dotenv

# Import time module
import time

class Assistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.active = True
        self.robot = "off"
        self.try1 = "try1 is off"
        self.speaking_lock = threading.Lock()

    def speak(self, text):
        try:
            with self.speaking_lock:
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)
                engine.say(text)
                engine.runAndWait()
        except Exception as e:
            print(f"An error occurred in speak: {e}")

    def run_voice_loop(self):
        while self.active:
            try:
                with sr.Microphone() as mic:
                    self.recognizer.energy_threshold = 10000  
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)

                    audio = self.recognizer.listen(mic)
                    text = self.recognizer.recognize_google(audio).lower()

                    print("You said:", text)

                    if any(keyword in text for keyword in ["activate", "thunder", "bolt"]):
                        self.say_and_wait("Activated")
                        print("Activated")
                        print("I'm listening")
                        self.current_result_on()
                        self.active = False  # Stop the loop

                        # Pass the microphone instance without using 'with' statement
                        speech_loop2(self.recognizer, mic, self)

            except sr.RequestError as e:
                # Handle request error (could not request results from Google Speech Recognition service)
                if "connection attempt failed" in str(e):
                    print("Connection to the Google Speech Recognition service failed. Please check your internet connection.")
                else:
                    print(f"An error occurred in run_voice_loop: {e}")
                time.sleep(1)  # Add a delay to control the loop speed
            except Exception as e:
                print(f"An error occurred in run_voice_loop: {e}")
                time.sleep(1)  # Add a delay to control the loop speed

    def say_and_wait(self, text):
        self.speak(text)

    def current_result_on(self):
        self.robot = "on"  # Update robot status
        self.try1 = "try1 success"
        print("Successfully changed robot status")


# def start_speech_loop():
#     global active
#     active = True

# def stop_speech_loop():
#     global active
#     active = False

# def speech_loop():
#     global active
#     active = True
#     assistant = Assistant()
#     assistant.voice_thread = threading.Thread(target=assistant.run_voice_loop)
#     assistant.voice_thread.start()
 
def print_status(assistant):
    while True:
        with assistant.speaking_lock:
            print(f"Robot: {assistant.robot},\ntry1: {assistant.try1},")
        time.sleep(20)  # Sleep for 20 seconds
            
def main():
    print("Main function started")
    assistant = Assistant()

    # Start the print_status thread
    print_thread = threading.Thread(target=print_status, args=(assistant,))
    print_thread.start()

    # Start speech loop
    assistant.run_voice_loop()


if __name__ == "__main__":
    main()


