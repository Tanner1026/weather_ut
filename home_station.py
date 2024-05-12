import bme280
import smbus2
import time
import requests
import pytz

auth_token= "Auth Token Here"
# I only created an Auth Token for myself so that I can't get random data entries from other people
post_url = "Website Post URL"
#Method of adding data to the weather-station endpoint so that I can update the data real-time
headers = {
           "Authorization": auth_token,
    }
running = True
#Initialize the BME280 sensor
#NOTE you must have I2C configured for the rapsberry pi to be able to detect the sensor
#Default address for I2C will by 0x76 but you can find the address by using terminal and running "ls /dev/i2c*" and then finding the I2C address and then running "sudo i2cdetect -y X" (replace X with number found using previous command
address = 0x76
bus = smbus2.SMBus(1)
calibration_params = bme280.load_calibration_params(bus, address)

while running == True:
    try:
        #calibrate bme280 sensor
        data = bme280.sample(bus, address, calibration_params)
        #access data points
        temp = data.temperature
        humidity = data.humidity
        #configure timezone for mountain time
        timestamp = data.timestamp
        desired_timezone = pytz.timezone('America/Denver')
        timestamp_tz = timestamp.replace(tzinfo=pytz.utc).astimezone(desired_timezone)
        pressure = data.pressure
        params = {
            "temperature": temp,
            "pressure": pressure,
            "humidity": humidity,
            "timestamp": timestamp_tz
            }
        response = requests.request("POST", post_url, params=params, headers=headers)
        print(response.text)
    except:
        pass
    time.sleep(300)

