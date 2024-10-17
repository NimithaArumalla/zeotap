import requests
import mysql.connector
import time
import datetime
import matplotlib.pyplot as plt

# Configuration
API_KEY = '9b85c724cb1cbbf2b634a49fdcf76b3c'
CITY_IDS = {
    'Delhi': '1273294',
    'Mumbai': '1275339',
    'Chennai': '1264527',
    'Bangalore': '1277333',
    'Kolkata': '1275004',
    'Hyderabad': '1269843'
}
ALERT_THRESHOLD = 25  # Example threshold

# Helper functions
def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def get_weather(city_id):
    url = f'http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}'
    response = requests.get(url)
    return response.json()

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Nimitha@1419.',
    database='zeotap'
)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(255),
    main VARCHAR(50),
    temp FLOAT,
    feels_like FLOAT,
    timestamp INT
)''')
conn.commit()

def store_weather_data(city, data):
    main = data['weather'][0]['main'] if 'weather' in data and 'main' in data['weather'][0] else 'Unknown'
    temp = kelvin_to_celsius(data['main']['temp']) if 'main' in data and 'temp' in data['main'] else None
    feels_like = kelvin_to_celsius(data['main']['feels_like']) if 'main' in data and 'feels_like' in data['main'] else None
    timestamp = data['dt'] if 'dt' in data else None

    if temp is not None and feels_like is not None and timestamp is not None:
        cursor.execute('''INSERT INTO weather (city, main, temp, feels_like, timestamp)
                          VALUES (%s, %s, %s, %s, %s)''', (city, main, temp, feels_like, timestamp))
        conn.commit()
        print(f"Stored data for city: {city}")
    else:
        print(f"Missing necessary data for city: {city}")

def calculate_daily_summary():
    cursor.execute('SELECT city, temp, main, timestamp FROM weather')
    data = cursor.fetchall()
    
    summary = {}
    for city, temp, main, timestamp in data:
        if main is None:
            main = 'Unknown'  # Provide a fallback if 'main' is missing


    for city, temp, main, timestamp in data:
        date = datetime.datetime.fromtimestamp(timestamp).date()
        if (city, date) not in summary:
            summary[(city, date)] = {'temps': [], 'main': {}}
        
        summary[(city, date)]['temps'].append(temp)
        if main not in summary[(city, date)]['main']:
            summary[(city, date)]['main'][main] = 0
        summary[(city, date)]['main'][main] += 1

    for key, value in summary.items():
        city, date = key
        temps = value['temps']
        main_counts = value['main']
        dominant_main = max(main_counts, key=main_counts.get)

        print(f"Date: {date}, City: {city}, Average Temp: {sum(temps)/len(temps):.2f}, "
              f"Max Temp: {max(temps):.2f}, Min Temp: {min(temps):.2f}, Dominant Condition: {dominant_main}")

def check_alerts():
    cursor.execute('SELECT city, temp, timestamp FROM weather ORDER BY timestamp DESC LIMIT 2')
    data = cursor.fetchall()
    
    if len(data) == 2:
        first_record, second_record = data
        _, first_temp,_ = first_record
        _, second_temp,_ = second_record

        if first_temp > ALERT_THRESHOLD and second_temp > ALERT_THRESHOLD:
            city = data[0][0]
            print(f"Alert! Temperature in {city} exceeded {ALERT_THRESHOLD}C for two consecutive updates")
    
def visualize_daily_summary():
    cursor.execute('SELECT city, temp,main, timestamp FROM weather')
    data = cursor.fetchall()
    
    summary = {}
    for city,temp,main, timestamp in data:
        date = datetime.datetime.fromtimestamp(timestamp).date()
        if (city, date) not in summary:
            summary[(city, date)] = {'temps': [], 'main': {}}
        
        summary[(city, date)]['temps'].append(temp)
        if main not in summary[(city, date)]['main']:
            summary[(city, date)]['main'][main] = 0
        summary[(city, date)]['main'][main] += 1

    dates = []
    avg_temps = []

    for key, value in summary.items():
        city, date = key
        temps = value['temps']
        avg_temp = sum(temps) / len(temps)
        
        dates.append(date)
        avg_temps.append(avg_temp)

    plt.plot(dates, avg_temps, 'bo-')
    plt.xlabel('Date')
    plt.ylabel('Average Temperature (C)')
    plt.title('Daily Weather Summary')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

while True:
    for city, city_id in CITY_IDS.items():
        weather_data = get_weather(city_id)
        store_weather_data(city, weather_data)
    
    calculate_daily_summary()
    check_alerts()
    visualize_daily_summary()

    time.sleep(300)  # Sleep for 5 minutes
