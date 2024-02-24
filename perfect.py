# index.html 
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Voice Assistant</title>
# </head>
# <body>
#     <h1>Voice Assistant</h1>
#     <button id="activate-btn" onclick="toggleAssistant()">Activate Assistant</button>

#     <script>
#         function toggleAssistant() {
#             var button = document.getElementById('activate-btn');
#             var buttonText = button.innerText;

#             if (buttonText === 'Activate Assistant') {
#                 button.innerText = 'Deactivate';
#                 button.disabled = true;

#                 fetch('/activate_assistant', { method: 'POST' })
#                     .then(response => response.json())
#                     .then(data => {
#                         console.log(data.response);
#                         alert(data.response); // Display response in an alert
#                         button.disabled = false;
#                     })
#                     .catch(error => {
#                         console.error('Error:', error);
#                         alert('An error occurred. Please try again.');
#                         button.disabled = false;
#                     });
#             } else {
#                 button.innerText = 'Activate Assistant';
#                 button.disabled = true;

#                 fetch('/deactivate_assistant', { method: 'POST' })
#                     .then(response => response.json())
#                     .then(data => {
#                         console.log(data.response);
#                         alert(data.response); // Display response in an alert
#                         button.disabled = false;
#                     })
#                     .catch(error => {
#                         console.error('Error:', error);
#                         alert('An error occurred. Please try again.');
#                         button.disabled = false;
#                     });
#             }
#         }
#     </script>
# </body>
# </html>


# app.py
from flask import Flask, render_template, jsonify
import threading
from speech_loop import speech_loop, stop_speech_loop, start_speech_loop


app = Flask(__name__)

# Flag to indicate if the assistant is active
assistant_active = False

class Assistant:
    def __init__(self):
        self.speech_thread = None

    def send_response(self, message):
        return jsonify({"response": message})

    def activate_assistant(self):
        global assistant_active
        if not assistant_active:
            start_speech_loop()  # Ensure active is set to True
            self.speech_thread = threading.Thread(target=speech_loop)
            self.speech_thread.start()
            assistant_active = True
            return self.send_response("Assistant activated")
        else:
            return self.send_response("Assistant is already active")

    def deactivate_assistant(self):
        global assistant_active
        if assistant_active:
            stop_speech_loop()
            assistant_active = False
            print("The Bot is Deactivated")
            return self.send_response("Assistant deactivated")
        else:
            return self.send_response("Assistant is not active")
  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activate_assistant', methods=['POST'])
def activate_assistant_route():
    return assistant.activate_assistant()

@app.route('/deactivate_assistant', methods=['POST'])
def deactivate_assistant_route():
    return assistant.deactivate_assistant()

if __name__ == '__main__':
    assistant = Assistant()
    app.run(debug=True)


# speech_loop.py
import sys
import speech_recognition as sr
import pyttsx3
import time
import datetime
import threading
import openai
from dotenv import load_dotenv
from speech_loop2 import speech_loop2
from ss import *

status_lock = threading.Lock()
load_dotenv()
OPENAI_KEY = chatgpt_API
openai.api_key = OPENAI_KEY

active = True

speaking_lock = threading.Lock()

class Assistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def send_to_chatGPT(self, messages, model="gpt-3.5-turbo"):
        try:
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
        except Exception as e:
            print(f"An error occurred in send_to_chatGPT: {e}")
            return None

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
        try:
            with speaking_lock:
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)
                engine.say(text)
                engine.runAndWait()
        except Exception as e:
            print(f"An error occurred in speak: {e}")

    def run_voice_loop(self):
        global active  # Declare active as global
        while active:
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
                        # current_result_on()
                        active = False  # Stop the loop
                        
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



#second file

# app.py
from flask import Flask, render_template, jsonify, request
import threading
from speech_loop import speech_loop, stop_speech_loop, start_speech_loop
from speech_loop2 import stop_speech_loop, start_speech_loop
import sys
from io import StringIO

app = Flask(__name__)

# Flag to indicate if the assistant is active
assistant_active = False

class Assistant:
    def __init__(self):
        self.speech_thread = None

    def send_response(self, message):
        return jsonify({"response": message})

    def activate_assistant(self):
        global assistant_active
        if not assistant_active:
            start_speech_loop()  # Start the speech loop
            self.speech_thread = threading.Thread(target=speech_loop)
            self.speech_thread.start()
            assistant_active = True
            print("Assistant Power On")
            return self.send_response("Assistant Power On")
        else:
            print("Assistant is already On")
            return self.send_response("Assistant is already On")

    def deactivate_assistant(self):
        global assistant_active
        if assistant_active:
            stop_speech_loop()
            assistant_active = False
            print("Assistant Power is Off")
            return self.send_response("Assistant Off")
        else:
            print("Assistant is not Off")
            return self.send_response("Assistant is not Off")
  
class StdoutCapture:
    def __init__(self):
        self.buffer = StringIO()

    def write(self, text):
        self.buffer.write(text)

    def flush(self):
        pass

    def clear_output(self):
        self.buffer.truncate(0)  # Clear the buffer
        self.buffer.seek(0)  # Reset the cursor to the beginning

    def get_output(self):
        return self.buffer.getvalue()

# Create an instance of the capture class
stdout_capture = StdoutCapture()

# Redirect stdout to the custom capture object
sys.stdout = stdout_capture

@app.route('/get_output')
def get_output():
    return stdout_capture.get_output().replace('\n', '<br>')

@app.route('/clear_output', methods=['POST'])
def clear_output():
    stdout_capture.clear_output()
    return jsonify({"message": "Output cleared"})

@app.route('/')
def index():
    return render_template('index.html', assistant_active=assistant_active)

@app.route('/activate_assistant', methods=['POST'])
def activate_assistant_route():
    assistant = Assistant()  # Create a new instance for each request
    return assistant.activate_assistant()

@app.route('/deactivate_assistant', methods=['POST'])
def deactivate_assistant_route():
    assistant = Assistant()  # Create a new instance for each request
    return assistant.deactivate_assistant()

if __name__ == '__main__':
    app.run(debug=True)



