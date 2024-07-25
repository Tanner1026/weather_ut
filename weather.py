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
URL_CURRENT_WEATHER = f"https://api.tomorrow.io/v4/weather/realtime?location=salt%20lake%20city&apikey={os.getenv('API_KEY')}"
URL_MAPS = 'https://api.tomorrow.io/v4/map/tile/'
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
header_map = {'accept': 'text/plain'}
precip_params = ['cloudBase', 'cloudCeiling', 'visibility', 'precipitationIntensity', 'humidity', 'pressureSurfaceLevel']
today = date.today()

running=True

def authentication(token):
    return str(token) == AUTH_TOKEN

def send_email(contents, sender_email): 
    with smtplib.SMTP('smtp.gmail.com', port=587) as connection:
        connection.starttls()
        connection.login(os.getenv('ADMIN_EMAIL'), os.getenv('APP_PASSWORD'))
        connection.sendmail(from_addr=sender_email, to_addrs=os.getenv('ADMIN_EMAIL'), msg=contents)

def create_graph(start_date, end_date, data_type):
    
    db = Database()
    print(data_type)
    results = db.graphical_results(start_date=start_date, end_date=end_date, data_type=data_type)
    print(results[0][1])
    grapher = Grapher()
    grapher.create_graphs(data=results, data_type=data_type)

def api_execute():
    try:
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
    
        current_weather = requests.get(URL_CURRENT_WEATHER).json()
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
    except:
        contents=f"Subject: Weather application API failure\n\nThe website failed to call the API"
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
# t.start()

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
    
@app.route('/air_quality')
def air_q():
    try:
        with open("weather_data.json", "r") as file:
            weather = json.load(file)
            time = weather['time']
        success = True
        return render_template('air_quality.html', success = success, time=time)
    except:
        return render_template("air_quality.html", success= success)
    
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
    return render_template("saratoga_data.html", data=data)

@app.route("/data_graphs")
def graphs():
    return render_template("graph.html")

@app.route('/process_dates', methods=['POST'])
@csrf.exempt
def process_dates():
    try:
        data = request.get_json()
        start_date = datetime.strptime(data.get('start_date'), '%m/%d/%Y').strftime('%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%m/%d/%Y').strftime('%Y-%m-%d')
        data_type = str(data.get('data_type'))
        create_graph(start_date=start_date, end_date=end_date, data_type=data_type)
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
            data = {'temperature': temp,
                    'pressure': pressure,
                    'humidity': humidity,
                    'timestamp': timestamp}
            
            with open("station_data.json", "w") as file:
                json.dump(data, file)
            
            try:
                db = Database()
                db.add_entry(data)
                db.disconnect()
            except:
                pass
            
            return jsonify({'message': 'Data was received', 'data': data}), 200
        else:
            return jsonify({'message': 'Authentication Failed'}), 401
    except Exception as e:
        return jsonify({'message': f'API Request failed due to error {e}'}), 400

app.run(host="0.0.0.0", debug=True)

