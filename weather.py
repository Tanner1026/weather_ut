import threading
import json
from datetime import date, datetime
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from forms import EmailForm
import smtplib
from database import Database
import os
from dotenv import load_dotenv
import requests
import schedule
import time

load_dotenv()
URL_FORECAST = "https://api.tomorrow.io/v4/weather/forecast"
URL_CURRENT_WEATHER = f"https://api.tomorrow.io/v4/weather/realtime?location=salt%20lake%20city&apikey={os.getenv('API_KEY')}"
URL_MAPS = 'https://api.tomorrow.io/v4/map/tile/'
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
header_map = {'accept': 'text/plain'}
precip_params = ['cloudBase', 'cloudCeiling', 'visibility', 'precipitationIntensity', 'humidity', 'pressureSurfaceLevel']
today = date.today()

running=True

def api_execute():
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
        weather_path = current_weather['data']
        with open("weather_data.json", "w") as file:
            json.dump(weather_path, file)
    except:
        import smtplib
        with smtplib.SMTP('smtp.gmail.com', port=587) as connection:
            connection.starttls()
            connection.login(os.getenv('ADMIN_EMAIL'), os.getenv('APP_PASSWORD'))
            connection.sendmail(from_addr=os.getenv('ADMIN_EMAIL'), to_addrs=os.getenv('ADMIN_EMAIL'), msg="Subject: Weather application API failure\n\nThe website failed to call the API")

schedule.every().hour.do(api_execute)

def run_background():
    while running:
        schedule.run_pending()
        time.sleep(1)

t= threading.Thread(target=run_background)
t.start()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/temperature')
def temp():
    try:
        with open("weather_data.json", "r") as file:
            weather = json.load(file)
            time = weather['time'].split("T")
            weather_path=weather['values']
            return render_template('temperature.html', 
                                   dewpoint=weather_path['dewPoint'], 
                                   temp= weather_path['temperature'], 
                                   temp_app= weather_path['temperatureApparent'], 
                                   wind_dir= weather_path['windDirection'], 
                                   wind_gust= weather_path['windGust'], 
                                   wind_speed= weather_path['windSpeed'], 
                                   time = time[1],
                                   success=True)
    except:
        return render_template('temperature.html', success=False)    


@app.route('/precipitation')
def precip():
    try:
        with open("weather_data.json", "r") as file:
            weather = json.load(file)
            time = weather['time'].split("T")
            weather_path=weather['values']
            return render_template('precipitation.html', 
                                   cloudBase = weather_path['cloudBase'], 
                                   cloudCeiling = weather_path['cloudCeiling'], 
                                   visibility= weather_path['visibility'], 
                                   precip_probability= weather_path['precipitationProbability'], 
                                   humidity= weather_path['humidity'], 
                                   pressure=weather_path['pressureSurfaceLevel'], 
                                   rain_intensity= weather_path['rainIntensity'], 
                                   sleet_intensity = weather_path['sleetIntensity'], 
                                   snow_intensity=weather_path['snowIntensity'], 
                                   success=True, 
                                   time = time[1],
                                   api_key = os.getenv('API_KEY'))
    except:
        return render_template('precipitation.html', success=False)
    
@app.route('/air_quality')
def air_q():
    try:
        with open("weather_data.json", "r") as file:
            weather = json.load(file)
            time = weather['time'].split("T")
        success = True
        return render_template('air_quality.html', success = success, time=time[1])
    except:
        return render_template("air_quality.html", success= success)
    
@app.route('/weather-station')
def weather_station():
    with open("station_data.json", "r") as file:
        unedited_data = json.load(file)
        timestamp = datetime.strptime(unedited_data['timestamp'].split(".")[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %I:%M %p')
        temperature_c = round(float(unedited_data['temperature']), 1)
        temperature_f = round(float(temperature_c) * (9/5) + 32, 1)
        humidity = round(float(unedited_data['humidity']), 1)
        pressure = round(float(unedited_data['pressure']), 1)
        data = {
            'temperature_c': temperature_c,
            'temperature_f': temperature_f,
            'humidity': humidity,
            'pressure': pressure,
            'timestamp': timestamp
        }
    return render_template("saratoga_data.html", data=data)

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

def authentication(token):
    return str(token) == AUTH_TOKEN
    

@app.route("/weather_data/post", methods=['POST'])
@csrf.exempt
def data():
    token = request.headers.get('Authorization')
    try:
        if authentication(token) == True:
            temp = request.args.get('temperature')
            pressure = request.args.get('pressure')
            humidity = request.args.get('humidity')
            timestamp = request.args.get('timestamp')
            data = {'temperature': temp,
                    'pressure': pressure,
                    'humidity': humidity,
                    'timestamp': timestamp}
            
            with open("station_data.json", "w") as file:
                json.dump(data, file)

            db = Database()
            db.add_entry(data)
            db.disconnect()

            
            return jsonify({'message': 'Data was received', 'data': data}), 200
        else:
            return jsonify({'message': 'Authentication Failed'}), 401
    except:
        return jsonify({'message': 'Invalid API request'}), 400

def send_email(contents, sender_email): 
    with smtplib.SMTP('smtp.gmail.com', port=587) as connection:
        connection.starttls()
        connection.login(os.getenv('ADMIN_EMAIL'), os.getenv('APP_PASSWORD'))
        connection.sendmail(from_addr=sender_email, to_addrs=os.getenv('ADMIN_EMAIL'), msg=contents)

app.run(host="0.0.0.0", debug=True)