# speech_loop.py
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

                    print("You said:", text)

                    if "activate" == text or "thunder activate" in text or "bolt activate" in text:
                        self.say_and_wait("Activated")
                        print("Activated")
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




# speech_loop2.py
import speech_recognition as sr
import randfacts
import threading
import tkinter as tk 
import datetime
from jokes_news_weather import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import subprocess
import sys
import pyautogui
from applications import *
import webbrowser

from word2number import w2n
import pyttsx3

today_date = datetime.datetime.now()
# Extract hour and minute from the scheduled time
hour = today_date.hour
minute = today_date.minute

# Convert to 12-hour format with AM/PM
period = "am" if hour < 12 else "pm"
hour_12 = hour % 12 if hour % 12 != 0 else 12  # Convert 0 to 12 for 12-hour format
scheduled_time_str = f"{hour_12:02d}:{minute:02d} {period}"

class Info_And_Music:
    def __init__(self, recognizer, mic, assistant):
        self.driver = webbrowser.get()
        self.recognizer = recognizer
        self.mic = mic
        self.assistant = assistant

    def get_info_wikipedia(self, query):
        self.query = query
        self.driver.open(f"https://www.wikipedia.org/w/index.php?search={query}")
        self.perform_actions_after_button_click()
        
    def get_info_google(self, query):
        self.query = query
        self.driver.open(f"https://www.google.com/search?q={query}")
        self.perform_actions_after_button_click()

    def perform_actions_after_button_click(self):
        print("Still listening")    # Print "still listening" after restarting the loop
        speech_loop2(self.recognizer, self.mic, self.assistant)
        
    def get_music(self, query):
        self.query = query
        self.driver.open(f"https://open.spotify.com/search/{query}")
        self.perform_actions_after_button_click()

    def perform_actions_after_button_click(self):
        print("Still listening")    # Print "still listening" after restarting the loop
        speech_loop2(self.recognizer, self.mic, self.assistant)


class Youtube_And_WhatsApp:
    def __init__(self, recognizer, mic, assistant):
        # self.options = options
        options = webdriver.FirefoxOptions()
        options.add_argument("--profile=C:/Users/bil/AppData/Roaming/Mozilla/Firefox/Profiles/v6hl3ec4.default-release")
        
        self.driver = webdriver.Firefox(options=options)
        self.recognizer = recognizer
        self.mic = mic
        self.assistant = assistant


    def whatsapp_message(self, receiver_name,text, user_time, user_scheduled_time_str):
        self.receiver_name = receiver_name
        self.text = text
        self.user_time = user_time
        self.user_scheduled_time_str = user_scheduled_time_str
        
        self.wait = WebDriverWait(self.driver, 100)
        self.driver.get("https://web.whatsapp.com/")

        contact_path = f'//span[contains(@title,"{receiver_name.capitalize()}")]'
        contact = self.wait.until(EC.presence_of_element_located((By.XPATH, contact_path)))
        contact.click()

        message_box_path = "//div[@contenteditable='true'][@data-tab='10']"
        message_box = self.wait.until(EC.presence_of_element_located((By.XPATH, message_box_path)))
        
        if user_time == "now":
            # Use ActionChains to simulate typing the message and pressing Enter
            actions = ActionChains(self.driver)
            actions.send_keys_to_element(message_box, text)
            actions.send_keys(Keys.ENTER)
            actions.perform()   
        elif user_time == "make a schedule":
            schedule_running = True
            while schedule_running:
                # Update the current time in each iteration
                today_date = datetime.now()
                hour = today_date.hour
                minute = today_date.minute
                period = "am" if hour < 12 else "pm"
                hour_12 = hour % 12 if hour % 12 != 0 else 12
                scheduled_time_str = f"{hour_12:02d}:{minute:02d} {period}"

                if user_scheduled_time_str == scheduled_time_str:
                    # Use ActionChains to simulate typing the message and pressing Enter
                    actions = ActionChains(self.driver)
                    actions.send_keys_to_element(message_box, text)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()
                    print("The Message has been delivered!")
                    schedule_running = False
                    
        self.perform_actions_after_button_click()
        while True:
            pass
        
    def play_vedio(self, query):
        self.query = query
        self.driver.get("https://www.youtube.com/results?search_query=" + query)
        video = self.driver.find_element(By.XPATH, '//*[@id="dismissible"]')
        video.click()
        self.perform_actions_after_button_click()
        while True:
            pass

    def perform_actions_after_button_click(self):
        print("Still listening")    # Print "still listening" after restarting the loop
        speech_loop2(self.recognizer, self.mic, self.assistant)

NOTE_STRS = ["make a note", "write this down", "remember this", "write a note on notepad"]  

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt" # we use this to remove the colon b/c colon is not allowed to save file
    with open(file_name, "w") as f:     # we use the "w" mode to rewrite the file or to create if it's not created
        f.write(text)
       
    vs_code = r"C:\Users\bil\AppData\Local\Programs\Microsoft VS Code\Code.exe"  
    # subprocess.Popen([vs_code, file_name])
    subprocess.Popen(["notepad.exe", file_name])


# Lock for managing access to the speaking engine
speaking_lock = threading.Lock()
# Global flag to control the speech loop
active = True

# Initialize deactivate_requested flag
deactivate_requested = False

