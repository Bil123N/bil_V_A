import requests

url = "https://official-joke-api.appspot.com/random_joke"
json_data = requests.get(url).json()

arr = ["", ""]
arr[0] = json_data["setup"]
arr[1] = json_data["punchline"]

def joke():
    return arr


# News
from ss import *

api_address = "http://newsapi.org/v2/top-headlines?country=us&apiKey="+key
json_data = requests.get(api_address).json()

ar = []

def news():
    for i in range(3):
        ar.append("Number " + str(i + 1)+ ", " + json_data["articles"][i]["title"] + ".")
        
    return ar

# weather
api_address2 = f'https://api.weatherapi.com/v1/current.json?key={key2}&q=Ethiopia'
json_data2 = requests.get(api_address2).json()

def temp():
    temprature = round(json_data2["current"]["temp_c"])
    return temprature

def des():
    description = json_data2["current"]["condition"]["text"]
    return description
