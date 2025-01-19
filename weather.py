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
import pytz
from graphing import Grapher

load_dotenv()
URL_FORECAST = "https://api.tomorrow.io/v4/weather/forecast"
URL_CURRENT_WEATHER = f"https://api.tomorrow.io/v4/weather/realtime?location=40.760780%2C%20-111.891045&units=metric&apikey={os.getenv('API_KEY')}"
URL_HEADERS = {"accept": "application/json"}
URL_MAPS = 'https://api.tomorrow.io/v4/map/tile/'
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
header_map = {'accept': 'text/plain'}

today = date.today()
running=True

def authentication(token):
    return str(token) == AUTH_TOKEN

def send_email(contents, sender_email): 
    with smtplib.SMTP('smtp.gmail.com', port=587) as connection:
        connection.starttls()
        connection.login(os.getenv('ADMIN_EMAIL'), os.getenv('APP_PASSWORD'))
        connection.sendmail(from_addr=sender_email, to_addrs=os.getenv('ADMIN_EMAIL'), msg=contents)

def create_graph(start_date, end_date, data_type, temp_units, station_id):
    db = Database()
    print(station_id)
    results = db.graphical_results(start_date=start_date, end_date=end_date, data_type=data_type, station_id=station_id)
    grapher = Grapher()
    grapher.create_graphs(data=results, data_type=data_type, temp_units=temp_units)

def api_execute():
    try:
        precip_params = ['cloudBase', 'cloudCeiling', 'visibility', 'precipitationIntensity', 'humidity', 'pressureSurfaceLevel']
        for param in precip_params:
            map = requests.get(f"https://api.tomorrow.io/v4/map/tile/2/0/1/{param}/now.png?apikey={os.getenv('API_KEY')}")
            time.sleep(5)
            with open(f'static/img/precipitation_maps/{param}.png', 'wb') as file:
                file.write(map.content)

        temp_page_params = ['windSpeed', 'windDirection', 'windGust', 'dewPoint', 'temperature', 'temperatureApparent']
        for param in temp_page_params:
                map = requests.get(f"https://api.tomorrow.io/v4/map/tile/2/0/1/{param}/now.png?apikey={os.getenv('API_KEY')}", headers=header_map)
                time.sleep(5)
                with open(f'static/img/temp_wind_maps/{param}.png','wb') as file:
                    file.write(map.content)
    
        current_weather = requests.get(URL_CURRENT_WEATHER, URL_HEADERS).json()
        weather_path = current_weather['data']
        with open("weather_data.json", "w") as file:
            timestamp_utc=weather_path['time']
            utc_dt = datetime.strptime(timestamp_utc, "%Y-%m-%dT%H:%M:%SZ")
            utc_zone = pytz.utc
            mst_zone = pytz.timezone("US/Arizona")
            utc_dt = utc_zone.localize(utc_dt)
            mst_dt = utc_dt.astimezone(mst_zone)
            weather_path['time'] = mst_dt.strftime("%m/%d/%Y %I:%M %p")
            json.dump(weather_path, file)
    except Exception as e:
        contents=f"Subject: Weather application API failure\n\nThe website failed to call the API.  Error is {e}"
        send_email(contents=contents, sender_email=os.getenv('ADMIN_EMAIL'))      

schedule.every().hour.do(api_execute)

def run_background():
    while running:
        try:
            schedule.run_pending()
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
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
            time = weather['time']
            weather_path=weather['values']
            return render_template('temperature.html', 
                                   data=weather_path,
                                   time = time,
                                   success=True)
    except:
        return render_template('temperature.html', success=False)    

@app.route('/precipitation')
def precip():
    try:
        with open("weather_data.json", "r") as file:
            weather = json.load(file)
            time = weather['time']
            weather_path=weather['values']
            return render_template('precipitation.html', 
                                   data=weather_path, 
                                   success=True, 
                                   time = time,
                                   api_key = os.getenv('API_KEY'))
    except:
        return render_template('precipitation.html', success=False)
    
@app.route('/weather-station')
def weather_station():
    with open("station_data.json", "r") as file:
        file_data = json.load(file)
        timestamp_formatted = datetime.strptime(file_data['timestamp'].split(".")[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %I:%M %p')
        temperature_c = file_data['temperature']
        data = {
            'temperature_c': file_data['temperature'],
            'temperature_f': round(temperature_c * (9/5) + 32, 1),
            'humidity': file_data['humidity'],
            'pressure': file_data['pressure'],
            'timestamp': timestamp_formatted
        }
    with open("station_2_data.json", "r") as file:
        file_data = json.load(file)
        timestamp_formatted = datetime.strptime(file_data['timestamp'].split(".")[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %I:%M %p')
        temperature_c = file_data['temperature']
        data_2 = {
            'temperature_c': file_data['temperature'],
            'temperature_f': round(temperature_c * (9/5) + 32, 1),
            'humidity': file_data['humidity'],
            'pressure': file_data['pressure'],
            'timestamp': timestamp_formatted
        }
    return render_template("saratoga_data.html", data=data, data_2=data_2)

@app.route("/data_graphs")
def graphs():
    return render_template("graph.html")

@app.route('/process_dates', methods=['POST'])
@csrf.exempt
def process_dates():
    try:
        temperature_units = None
        data = request.get_json()
        start_date = datetime.strptime(data.get('start_date'), '%m/%d/%Y').strftime('%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%m/%d/%Y').strftime('%Y-%m-%d')
        station_id = int(data.get('station_id'))
        data_type = str(data.get('data_type'))
        if data_type == 'temperature':
            temperature_units = data.get('units')
        else:
            pass
        create_graph(start_date=start_date, end_date=end_date, data_type=data_type, temp_units=temperature_units, station_id=station_id)
        return jsonify({'status': 'success', 'message': 'Dates processed successfully'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred'}), 400

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

@app.route("/weather_data/post", methods=['POST'])
@csrf.exempt
def data():
    token = request.headers.get('Authorization')
    try:
        if authentication(token) == True:
            temp = round(float(request.args.get('temperature')), 1)
            pressure = round(float(request.args.get('pressure')), 2)
            humidity = round(float(request.args.get('humidity')), 1)
            timestamp = request.args.get('timestamp')
            station_id = int(request.args.get('station_id'))
            data = {'temperature': temp,
                    'pressure': pressure,
                    'humidity': humidity,
                    'timestamp': timestamp,
                    'station_id': station_id
                    }
            if station_id == 1:
                with open("station_data.json", "w") as file:
                    json.dump(data, file)
            elif station_id == 2:
                with open("station_2_data.json", "w") as file:
                    json.dump(data, file)
            else:
                pass

            try:
                db = Database()
                db.add_entry(data)
                db.disconnect()
            except Exception as e:
                print(e)
            
            return jsonify({'message': 'Data was received', 'data': data}), 200
        else:
            return jsonify({'message': 'Authentication Failed'}), 401
    except Exception as e:
        return jsonify({'message': f'API Request failed due to error {e}'}), 400

app.run(host="0.0.0.0", debug=True)

