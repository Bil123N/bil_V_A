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
