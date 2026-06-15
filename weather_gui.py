import tkinter as tk
from tkinter import messagebox
import requests
import threading
from datetime import datetime

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌦️"),
    56: ("Freezing drizzle", "🌧️"),
    57: ("Freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Freezing rain", "🌧️"),
    67: ("Freezing rain", "🌧️"),
    71: ("Slight snow", "❄️"),
    73: ("Moderate snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Rain showers", "🌦️"),
    81: ("Rain showers", "🌦️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Snow showers", "🌨️"),
    86: ("Heavy snow showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with hail", "⛈️")
}


def get_condition(code):
    return WEATHER_CODES.get(code, ("Unknown", "🌡️"))


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Weather Dashboard")
        self.geometry("520x680")
        self.minsize(480, 620)
        self.configure(bg="#1e2a3a")

        self.build_ui()

    def build_ui(self):
        top_frame = tk.Frame(self, bg="#1e2a3a")
        top_frame.pack(fill="x", padx=20, pady=15)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            top_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 13),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self.search_location())
        self.search_entry.insert(0, "Enter city name")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)

        search_btn = tk.Button(
            top_frame,
            text="Search",
            command=self.search_location,
            bg="#3498db",
            fg="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=12
        )
        search_btn.pack(side="left")

        self.status_label = tk.Label(
            self,
            text="Search for a city to get started",
            font=("Segoe UI", 10),
            bg="#1e2a3a",
            fg="#95a5a6"
        )
        self.status_label.pack(pady=(0, 5))

        self.main_card = tk.Frame(self, bg="#2c3e50")
        self.main_card.pack(fill="x", padx=20, pady=10)

        self.city_label = tk.Label(
            self.main_card,
            text="--",
            font=("Segoe UI", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        self.city_label.pack(pady=(15, 0))

        self.icon_label = tk.Label(
            self.main_card,
            text="",
            font=("Segoe UI", 48),
            bg="#2c3e50",
            fg="white"
        )
        self.icon_label.pack()

        self.temp_label = tk.Label(
            self.main_card,
            text="--°C",
            font=("Segoe UI", 36, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        self.temp_label.pack()

        self.desc_label = tk.Label(
            self.main_card,
            text="",
            font=("Segoe UI", 13),
            bg="#2c3e50",
            fg="#bdc3c7"
        )
        self.desc_label.pack(pady=(0, 15))

        details_frame = tk.Frame(self.main_card, bg="#2c3e50")
        details_frame.pack(pady=(0, 15), fill="x")

        self.humidity_label = self.make_detail(details_frame, "Humidity", "--%", 0)
        self.wind_label = self.make_detail(details_frame, "Wind", "-- km/h", 1)
        self.pressure_label = self.make_detail(details_frame, "Pressure", "-- hPa", 2)
        self.feels_label = self.make_detail(details_frame, "Feels Like", "--°C", 3)

        forecast_title = tk.Label(
            self,
            text="Hourly Forecast",
            font=("Segoe UI", 12, "bold"),
            bg="#1e2a3a",
            fg="white",
            anchor="w"
        )
        forecast_title.pack(fill="x", padx=20, pady=(10, 5))

        self.hourly_frame = tk.Frame(self, bg="#1e2a3a")
        self.hourly_frame.pack(fill="x", padx=20)

        daily_title = tk.Label(
            self,
            text="7-Day Forecast",
            font=("Segoe UI", 12, "bold"),
            bg="#1e2a3a",
            fg="white",
            anchor="w"
        )
        daily_title.pack(fill="x", padx=20, pady=(15, 5))

        self.daily_frame = tk.Frame(self, bg="#1e2a3a")
        self.daily_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def make_detail(self, parent, title, value, col):
        frame = tk.Frame(parent, bg="#2c3e50")
        frame.grid(row=0, column=col, padx=10, sticky="n")

        title_label = tk.Label(frame, text=title, font=("Segoe UI", 9), bg="#2c3e50", fg="#95a5a6")
        title_label.pack()

        value_label = tk.Label(frame, text=value, font=("Segoe UI", 11, "bold"), bg="#2c3e50", fg="white")
        value_label.pack()

        parent.grid_columnconfigure(col, weight=1)
        return value_label

    def clear_placeholder(self, event):
        if self.search_entry.get() == "Enter city name":
            self.search_entry.delete(0, "end")

    def search_location(self):
        city = self.search_var.get().strip()
        if not city or city == "Enter city name":
            messagebox.showwarning("Input needed", "Please type a city name first.")
            return

        self.status_label.config(text="Loading...")
        thread = threading.Thread(target=self.fetch_weather, args=(city,))
        thread.start()

    def fetch_weather(self, city):
        try:
            geo_params = {"name": city, "count": 1}
            geo_resp = requests.get(GEO_URL, params=geo_params, timeout=10)
            geo_data = geo_resp.json()

            results = geo_data.get("results")
            if not results:
                self.after(0, lambda: self.status_label.config(text="City not found."))
                return

            place = results[0]
            lat = place["latitude"]
            lon = place["longitude"]
            display_name = f"{place['name']}, {place.get('country', '')}"

            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code,pressure_msl",
                "hourly": "temperature_2m,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "timezone": "auto"
            }
            weather_resp = requests.get(WEATHER_URL, params=weather_params, timeout=10)
            weather_data = weather_resp.json()

            self.after(0, lambda: self.update_ui(display_name, weather_data))

        except requests.exceptions.RequestException:
            self.after(0, lambda: self.status_label.config(text="Network error. Check your connection."))
        except Exception:
            self.after(0, lambda: self.status_label.config(text="Something went wrong fetching the data."))

    def update_ui(self, display_name, weather_data):
        self.status_label.config(text="")

        self.city_label.config(text=display_name)

        current = weather_data["current"]
        temp = round(current["temperature_2m"])
        feels_like = round(current["apparent_temperature"])
        humidity = current["relative_humidity_2m"]
        pressure = round(current["pressure_msl"])
        wind_speed = current["wind_speed_10m"]
        code = current["weather_code"]

        condition, icon = get_condition(code)

        self.icon_label.config(text=icon)
        self.temp_label.config(text=f"{temp}°C")
        self.desc_label.config(text=condition)

        self.humidity_label.config(text=f"{humidity}%")
        self.wind_label.config(text=f"{wind_speed} km/h")
        self.pressure_label.config(text=f"{pressure} hPa")
        self.feels_label.config(text=f"{feels_like}°C")

        self.populate_hourly(weather_data)
        self.populate_daily(weather_data)

    def populate_hourly(self, weather_data):
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        hourly = weather_data.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        codes = hourly.get("weather_code", [])

        now_str = weather_data["current"]["time"]
        start_index = 0
        for i, t in enumerate(times):
            if t >= now_str:
                start_index = i
                break

        for i in range(start_index, min(start_index + 6, len(times))):
            time_str = times[i]
            hour = datetime.fromisoformat(time_str).strftime("%H:%M")
            temp = round(temps[i])
            _, icon = get_condition(codes[i])

            card = tk.Frame(self.hourly_frame, bg="#2c3e50")
            card.pack(side="left", expand=True, fill="x", padx=4, pady=4)

            tk.Label(card, text=hour, font=("Segoe UI", 9), bg="#2c3e50", fg="#95a5a6").pack(pady=(8, 2))
            tk.Label(card, text=icon, font=("Segoe UI", 18), bg="#2c3e50", fg="white").pack()
            tk.Label(card, text=f"{temp}°", font=("Segoe UI", 11, "bold"), bg="#2c3e50", fg="white").pack(pady=(2, 8))

    def populate_daily(self, weather_data):
        for widget in self.daily_frame.winfo_children():
            widget.destroy()

        daily = weather_data.get("daily", {})
        dates = daily.get("time", [])
        codes = daily.get("weather_code", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])

        for i in range(len(dates)):
            date_obj = datetime.fromisoformat(dates[i])
            day_name = date_obj.strftime("%a %d %b")
            condition, icon = get_condition(codes[i])
            max_temp = round(max_temps[i])
            min_temp = round(min_temps[i])

            row = tk.Frame(self.daily_frame, bg="#2c3e50")
            row.pack(fill="x", pady=3)

            tk.Label(row, text=day_name, font=("Segoe UI", 10), bg="#2c3e50", fg="#bdc3c7", width=12, anchor="w").pack(side="left", padx=10, pady=8)
            tk.Label(row, text=icon, font=("Segoe UI", 16), bg="#2c3e50", fg="white").pack(side="left", padx=10)
            tk.Label(row, text=condition, font=("Segoe UI", 10), bg="#2c3e50", fg="#bdc3c7", anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(row, text=f"{max_temp}° / {min_temp}°", font=("Segoe UI", 11, "bold"), bg="#2c3e50", fg="white").pack(side="right", padx=10)


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