def speech_loop2(recognizer, mic, assistant):
    global active, deactivate_requested
    while active:
        try:
            audio = recognizer.listen(mic, timeout=1, phrase_time_limit=None)
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)
            
            with speaking_lock:
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)
                
            # if any(keyword in text for keyword in ["hi", "jarvis", "hi thunder", "hello", "hey"]):
            if "hi" == text or "hi thunder" in text or "hello" == text or "hey" == text:
                assistant.speak("Hello boss, good " + assistant.wishme() + ", What can I do for you?")
        
                print("Hi I'm listening")
                
            elif "activated" in text:
                continue
            
            elif "information" in text or "open wikipedia" in text:
                assistant.speak("You need information related to which topics?")
        

                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    infor = recognizer.recognize_google(audio)

                print("searching {} in Wikipedia".format(infor))
                assistant.speak("searching {} in Wikipedia".format(infor))
        
                assist = Info_And_Music(recognizer, mic, assistant)  # Assuming Infow is the class from your existing code
                assist.get_info_wikipedia(infor)
                print("I'm listening")
                
                
                # Start a timer to restart the loop after 10 seconds
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start()
                                   
            elif "play" and "video" in text:
                assistant.speak("You want me to play which video?")
        
                
                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    vid = recognizer.recognize_google(audio)  
                    
                print("Playing {} on YouTube".format(vid))
                assistant.speak("Playing {} on YouTube".format(vid))
        
                assist = Youtube_And_WhatsApp(recognizer, mic, assistant)
                assist.play_vedio(vid) 
                print("I'm listening")
                 
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start() 
                                    
            elif "send message" in text or "open whatsapp" in text or "send a message" in text:
                
                while True:
                    assistant.speak("To whom do you want to send a message from your contact tell me his name?")
            
                    try:
                        with sr.Microphone() as source:
                            print("Running!!")
                            audio = recognizer.listen(source)
                            contact_name = recognizer.recognize_google(audio)  
                        
                        assistant.speak(f"Tell me what message you want to send?")
                
                        print(f"Tell me what message you want to send?")
                        
                        with sr.Microphone() as source:
                            print("Running!!")
                            audio = recognizer.listen(source)
                            user_text = recognizer.recognize_google(audio) 
                            
                        assistant.speak(f"This is your message: {user_text}")
                
                        print(f"This is your message: {user_text}")
                            
                        assistant.speak(f"And the time is {scheduled_time_str} You want to send this message to {contact_name} 'now' or 'make a schedule' and also you can 'cancel or stop' the message: ")
                
                        print(f"And the time is {scheduled_time_str} You want to send this message to {contact_name} 'now' or 'make a schedule' and also you can 'cancel or stop' the message: ")
                    
                        with sr.Microphone() as source:
                            print("Listening")
                            audio = recognizer.listen(source)
                            time = recognizer.recognize_google(audio) 
                            
                        if "now" in time:
                            assistant.speak("The message will be send in few second!")
                    
                            print("The message will be send in few second!")
                            user_time_input = "now"
                            user_scheduled_input = "now"
                            
                            break
                            
                        elif "cancel" in time or "stop" in time:
                            print("Still listening")    # Print "still listening" after restarting the loop
                            speech_loop2(recognizer, mic, assistant) 

                        elif "make a schedule" in time:
                            assistant.speak("What time: ")
                    
                            print("What time: ")
                            while True:
                                try:
                                    with sr.Microphone() as source:
                                        print("Listening")
                                        audio = recognizer.listen(source)
                                        recognized_word = recognizer.recognize_google(audio).lower()

                                    # Try to convert recognized word to a number
                                    try:
                                        user_hour = w2n.word_to_num(recognized_word)
                                        # Break out of the loop if conversion is successful
                                        break
                                    except ValueError:
                                        print("Invalid input. Please repeat the hour.")

                                except sr.UnknownValueError:
                                    print("Speech Recognition could not understand audio. Please repeat the input.")
                                except sr.RequestError as e:
                                    print(f"Could not request results from Google Speech Recognition service; {e}")
                                    # Handle the request error as needed
                            
                            assistant.speak("What Minute: ")
                    
                            print("What Minute: ")
                            while True:
                                try:
                                    with sr.Microphone() as source:
                                        print("Listening")
                                        audio = recognizer.listen(source)
                                        recognized_word = recognizer.recognize_google(audio).lower()

                                    # Try to convert recognized word to a number
                                    try:
                                        user_min = w2n.word_to_num(recognized_word)
                                        # Break out of the loop if conversion is successful
                                        break
                                    except ValueError:
                                        print("Invalid input. Please repeat the hour.")

                                except sr.UnknownValueError:
                                    print("Speech Recognition could not understand audio. Please repeat the input.")
                                except sr.RequestError as e:
                                    print(f"Could not request results from Google Speech Recognition service; {e}")
                                    # Handle the request error as needed
                                    
                            assistant.speak("am or pm: ")
                    
                            print("am or pm: ")
                            while True:
                                try:
                                    with sr.Microphone() as source:
                                        print("Listening")
                                        audio = recognizer.listen(source)
                                        the_am_pm = recognizer.recognize_google(audio) 
                                    if "a" in the_am_pm:
                                        user_am_pm = "am"  
                                        break
                                    elif "p" in the_am_pm:
                                        user_am_pm = "pm"
                                        break
                                except ValueError:  
                                    print(f"You said: {the_am_pm} Enter the correct value please!")
                            
                            user_scheduled_input = f"{user_hour:02d}:{user_min:02d} {user_am_pm}"
                            print(f"You put schedule {user_scheduled_input}")
                            
                            assistant.speak(f"The time is {scheduled_time_str} and your message will be sent on: {user_scheduled_input}")
                    
                            print(f"The time is {scheduled_time_str} and your message will be sent on: {user_scheduled_input}")
                            
                            user_time_input = "make a schedule"
                            break
                        else:
                            print(f"You said {time} Invalid choice please select: 'now' , 'make a schedule' or 'cancel or stop'. \nTry again!")
                            assistant.speak(f"You said {time} Invalid choice please select: 'now' or 'make a schedule' or 'cancel or stop'. \nTry again!")
                    
                     
                    
                    except sr.UnknownValueError:
                        print("Speech Recognition could not understand audio. Please repeat the input.")
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                        
            
                assist = Youtube_And_WhatsApp(recognizer, mic, assistant)
                assist.whatsapp_message(contact_name, user_text, user_time_input, user_scheduled_input) 
                print("I'm listening")
                
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start() 
                
            elif "open" and "song" in text or "open" and "music" in text:
                assistant.speak("You want me to open which Song?")
        
                
                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    vid = recognizer.recognize_google(audio)  
                    
                print("Opening {} on Spotify".format(vid))
                assistant.speak("Opening {} on Spotify".format(vid))
        
                assist = Info_And_Music(recognizer, mic, assistant)
                assist.get_music(vid) 
                print("I'm listening")
                 
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start() 
                
            elif "news" in text:
                print("Sure sir, Now I will read news for you.")
                assistant.speak("Sure sir, Now I will read news for you.")
        
                arr = news()
                for i in range(len(arr)):
                    print(arr[i])
                    assistant.speak(arr[i])
              
                    print("I'm listening")
                  
            elif "fact" in text or "facts" in text:
                print(text)
                assistant.speak("Sure sir,")
        
                x = randfacts.get_fact()
                print(x)
                assistant.speak("Did you know that, " + x)
        
                print("I'm listening")
                              
            elif "joke" in text or "jokes" in text:
                assistant.speak("Sure sir, get ready for some chuckles")
        
                ar = joke()
                print(ar[0])
                assistant.speak(ar[0])
        
                print(ar[1])
                assistant.speak(ar[1])
        
                print("I'm listening")
                
            elif "temperature " in text or "weather" in text or "time" in text or "date" in text:
                assistant.speak("The Weather today is,")
        
                print("Today is " + today_date.strftime("%d") + " of " + today_date.strftime("%B") + " And the time is " + (today_date.strftime("%I")) + ":" + (today_date.strftime("%M")) + ":" + (today_date.strftime("%p"))) 
                assistant.speak("Today is " + today_date.strftime("%d") + " of " + today_date.strftime("%B") + " And the time is " + (today_date.strftime("%I")) + (today_date.strftime("%M")) + (today_date.strftime("%p")))
        
                print("Temperature in addis ababa is " + str(temp()) + " degree celsius " + " and with " + str(des()))
                assistant.speak("temperature in addis ababa is " + str(temp()) + " degree celsius " + " and with " + str(des()) )
        
                print("I'm listening")
                
            elif "tell me about you" in text or "who are you" in text:
                print("I am an AI voice assistance that is developed by the one of the most greatest programmer and his name is Bilal Nesru, I can help you on: \n1, Play video on YouTube \n2, Search Information on Wikipedia \n3, Write letter and write some words by another languages \n4, Etc..")
                assistant.speak("I am an AI voice assistance that is developed by the one of the most greatest programmer and his name is Belal Nesru, I can help you on: \n1, Play video on YouTube \n2, Search Information on Wikipedia \n3, Write letter and write some words by another languages \n4, Etc..")
        
                print("I'm listening")
                
            
            elif any(phrase in text for phrase in NOTE_STRS):
                assistant.speak("What would you like me to write down?")
        
                print("What would you like me to write down?")
                
                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    user_note = recognizer.recognize_google(audio)
                note_text = user_note
                note(note_text)
                assistant.speak("I've made a note of that.")
        
                print("I'm listening")
               
            elif "search" in text or "open google" in text:
                assistant.speak("Tell me what do you want to search?")
        

                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    infor = recognizer.recognize_google(audio)

                print("searching {} in Google".format(infor))
                assistant.speak("searching {} in Google".format(infor))
        
                assist = Info_And_Music(recognizer, mic, assistant)  # Assuming Infow is the class from your existing code
                assist.get_info_google(infor)
                print("I'm listening")
                
                # Start a timer to restart the loop after 10 seconds
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start()
            
            elif "open application" in text or "application" in text or "open app" in text:
                assistant.speak("Which application you want me to open from the list:")
        
                print("Which application you want me to open from the list:")
                
                for i, app_name in enumerate(application_list, start=1):
                    print(i, app_name)

                with sr.Microphone() as source:
                    audio = recognizer.listen(source)

                app_choice = recognizer.recognize_google(audio).lower()
                selected_app_path = application_list.get(app_choice)

                if selected_app_path:
                    print(f"Opening {app_choice}")
                    assistant.speak(f"Opening {app_choice}")
            

                    try:
                        subprocess.Popen([selected_app_path])
                    except FileNotFoundError:
                        print("Running!!")
                        webbrowser.open(selected_app_path)
                    
                    print("Still Listening")
                else:
                    print("You said:", app_choice)
                    print("Invalid application choice.")
                    assistant.speak("Invalid application choice.")
            
                    print("Still Listening")


            elif "minimize" in text:
                print("Minimizing the active window.")
                
                pyautogui.hotkey("winleft", "down")
                assistant.speak("Minimizing the active window.")
        
                print("I'm listening")
            elif "maximize" in text:
                print("Maximizing the active window.")
                
                pyautogui.hotkey("winleft", "up")
                assistant.speak("Maximizing the active window.")
        
                print("I'm listening")
                
            elif "change the window" in text:
                print("Changing to another window.")
                
                pyautogui.hotkey("alt", "tab")
                assistant.speak("Changing to another window.")
        
                print("I'm listening")
                
            elif "show me the open windows" in text or "is there any open window" in text:
                print("Showing all the open windows.")
                
                pyautogui.hotkey("win", "tab")
                assistant.speak("Showing all the open windows.")
        
                print("I'm listening")
                
            elif "hide the windows" in text or "hide the window" in text:
                print("Hiding the active windows.")
                pyautogui.hotkey("win", "d")
                assistant.speak("hiding the active windows.")
        
                print("I'm listening")
                
            elif "show the windows" in text or "show the window" in text:
                print("Restoring the windows.")
                pyautogui.hotkey("win", "d")
                assistant.speak("Restoring the windows.")
        
                print("I'm listening")

            elif "exit" in text or "close" in text:
                print("Closing the active window.")
                
                pyautogui.hotkey("alt", "f4")
                assistant.speak("Closing the active window.")
        
                print("I'm listening")

             
            elif "deactivate" in text:
                print("Deactivated")
                assistant.speak("Deactivate")
                # active = False
                deactivate_requested = True  # Set the flag for deactivation request
                return deactivate_requested  # Return the flag after setting it
                
            elif text:
                messages = [{"role": "user", "content": text}]
                response = assistant.send_to_chatGPT(messages)
                print("You said: \n", text)
                print("Chat GPT: \n", response)
                assistant.speak(response)
        
                print("I'm listening")
                
                
                
                
                
                
        except sr.WaitTimeoutError:
            # Handle timeout (no speech detected within the timeout)
            continue
        except sr.UnknownValueError:
            # Handle unknown value (speech could not be understood)
            continue
        except sr.RequestError as e:
            # Handle request error (could not request results from Google Speech Recognition service)
            if "recognition connection failed" in str(e):
                print("Connection to the Google Speech Recognition service failed. Please check your internet connection.")
            else:
                print(f"Could not request results from Google Speech Recognition service: {e}")
            continue
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            continue


