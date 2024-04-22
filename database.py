import os
from dotenv import load_dotenv
import psycopg2
load_dotenv()

class Database():
    def __init__(self):
        self.db_host = os.getenv('IP')
        self.db_port = '5432'
        self.db_name = 'weather_data'
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                    host = self.db_host,
                    port = self.db_port,
                    dbname = self.db_name,
                    user = self.db_user,
                    password = self.db_password,
                )
                
        except psycopg2.Error as e:
            print("Error Connecting to PostgreSQL:", e)

    def add_entry(self, data):
        try:
            cursor = self.conn.cursor()
            insert_data = """
            INSERT INTO weather_data (temperature, humidity, surface_pressure, timestamp)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_data, (data['temperature'], data['humidity'], data['pressure'], data['timestamp']))
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Error: {e}")

    def get_recent(self):
        try:
            cursor = self.conn.cursor()
            query = f"SELECT * FROM weather_data ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            last_value = cursor.fetchone()
            if last_value:
                data = {
                    'temperature': last_value[1],
                    'humidity': last_value[2],
                    'pressure': last_value[3],
                    'date': last_value[4]
                }
                return data
            else:
                print("No values found in the table.")
        except psycopg2.Error as e:
            print(f"Error: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()