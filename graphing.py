import pandas as pd
import matplotlib.pyplot as plt

class Grapher:
    def __init__(self):
        pass
    def create_graphs(self, data, data_type, temp_units):
        df = pd.DataFrame(data, columns=[data_type, 'timestamp'])
        df[data_type] = df[data_type].astype(float)
        if data_type == 'temperature' and temp_units == 'fahrenheit':
            print('yes')
            df[data_type] = df[data_type].apply(lambda x: x * (9/5) + 32) 
        else:
            pass
        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df[data_type])
        plt.title(f'{data_type.capitalize()} Over Selected Date(s)')
        y_axis_label = ''
        if data_type == 'temperature' and temp_units == 'celsius':
            y_axis_label = 'Temperature (°C)'
        elif data_type == 'temperature' and temp_units == 'fahrenheit':
            y_axis_label == 'Temperature (°F)'
        elif data_type == 'humidity':
            y_axis_label = 'Humidity in %'
        else:
            y_axis_label = 'Pressure in hPa'
        plt.xlabel('Timestamp')
        plt.ylabel(y_axis_label)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('static/img/data_graph/graph.png')