def start_speech_loop():
    global active
    active = True

def stop_speech_loop():
    global active
    active = False




# index.html
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Voice Assistant</title>
#     <link rel="stylesheet" href="static/style.css">
    
#     <script>
#         // Update button text based on assistant active state
#         window.onload = function() {
#             const assistantActive = {{ assistant_active | tojson }};
#             const button = document.getElementById('activate-btn');
#             button.innerText = assistantActive ? 'Deactivate Assistant' : 'Activate Assistant';
#         };

#         function toggleAssistant() {
#             var button = document.getElementById('activate-btn');
#             var buttonText = button.innerText;

#             if (buttonText === 'Activate Assistant') {
#                 button.innerText = 'Deactivate Assistant';
#                 button.disabled = true;

#                 fetch('/activate_assistant', { method: 'POST' })
#                     .then(response => response.json())
#                     .then(data => {
#                         console.log(data.response);
#                         alert(data.response); // Display response in an alert
#                         button.disabled = false;
#                         document.getElementById('robotImg').src = "static/img/chatbot_2.png";
#                     })
#                     .catch(error => {
#                         console.error('Error:', error);
#                         alert('An error occurred. Please try again.');
#                         button.disabled = false;
#                     });
#             } else {
#                 button.innerText = 'Activate Assistant';
#                 button.disabled = true;

