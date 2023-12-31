import requests
import pandas as pd
from datetime import date
from flask import Flask, render_template, url_for, request, redirect
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from forms import EmailForm
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()
today = date.today()
header_map = {'accept': 'text/plain'}
URL_FORECAST = "https://api.tomorrow.io/v4/weather/forecast"
URL_CURRENT_WEATHER = f"https://api.tomorrow.io/v4/weather/realtime?location=salt%20lake%20city&units=metric&apikey={os.getenv('API_KEY')}"
URL_MAPS = 'https://api.tomorrow.io/v4/map/tile/'

precip_params = ['cloudBase', 'cloudCeiling']
for param in precip_params:
    map = requests.get(f"https://api.tomorrow.io/v4/map/tile/2/0/1/{param}/now.png?apikey={os.getenv('API_KEY')}")
    with open(f'static/img/precipitation_maps/{param}.png', 'wb') as file:
        file.write(map.content)

temp_page_params = ['windSpeed', 'windDirection', 'windGust', 'dewPoint', 'temperature', 'temperatureApparent']
for param in temp_page_params:
        map = requests.get(f"https://api.tomorrow.io/v4/map/tile/2/0/1/{param}/now.png?apikey={os.getenv('API_KEY')}", headers=header_map)
        with open(f'static/img/temp_wind_maps/{param}.png','wb') as file:
            file.write(map.content)

air_q_params = ['particulateMatter25', 'particulateMatter10', 'pollutantO3', 'pollutantNO2', 'pollutantCO', 'epaIndex']
for param in air_q_params:
        map = requests.get(f"https://api.tomorrow.io/v4/map/tile/2/0/1/{param}/now.png?apikey={os.getenv('API_KEY')}", headers=header_map)
        with open(f'static/img/air_q_maps/{param}.png','wb') as file:
            file.write(map.content)
    
try:
    current_weather = requests.get(URL_CURRENT_WEATHER).json()
    weather_path = current_weather['data']['values']
    success = True
except:
    success = False

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/temperature')
def temp():
    if success == True:
        try:
            return render_template('temperature.html', dewpoint=weather_path['dewPoint'], temp= weather_path['temperature'], temp_app= weather_path['temperatureApparent'], wind_dir= weather_path['windDirection'], wind_gust= weather_path['windGust'], wind_speed= weather_path['windSpeed'], success=success)
        except:
            return render_template('temperature.html', success=success)    
    else:
        return render_template('temperature.html', success=success)

@app.route('/precipitation')
def precip():
    if success == True:
        try:
            return render_template('precipitation.html', cloudBase = weather_path['cloudBase'], cloudCeiling = weather_path['cloudCeiling'], visibility= weather_path['visibility'], precip_probability= weather_path['precipitationProbability'], humidity= weather_path['humidity'], pressure=weather_path['pressureSurfaceLevel'], rain_intensity= weather_path['rainIntensity'], sleet_intensity = weather_path['sleetIntensity'], snow_intensity=weather_path['snowIntensity'], success=success)
        except:
            return render_template('precipitation.html', success=success)
    else:
        return render_template('precipitation.html', success=success)
    
@app.route('/air_quality')
def air_q():
    return render_template('air_quality.html')

@app.route('/contact-me', methods=['POST', 'GET'])
def contact():
    form = EmailForm()
    if form.validate_on_submit():
        name = form.name.data
        sender_email = form.email.data
        message = form.message.data
        email_contents = f'Subject:Weather Application Message\n\nName: {name}\nMessage: {message}'
        send_email(email_contents, sender_email)
        return redirect(url_for('thank_you'))
    return render_template('contact.html', form=form)

@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')

def send_email(contents, sender_email): 
    with smtplib.SMTP('smtp.gmail.com', port=587) as connection:
        connection.starttls()
        connection.login(os.getenv('ADMIN_EMAIL'), os.getenv('APP_PASSWORD'))
        connection.sendmail(from_addr=sender_email, to_addrs=os.getenv('ADMIN_EMAIL'), msg=contents)

app.run(debug=True)