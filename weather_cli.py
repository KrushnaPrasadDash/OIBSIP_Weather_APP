import requests
import sys

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def get_coordinates(city):
    params = {"name": city, "count": 1}

    response = requests.get(GEO_URL, params=params, timeout=10)
    data = response.json()

    results = data.get("results")
    if not results:
        return None

    place = results[0]
    return {
        "name": place["name"],
        "country": place.get("country", ""),
        "lat": place["latitude"],
        "lon": place["longitude"]
    }


def get_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code,pressure_msl",
        "timezone": "auto"
    }

    response = requests.get(WEATHER_URL, params=params, timeout=10)
    return response.json()


def display_weather(location, weather_data):
    current = weather_data["current"]

    temp = current["temperature_2m"]
    feels_like = current["apparent_temperature"]
    humidity = current["relative_humidity_2m"]
    wind_speed = current["wind_speed_10m"]
    pressure = current["pressure_msl"]
    code = current["weather_code"]

    condition = WEATHER_CODES.get(code, "Unknown")

    print("-" * 40)
    print(f"Weather Report for {location['name']}, {location['country']}")
    print("-" * 40)
    print(f"Condition    : {condition}")
    print(f"Temperature  : {temp} C")
    print(f"Feels Like   : {feels_like} C")
    print(f"Humidity     : {humidity}%")
    print(f"Pressure     : {pressure} hPa")
    print(f"Wind Speed   : {wind_speed} km/h")
    print("-" * 40)


def main():
    print("===== Simple Weather App =====")
    print("Powered by Open-Meteo (no API key required)")
    print()

    while True:
        city = input("Enter city name (or 'exit' to quit): ").strip()

        if city.lower() == "exit":
            print("Goodbye!")
            sys.exit()

        if city == "":
            print("Please enter a valid city name.")
            continue

        try:
            location = get_coordinates(city)
        except requests.exceptions.RequestException:
            print("Could not connect to the weather service. Check your internet connection.")
            print()
            continue

        if location is None:
            print("City not found. Please check the spelling and try again.")
            print()
            continue

        try:
            weather_data = get_weather(location["lat"], location["lon"])
        except requests.exceptions.RequestException:
            print("Could not fetch weather data. Check your internet connection.")
            print()
            continue

        display_weather(location, weather_data)
        print()


if __name__ == "__main__":
    main()
