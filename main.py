from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
import requests
from datetime import datetime, timedelta
import pytz
import pprint

# Constants
API_URL = "https://api.open-meteo.com/v1/forecast"
LATITUDE = 55.605  # Malmö latitude
LONGITUDE = 13.0038  # Malmö longitude
TIMEZONE = "Europe/Stockholm"
BACKGROUND_IMAGE = "/Users/axelmansson/Documents/CPY/pyportalweather_news.bmp"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy",
    71: "Snow: Slight",
    73: "Snow: Moderate",
    75: "Snow: Heavy",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    95: "Thunderstorm: Slight",
    96: "Thunderstorm: Moderate",
    99: "Thunderstorm: Heavy hail",
}

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Futuristic Weather App")
        self.setGeometry(100, 100, 480, 320)  # Set window size to 320x240

        # Set background image
        self.background = QLabel(self)
        pixmap = QPixmap(BACKGROUND_IMAGE)
        self.background.setPixmap(pixmap)
        self.background.setGeometry(0, 0, 480, 320)  # Match background size to window

        # Set futuristic font
        self.futuristic_font = QFont("Orbitron", 14, QFont.Bold)

        # Add labels
        self.time_label = self.add_transparent_label("", 400, 285)
        self.weather_labels = {
            "current_temp": self.add_transparent_label("", 25, 20),
            "current_feels_like": self.add_transparent_label("", 25, 74),
            "current_weather" : self.add_transparent_label("", 83, 38),
            "hi_lo_temp": self.add_transparent_label("", 105, 20),
            "sunrise_sunset": self.add_transparent_label("", 230, 20),
            "precipitation": self.add_transparent_label("", 280, 68),
        }

        self.weather_labels["current_weather"].setFont(QFont("Orbitron", 22, QFont.Bold))

        # Initialize time and weather updates
        self.current_time = datetime.now(pytz.timezone(TIMEZONE))
        self.update_clock()
        self.fetch_and_update_weather()

        # Set timers
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second

        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.fetch_and_update_weather)
        self.weather_timer.start(600000)  # Update every 10 minutes

    def add_transparent_label(self, text, x, y):
        label = QLabel(text, self)
        label.setFont(self.futuristic_font)
        label.setStyleSheet("color: white; background: transparent;")
        label.move(x, y)
        label.adjustSize()
        return label

    def update_clock(self):
        self.current_time += timedelta(seconds=1)
        self.time_label.setText(f"{self.current_time.strftime('%H:%M:%S')}")
        self.time_label.adjustSize()

    def fetch_weather_data(self):
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,apparent_temperature,is_day,weather_code",
            "hourly": "precipitation_probability",
            "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
            "timezone": TIMEZONE,
            "forecast_days": 1,
            "forecast_hours":  1,
        }
        response = requests.get(API_URL, params=params)
        print(response.url)  # Print the full URL used for the API call
        response.raise_for_status()
        return response.json()

    def update_weather(self, weather_data):
        #pprint.pprint(weather_data)  # Print the fetched data in a nicely formatted way
        current_weather = weather_data["current"]
        current_temp = current_weather["temperature_2m"]
        current_feels_like = current_weather["apparent_temperature"]
        weather_code = current_weather["weather_code"]
        weather_desc = WEATHER_CODES.get(weather_code, "Unknown")

        daily = weather_data["daily"]
        hi_temp = daily["temperature_2m_max"][0]
        lo_temp = daily["temperature_2m_min"][0]
        sunrise = daily["sunrise"][0][11:16]
        sunset = daily["sunset"][0][11:16]

        hourly = weather_data["hourly"]
        next_hour_precipitation = hourly["precipitation_probability"][0]

        self.weather_labels["current_temp"].setText(f"{current_temp} °C")
        self.weather_labels["current_weather"].setText(f"{weather_desc}")
        self.weather_labels["current_feels_like"].setText(f"{current_feels_like} °C")

        self.weather_labels["hi_lo_temp"].setText(f"{round(hi_temp)} °           {round(lo_temp)} °")
        self.weather_labels["sunrise_sunset"].setText(f"{sunrise}               {sunset}")
        self.weather_labels["precipitation"].setText(f"{next_hour_precipitation}%")

        for label in self.weather_labels.values():
            label.adjustSize()

    def fetch_and_update_weather(self):
        weather_data = self.fetch_weather_data()
        self.update_weather(weather_data)

def main():
    app = QApplication([])
    window = WeatherApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()