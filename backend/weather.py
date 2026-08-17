"""Current weather for a location, via OpenWeatherMap."""
import requests

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherError(Exception):
    """Raised when the weather API can't answer (bad key, bad coords, etc.)."""


def fetch_weather(origin: str, api_key: str) -> dict:
    """origin is a "lat,lon" string. Returns {condition, description, temp_c}."""
    lat, lon = origin.split(",")
    resp = requests.get(WEATHER_URL, params={
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
    }, timeout=10)
    if resp.status_code != 200:
        raise WeatherError(f"OpenWeatherMap API error {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    return {
        "condition": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "temp_c": data["main"]["temp"],
    }