#                 fetch('/deactivate_assistant', { method: 'POST' })
#                     .then(response => response.json())
#                     .then(data => {
#                         console.log(data.response);
#                         alert(data.response); // Display response in an alert
#                         button.disabled = false;
#                         document.getElementById('robotImg').src = "static/img/chatbot.png";
#                     })
#                     .catch(error => {
#                         console.error('Error:', error);
#                         alert('An error occurred. Please try again.');
#                         button.disabled = false;
#                     });
#             }
#         }
        
#         function fetchOutput() {
#             fetch('/get_output')
#             .then(response => response.text())
#             .then(data => {
#                 document.getElementById('output').innerHTML = data;
        
#                 // Split the data by newline characters
#                 const lines = data.split('\n');
#                 let lastDeactivateIndex = -1;
#                 let lastActivateIndex = -1;
        
#                 // Iterate over the lines in reverse order to find the last occurrence of "You said: deactivate"
#                 for (let i = lines.length - 1; i >= 0; i--) {
#                     if (lines[i].includes("You said: deactivate")) {
#                         lastDeactivateIndex = i;
#                         break;
#                     }
#                 }
        
#                 // Iterate over the lines in reverse order to find the last occurrence of "You said: activate"
#                 for (let i = lines.length - 1; i >= 0; i--) {
#                     if (lines[i].includes("You said: activate")) {
#                         lastActivateIndex = i;
#                         break;
#                     }
#                 }
        
#                 // Check if "You said: deactivate" was found
#                 if (lastDeactivateIndex !== -1) {
#                     document.getElementById('Result').innerText = "Waiting for activation word!";
#                     document.getElementById('robotImg').src = "static/img/chatbot_2.png";
#                 } else if (lastActivateIndex !== -1) {
#                     document.getElementById('Result').innerText = "Welcome, I'm activated";
#                     document.getElementById('robotImg').src = "static/img/chatbot_3.png";
#                 } else {
#                     document.getElementById('Result').innerText = ""; // Clear the result if not activated
#                 }
#             })
#             .catch(error => console.error('Error:', error));
#         }
        
#         // Fetch output every second
#         setInterval(fetchOutput, 1000);

#         function clearOutput() {
#             document.getElementById('output').innerHTML = "";
#             fetch('/clear_output', { method: 'POST' }) // Clear the captured output on the server side
#                 .then(response => response.json())
#                 .then(data => console.log(data.message))
#                 .catch(error => console.error('Error:', error));
#         }
#     </script>
# </head>
# <body>
#     <h1>Voice Assistant</h1>
#     <div class="robotImg"><img id="robotImg" src="static/img/chatbot.png" alt="robot logo"></div>
#     <button id="activate-btn" onclick="toggleAssistant()"></button>
#     <p id="Result"></p>
#     <div id="output"></div> <!-- Output will be displayed here -->

#     <div>
#         <button onclick="clearOutput()">Clear Text</button>
#     </div>
# </body>
# </html>


# need

    # $(".topImg2").click(function () {
    #     var contentDiv = document.getElementById("content1");
    #     var display = window.getComputedStyle(contentDiv).getPropertyValue("display");
    #     if (display === "none") {
    #         contentDiv.style.display = "block"; 
    #     } else {
    #         contentDiv.style.display = "none";  
    #     }; // Call the showCard function to toggle content visibility

    
    # <div class="container">
    #     <div class="card">
    #         <p class="topImg" onclick="showCard()">
    #             <img class="topImg2" id="robotImg" src="static/img/chatbot_4.png" alt="robot logo">
    #         </p>
    
    #         <div id="content1">
    #         <div>
    #             <h2>01</h2>
    #             <h3>Robot Status</h3>
    #             <h2>01</h2>
    #             <a href="#">
    #                 <button id="activate-btn" onclick="toggleAssistant()">Activate Assistant</button>
    #             </a>
    #         </div>
    #         </div>
    #     </div>
    
    #     <div class="container">
    #         <div class="card">
    #             <h2>01</h2>
    #             <p id="Result"></p>
    #             <div id="output"></div> <!-- Output will be displayed here -->
    #             <a href="#">
    #                 <button onclick="clearOutput()">Clear Text</button>
    #             </a>
    #         </div>
    #     </div>
    # </div>
    
    
    import speech_recognition as sr
import randfacts
import threading
import tkinter as tk 
import datetime
from jokes_news_weather import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import subprocess
import sys
import pyautogui
from applications import *
import webbrowser

from word2number import w2n
import pyttsx3

today_date = datetime.datetime.now()
# Extract hour and minute from the scheduled time
hour = today_date.hour
minute = today_date.minute

