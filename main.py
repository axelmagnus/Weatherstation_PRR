from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
import requests
from datetime import datetime, timedelta
import pytz
import pprint
import json

# Add your Guardian API key here
GUARDIAN_API_URL = "https://content.guardianapis.com/search"
GUARDIAN_API_KEY = "7ddc8b05-83cc-4ab0-a05c-5358208f0c31"

# Adafruit IO credentials
ADAFRUIT_IO_USERNAME = "axelmagnus"
ADAFRUIT_IO_KEY = "1a20315d078d4304bee799ce4b2af0e7"
ADAFRUIT_IO_URL = "https://io.adafruit.com/api/v2"



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

        # Initialize cycle counter
        self.cycle_count = 0

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

        # Add a status label
        self.status_label = self.add_transparent_label("", 25, 293)
        self.status_label.setStyleSheet("color: black; background: transparent;")

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

        # Add a label for news
        self.news_label = self.add_transparent_label("", 25, 230)
        # Add a label for the section name and publication time
        self.news_meta_label = self.add_transparent_label("", 120, 210)

        # Initialize news data and index
        self.news_items = []
        self.current_news_index = 0

        # Set a timer to cycle through news items
        self.news_timer = QTimer(self)
        self.news_timer.timeout.connect(self.cycle_news)
        self.news_timer.start(5000)  # Change news every 5 seconds

        # Fetch and update news
        self.fetch_and_update_news()

        # Add labels for Adafruit IO data
        self.adafruit_labels = {
            "temp": self.add_transparent_label("", 25, 110),
            "voltage": self.add_transparent_label("", 110, 143),
            "percent": self.add_transparent_label("", 110, 165),
            "current": self.add_transparent_label("", 279, 143),
            "hum": self.add_transparent_label("", 279, 165),
        }

        self.adafruit_labels["temp"].setFont(QFont("Orbitron", 22, QFont.Bold))

        # Timer to fetch Adafruit IO data every 10 minutes
        self.adafruit_timer = QTimer(self)
        self.adafruit_timer.timeout.connect(self.fetch_and_update_adafruit_data)
        self.adafruit_timer.start(600000)  # 10 minutes

        # Fetch initial data
        self.fetch_and_update_adafruit_data()


    def fetch_adafruit_data(self, feed_key):
        url = f"{ADAFRUIT_IO_URL}/{ADAFRUIT_IO_USERNAME}/feeds/{feed_key}/data/last"
        headers = {"X-AIO-Key": ADAFRUIT_IO_KEY}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.status_label.setText(f"AIO feeds updated {datetime.now(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S')}.")

        return response.json()["value"]

    def fetch_and_update_adafruit_data(self):
        try:
            # Fetch data for each feed
            temp = self.fetch_adafruit_data("esp32s2.temp")
            voltage = self.fetch_adafruit_data("esp32s2.voltage")
            percent = self.fetch_adafruit_data("esp32s2.percent")
            current= self.fetch_adafruit_data("esp32s2.current")
            hum = self.fetch_adafruit_data("esp32s2.hum")

            # Update labels
            self.adafruit_labels["temp"].setText(f"{float(temp):.1f} °C")
            self.adafruit_labels["voltage"].setText(f"{float(voltage):.2f} V")
            self.adafruit_labels["percent"].setText(f"{float(percent):.1f} %")
            self.adafruit_labels["current"].setText(f"{float(current):.0f} mA")
            self.adafruit_labels["hum"].setText(f"{float(hum):.0f} %")

            for label in self.adafruit_labels.values():
                label.adjustSize()
        except Exception as e:
            print(f"Error fetching Adafruit IO data: {e}")


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
        # Update the status label with a timestamp
        self.status_label.setText(f"Weather data updated {datetime.now(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S')}.")
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

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                current_line += (word + " ")
            else:
                lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return "\n".join(lines)

    def update_news(self, news_data):
        # Extract the first 3 news items with metadata
        self.news_items = [
            {
                "headline": self.wrap_text(result["webTitle"], 45),
                "section": result["sectionName"],
                "time": (datetime.strptime(result["webPublicationDate"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=1)).strftime("%H:%M"),  }
            for result in news_data["response"]["results"][:10]
        ]
        self.cycle_news()

    def cycle_news(self):
        if self.news_items:
            current_item = self.news_items[self.current_news_index]
            self.news_label.setText(current_item["headline"])
            self.news_meta_label.setText(
                f" {current_item['time']}     {current_item['section']}    {self.current_news_index + 1}/{len(self.news_items)}"
            )
            self.news_label.adjustSize()
            self.news_meta_label.adjustSize()

            # Calculate display time based on word count (10 words per second)
            word_count = len(current_item["headline"].split())
            display_time = max(4000, (word_count / 10) * 3000+1500)  # Minimum 3 seconds

            # Restart the timer with the calculated display time
            self.news_timer.start(int(display_time))

            # Update index and cycle count
            self.current_news_index = (self.current_news_index + 1) % len(self.news_items)
            if self.current_news_index == 0:
                self.cycle_count += 1

            # Fetch new news data after 4 full cycles
            if self.cycle_count >= 4:
                self.cycle_count = 0
                self.fetch_and_update_news()
    def fetch_news_data(self):
        params = {
            "api-key": GUARDIAN_API_KEY,
            "page-size": 10,  # Fetch only the first 3 news items
            "order-by": "newest",
            "sections": "business,news,politics,science,technology,us-news,world",  # Filter by sectionIds

        }
        response = requests.get(GUARDIAN_API_URL, params=params)
        print(response.url)
        response.raise_for_status()
        self.status_label.setText(f"News updated {datetime.now(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S')}.")

        return response.json()

    def fetch_and_update_news(self):
        news_data = self.fetch_news_data()
        self.update_news(news_data)

def main():
    app = QApplication([])
    window = WeatherApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()