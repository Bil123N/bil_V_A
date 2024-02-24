import sys
import speech_recognition as sr
import pyttsx3
import time
import datetime
import threading
import openai
from dotenv import load_dotenv
from speech_loop2 import speech_loop2, deactivate_requested
from ss import *

load_dotenv()
OPENAI_KEY = chatgpt_API
openai.api_key = OPENAI_KEY

# Global flag to control the speech loop
active = True

# Initialize deactivate_requested flag
# deactivate_requested = False

# Global flag to control the speaking state
speaking_lock = threading.Lock()

class Assistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def send_to_chatGPT(self, messages, model="gpt-3.5-turbo"):
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        message = response.choices[0].message.content
        messages.append(response.choices[0].message)
        return message

    def wishme(self):
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            return "morning"
        elif 12 <= hour < 16:
            return "afternoon"
        else:
            return "evening"

    def say_and_wait(self, text):
        global speaking_lock
        with speaking_lock:
            threading.Thread(target=self.speak, args=(text,)).start()

    def speak(self, text):
        global speaking_lock
        with speaking_lock:
            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.say(text)
            engine.runAndWait()

    def run_voice_loop(self):
        global active
        while active:
            try:
                with sr.Microphone() as mic:
                    self.recognizer.energy_threshold = 10000  
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)

                    audio = self.recognizer.listen(mic)
                    text = self.recognizer.recognize_google(audio).lower()

                    if "activate" == text or "thunder activate" in text or "bolt activate" in text:
                        self.say_and_wait("Activated")
                        print("Assistance is Activated.")
                        print("I'm listening")
                        active = False  # Stop the loop

                        # Pass the microphone instance without using 'with' statement
                        deactivate_requested = speech_loop2(self.recognizer, mic, self)
                        if deactivate_requested:
                            print("The assistance is deactivated.")
                            active = True
                            continue  # Restart the loop

                    else:
                        print("Wait for the activation word & You said:",text)

            except sr.WaitTimeoutError:
                print("No speech detected. Retrying...")
                time.sleep(1)  # Add a delay before retrying
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service: {e}")
                time.sleep(1)  # Add a delay before retrying
            except Exception as e:
                print(f"An unexpected error occurred in run_voice_loop: {e}")
                time.sleep(1)  # Add a delay before retrying

def start_speech_loop():
    global active
    active = True

def stop_speech_loop():
    global active
    active = False
    

def speech_loop():
    global active
    active = True
    assistant = Assistant()
    assistant.voice_thread = threading.Thread(target=assistant.run_voice_loop)
    assistant.voice_thread.start()