# Convert to 12-hour format with AM/PM
period = "am" if hour < 12 else "pm"
hour_12 = hour % 12 if hour % 12 != 0 else 12  # Convert 0 to 12 for 12-hour format
scheduled_time_str = f"{hour_12:02d}:{minute:02d} {period}"

class Info_And_Music:
    def __init__(self, recognizer, mic, assistant):
        self.driver = webbrowser.get()
        self.recognizer = recognizer
        self.mic = mic
        self.assistant = assistant

    def get_info_wikipedia(self, query):
        self.query = query
        self.driver.open(f"https://www.wikipedia.org/w/index.php?search={query}")
        self.perform_actions_after_button_click()
        
    def get_info_google(self, query):
        self.query = query
        self.driver.open(f"https://www.google.com/search?q={query}")
        self.perform_actions_after_button_click()

    def perform_actions_after_button_click(self):
        print("Still listening")    # Print "still listening" after restarting the loop
        speech_loop2(self.recognizer, self.mic, self.assistant)
        
    def get_music(self, query):
        self.query = query
        self.driver.open(f"https://open.spotify.com/search/{query}")
        self.perform_actions_after_button_click()

    def perform_actions_after_button_click(self):
        print("Still listening")    # Print "still listening" after restarting the loop
        speech_loop2(self.recognizer, self.mic, self.assistant)


class Youtube_And_WhatsApp:
    def __init__(self, recognizer, mic, assistant):
        # self.options = options
        options = webdriver.FirefoxOptions()
        options.add_argument("--profile=C:/Users/bil/AppData/Roaming/Mozilla/Firefox/Profiles/v6hl3ec4.default-release")
        
        self.driver = webdriver.Firefox(options=options)
        self.recognizer = recognizer
        self.mic = mic
        self.assistant = assistant


    def whatsapp_message(self, receiver_name,text, user_time, user_scheduled_time_str):
        self.receiver_name = receiver_name
        self.text = text
        self.user_time = user_time
        self.user_scheduled_time_str = user_scheduled_time_str
        
        self.wait = WebDriverWait(self.driver, 100)
        self.driver.get("https://web.whatsapp.com/")

        contact_path = f'//span[contains(@title,"{receiver_name.capitalize()}")]'
        contact = self.wait.until(EC.presence_of_element_located((By.XPATH, contact_path)))
        contact.click()

        message_box_path = "//div[@contenteditable='true'][@data-tab='10']"
        message_box = self.wait.until(EC.presence_of_element_located((By.XPATH, message_box_path)))
        
        if user_time == "now":
            # Use ActionChains to simulate typing the message and pressing Enter
            actions = ActionChains(self.driver)
            actions.send_keys_to_element(message_box, text)
            actions.send_keys(Keys.ENTER)
            actions.perform()   
        elif user_time == "make a schedule":
            schedule_running = True
            while schedule_running:
                # Update the current time in each iteration
                today_date = datetime.now()
                hour = today_date.hour
                minute = today_date.minute
                period = "am" if hour < 12 else "pm"
                hour_12 = hour % 12 if hour % 12 != 0 else 12
                scheduled_time_str = f"{hour_12:02d}:{minute:02d} {period}"

                if user_scheduled_time_str == scheduled_time_str:
                    # Use ActionChains to simulate typing the message and pressing Enter
                    actions = ActionChains(self.driver)
                    actions.send_keys_to_element(message_box, text)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()
                    print("The Message has been delivered!")
                    schedule_running = False
                    
        self.perform_actions_after_button_click()
        while True:
            pass
        
    def play_vedio(self, query):
        self.query = query
        self.driver.get("https://www.youtube.com/results?search_query=" + query)
        video = self.driver.find_element(By.XPATH, '//*[@id="dismissible"]')
        video.click()
        self.perform_actions_after_button_click()
        while True:
            pass

    def perform_actions_after_button_click(self):
        print("Still listening")    # Print "still listening" after restarting the loop
        speech_loop2(self.recognizer, self.mic, self.assistant)

NOTE_STRS = ["make a note", "write this down", "remember this", "write a note on notepad"]  

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt" # we use this to remove the colon b/c colon is not allowed to save file
    with open(file_name, "w") as f:     # we use the "w" mode to rewrite the file or to create if it's not created
        f.write(text)
       
    vs_code = r"C:\Users\bil\AppData\Local\Programs\Microsoft VS Code\Code.exe"  
    # subprocess.Popen([vs_code, file_name])
    subprocess.Popen(["notepad.exe", file_name])


# Lock for managing access to the speaking engine
speaking_lock = threading.Lock()
# Global flag to control the speech loop
active = True

# Initialize deactivate_requested flag
deactivate_requested = False

