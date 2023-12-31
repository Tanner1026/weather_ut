import requests
import pandas as pd
from datetime import date
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap5
today = date.today()
header_map = {'accept': 'text/plain'}
API_KEY = 'wOYs2qlYuW7tA76UC3WTeHGpa4LWkXPR'
MAPS_API = 'AIzaSyCMoTTC1yzeNrfla_4IKB0XAQQUSYa1Ido'
URL_FORECAST = "https://api.tomorrow.io/v4/weather/forecast"
URL_CURRENT_WEATHER = "https://api.tomorrow.io/v4/weather/realtime?location=salt%20lake%20city&units=metric&apikey=wOYs2qlYuW7tA76UC3WTeHGpa4LWkXPR"
URL_MAPS = 'https://api.tomorrow.io/v4/map/tile/'

precip_params = ['cloudBase', 'cloudCeiling']
for param in precip_params:
    map = requests.get(f"https://api.tomorrow.io/v4/map/tile/2/0/1/{param}/now.png?apikey=wOYs2qlYuW7tA76UC3WTeHGpa4LWkXPR")
    with open(f'static/img/{param}.png', 'wb') as file:
        file.write(map.content)

temp_page_params = ['windSpeed', 'windDirection', 'windGust', 'dewPoint', 'temperature', 'temperatureApparent']
for param in temp_page_params:
        map = requests.get(f"https://api.tomorrow.io/v4/map/tile/2/0/1/{param}/now.png?apikey=wOYs2qlYuW7tA76UC3WTeHGpa4LWkXPR", headers=header_map)
        with open(f'static/img/{param}.png','wb') as file:
            file.write(map.content)

current_weather = requests.get(URL_CURRENT_WEATHER).json()
weather_path = current_weather['data']['values']

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/temperature')
def temp():
    return render_template('temperature.html', dewpoint=weather_path['dewPoint'], temp= weather_path['temperature'], temp_app= weather_path['temperatureApparent'], wind_dir= weather_path['windDirection'], wind_gust= weather_path['windGust'], wind_speed= weather_path['windSpeed'])


@app.route('/precipitation')
def precip():
    return render_template('precipitation.html')

@app.route('/air_quality')
def air_q():
    return render_template('air_quality.html')


app.run(debug=True)