def speech_loop2(recognizer, mic, assistant):
    global active, deactivate_requested
    while active:
        try:
            audio = recognizer.listen(mic, timeout=1, phrase_time_limit=None)
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)
            
            with speaking_lock:
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)
                
            # if any(keyword in text for keyword in ["hi", "jarvis", "hi thunder", "hello", "hey"]):
            if "hi" == text or "hi thunder" in text or "hello" == text or "hey" == text:
                assistant.speak("Hello boss, good " + assistant.wishme() + ", What can I do for you?")
        
                print("Hi I'm listening")
                
            elif "activated" in text:
                continue
            
            elif "information" in text or "open wikipedia" in text:
                assistant.speak("You need information related to which topics?")
        

                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    infor = recognizer.recognize_google(audio)

                print("searching {} in Wikipedia".format(infor))
                assistant.speak("searching {} in Wikipedia".format(infor))
        
                assist = Info_And_Music(recognizer, mic, assistant)  # Assuming Infow is the class from your existing code
                assist.get_info_wikipedia(infor)
                print("I'm listening")
                
                
                # Start a timer to restart the loop after 10 seconds
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start()
                                   
            elif "play" and "video" in text:
                assistant.speak("You want me to play which video?")
        
                
                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    vid = recognizer.recognize_google(audio)  
                    
                print("Playing {} on YouTube".format(vid))
                assistant.speak("Playing {} on YouTube".format(vid))
        
                assist = Youtube_And_WhatsApp(recognizer, mic, assistant)
                assist.play_vedio(vid) 
                print("I'm listening")
                 
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start() 
                                    
            elif "send message" in text or "open whatsapp" in text or "send a message" in text:
                
                while True:
                    assistant.speak("To whom do you want to send a message from your contact tell me his name?")
            
                    try:
                        with sr.Microphone() as source:
                            print("Running!!")
                            audio = recognizer.listen(source)
                            contact_name = recognizer.recognize_google(audio)  
                        
                        assistant.speak(f"Tell me what message you want to send?")
                
                        print(f"Tell me what message you want to send?")
                        
                        with sr.Microphone() as source:
                            print("Running!!")
                            audio = recognizer.listen(source)
                            user_text = recognizer.recognize_google(audio) 
                            
                        assistant.speak(f"This is your message: {user_text}")
                
                        print(f"This is your message: {user_text}")
                            
                        assistant.speak(f"And the time is {scheduled_time_str} You want to send this message to {contact_name} 'now' or 'make a schedule' and also you can 'cancel or stop' the message: ")
                
                        print(f"And the time is {scheduled_time_str} You want to send this message to {contact_name} 'now' or 'make a schedule' and also you can 'cancel or stop' the message: ")
                    
                        with sr.Microphone() as source:
                            print("Listening")
                            audio = recognizer.listen(source)
                            time = recognizer.recognize_google(audio) 
                            
                        if "now" in time:
                            assistant.speak("The message will be send in few second!")
                    
                            print("The message will be send in few second!")
                            user_time_input = "now"
                            user_scheduled_input = "now"
                            
                            break
                            
                        elif "cancel" in time or "stop" in time:
                            print("Still listening")    # Print "still listening" after restarting the loop
                            speech_loop2(recognizer, mic, assistant) 

                        elif "make a schedule" in time:
                            assistant.speak("What time: ")
                    
                            print("What time: ")
                            while True:
                                try:
                                    with sr.Microphone() as source:
                                        print("Listening")
                                        audio = recognizer.listen(source)
                                        recognized_word = recognizer.recognize_google(audio).lower()

                                    # Try to convert recognized word to a number
                                    try:
                                        user_hour = w2n.word_to_num(recognized_word)
                                        # Break out of the loop if conversion is successful
                                        break
                                    except ValueError:
                                        print("Invalid input. Please repeat the hour.")

                                except sr.UnknownValueError:
                                    print("Speech Recognition could not understand audio. Please repeat the input.")
                                except sr.RequestError as e:
                                    print(f"Could not request results from Google Speech Recognition service; {e}")
                                    # Handle the request error as needed
                            
                            assistant.speak("What Minute: ")
                    
                            print("What Minute: ")
                            while True:
                                try:
                                    with sr.Microphone() as source:
                                        print("Listening")
                                        audio = recognizer.listen(source)
                                        recognized_word = recognizer.recognize_google(audio).lower()

                                    # Try to convert recognized word to a number
                                    try:
                                        user_min = w2n.word_to_num(recognized_word)
                                        # Break out of the loop if conversion is successful
                                        break
                                    except ValueError:
                                        print("Invalid input. Please repeat the hour.")

                                except sr.UnknownValueError:
                                    print("Speech Recognition could not understand audio. Please repeat the input.")
                                except sr.RequestError as e:
                                    print(f"Could not request results from Google Speech Recognition service; {e}")
                                    # Handle the request error as needed
                                    
                            assistant.speak("am or pm: ")
                    
                            print("am or pm: ")
                            while True:
                                try:
                                    with sr.Microphone() as source:
                                        print("Listening")
                                        audio = recognizer.listen(source)
                                        the_am_pm = recognizer.recognize_google(audio) 
                                    if "a" in the_am_pm:
                                        user_am_pm = "am"  
                                        break
                                    elif "p" in the_am_pm:
                                        user_am_pm = "pm"
                                        break
                                except ValueError:  
                                    print(f"You said: {the_am_pm} Enter the correct value please!")
                            
                            user_scheduled_input = f"{user_hour:02d}:{user_min:02d} {user_am_pm}"
                            print(f"You put schedule {user_scheduled_input}")
                            
                            assistant.speak(f"The time is {scheduled_time_str} and your message will be sent on: {user_scheduled_input}")
                    
                            print(f"The time is {scheduled_time_str} and your message will be sent on: {user_scheduled_input}")
                            
                            user_time_input = "make a schedule"
                            break
                        else:
                            print(f"You said {time} Invalid choice please select: 'now' , 'make a schedule' or 'cancel or stop'. \nTry again!")
                            assistant.speak(f"You said {time} Invalid choice please select: 'now' or 'make a schedule' or 'cancel or stop'. \nTry again!")
                    
                     
                    
                    except sr.UnknownValueError:
                        print("Speech Recognition could not understand audio. Please repeat the input.")
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                        
            
                assist = Youtube_And_WhatsApp(recognizer, mic, assistant)
                assist.whatsapp_message(contact_name, user_text, user_time_input, user_scheduled_input) 
                print("I'm listening")
                
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start() 
                
            elif "open" and "song" in text or "open" and "music" in text:
                assistant.speak("You want me to open which Song?")
        
                
                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    vid = recognizer.recognize_google(audio)  
                    
                print("Opening {} on Spotify".format(vid))
                assistant.speak("Opening {} on Spotify".format(vid))
        
                assist = Info_And_Music(recognizer, mic, assistant)
                assist.get_music(vid) 
                print("I'm listening")
                 
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start() 
                
            elif "news" in text:
                print("Sure sir, Now I will read news for you.")
                assistant.speak("Sure sir, Now I will read news for you.")
        
                arr = news()
                for i in range(len(arr)):
                    print(arr[i])
                    assistant.speak(arr[i])
              
                    print("I'm listening")
                  
            elif "fact" in text or "facts" in text:
                print(text)
                assistant.speak("Sure sir,")
        
                x = randfacts.get_fact()
                print(x)
                assistant.speak("Did you know that, " + x)
        
                print("I'm listening")
                              
            elif "joke" in text or "jokes" in text:
                assistant.speak("Sure sir, get ready for some chuckles")
        
                ar = joke()
                print(ar[0])
                assistant.speak(ar[0])
        
                print(ar[1])
                assistant.speak(ar[1])
        
                print("I'm listening")
                
            elif "temperature " in text or "weather" in text or "time" in text or "date" in text:
                assistant.speak("The Weather today is,")
        
                print("Today is " + today_date.strftime("%d") + " of " + today_date.strftime("%B") + " And the time is " + (today_date.strftime("%I")) + ":" + (today_date.strftime("%M")) + ":" + (today_date.strftime("%p"))) 
                assistant.speak("Today is " + today_date.strftime("%d") + " of " + today_date.strftime("%B") + " And the time is " + (today_date.strftime("%I")) + (today_date.strftime("%M")) + (today_date.strftime("%p")))
        
                print("Temperature in addis ababa is " + str(temp()) + " degree celsius " + " and with " + str(des()))
                assistant.speak("temperature in addis ababa is " + str(temp()) + " degree celsius " + " and with " + str(des()) )
        
                print("I'm listening")
                
            elif "tell me about you" in text or "who are you" in text:
                print("I am an AI voice assistance that is developed by the one of the most greatest programmer and his name is Bilal Nesru, I can help you on: \n1, Play video on YouTube \n2, Search Information on Wikipedia \n3, Write letter and write some words by another languages \n4, Etc..")
                assistant.speak("I am an AI voice assistance that is developed by the one of the most greatest programmer and his name is Belal Nesru, I can help you on: \n1, Play video on YouTube \n2, Search Information on Wikipedia \n3, Write letter and write some words by another languages \n4, Etc..")
        
                print("I'm listening")
                
            
            elif any(phrase in text for phrase in NOTE_STRS):
                assistant.speak("What would you like me to write down?")
        
                print("What would you like me to write down?")
                
                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    user_note = recognizer.recognize_google(audio)
                note_text = user_note
                note(note_text)
                assistant.speak("I've made a note of that.")
        
                print("I'm listening")
               
            elif "search" in text or "open google" in text:
                assistant.speak("Tell me what do you want to search?")
        

                with sr.Microphone() as source:
                    print("Running!!")
                    audio = recognizer.listen(source)
                    infor = recognizer.recognize_google(audio)

                print("searching {} in Google".format(infor))
                assistant.speak("searching {} in Google".format(infor))
        
                assist = Info_And_Music(recognizer, mic, assistant)  # Assuming Infow is the class from your existing code
                assist.get_info_google(infor)
                print("I'm listening")
                
                # Start a timer to restart the loop after 10 seconds
                threading.Timer(3, lambda: speech_loop2(recognizer, mic, assistant)).start()
            
            elif "open application" in text or "application" in text or "open app" in text:
                assistant.speak("Which application you want me to open from the list:")
        
                print("Which application you want me to open from the list:")
                
                for i, app_name in enumerate(application_list, start=1):
                    print(i, app_name)

                with sr.Microphone() as source:
                    audio = recognizer.listen(source)

                app_choice = recognizer.recognize_google(audio).lower()
                selected_app_path = application_list.get(app_choice)

                if selected_app_path:
                    print(f"Opening {app_choice}")
                    assistant.speak(f"Opening {app_choice}")
            

                    try:
                        subprocess.Popen([selected_app_path])
                    except FileNotFoundError:
                        print("Running!!")
                        webbrowser.open(selected_app_path)
                    
                    print("Still Listening")
                else:
                    print("You said:", app_choice)
                    print("Invalid application choice.")
                    assistant.speak("Invalid application choice.")
            
                    print("Still Listening")


            elif "minimize" in text:
                print("Minimizing the active window.")
                
                pyautogui.hotkey("winleft", "down")
                assistant.speak("Minimizing the active window.")
        
                print("I'm listening")
            elif "maximize" in text:
                print("Maximizing the active window.")
                
                pyautogui.hotkey("winleft", "up")
                assistant.speak("Maximizing the active window.")
        
                print("I'm listening")
                
            elif "change the window" in text:
                print("Changing to another window.")
                
                pyautogui.hotkey("alt", "tab")
                assistant.speak("Changing to another window.")
        
                print("I'm listening")
                
            elif "show me the open windows" in text or "is there any open window" in text:
                print("Showing all the open windows.")
                
                pyautogui.hotkey("win", "tab")
                assistant.speak("Showing all the open windows.")
        
                print("I'm listening")
                
            elif "hide the windows" in text or "hide the window" in text:
                print("Hiding the active windows.")
                pyautogui.hotkey("win", "d")
                assistant.speak("hiding the active windows.")
        
                print("I'm listening")
                
            elif "show the windows" in text or "show the window" in text:
                print("Restoring the windows.")
                pyautogui.hotkey("win", "d")
                assistant.speak("Restoring the windows.")
        
                print("I'm listening")

            elif "exit" in text or "close" in text:
                print("Closing the active window.")
                
                pyautogui.hotkey("alt", "f4")
                assistant.speak("Closing the active window.")
        
                print("I'm listening")

             
            elif "deactivate" in text:
                print("Deactivated")
                assistant.speak("Deactivate")
                # active = False
                deactivate_requested = True  # Set the flag for deactivation request
                return deactivate_requested  # Return the flag after setting it
                
            elif text:
                messages = [{"role": "user", "content": text}]
                response = assistant.send_to_chatGPT(messages)
                print("You said: \n", text)
                print("Chat GPT: \n", response)
                assistant.speak(response)
        
                print("I'm listening")
                
                
                
                
                
                
        except sr.WaitTimeoutError:
            # Handle timeout (no speech detected within the timeout)
            continue
        except sr.UnknownValueError:
            # Handle unknown value (speech could not be understood)
            continue
        except sr.RequestError as e:
            # Handle request error (could not request results from Google Speech Recognition service)
            if "recognition connection failed" in str(e):
                print("Connection to the Google Speech Recognition service failed. Please check your internet connection.")
            else:
                print(f"Could not request results from Google Speech Recognition service: {e}")
            continue
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            continue


def start_speech_loop():
    global active
    active = True

def stop_speech_loop():
    global active
    active = False



# sppech_loop.py
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
