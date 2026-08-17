"""Current weather for a location, via Open-Meteo (free, no API key needed)."""
import requests

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes -> human description (https://open-meteo.com/en/docs)
_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow",
    80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
    95: "thunderstorm",
}


class WeatherError(Exception):
    """Raised when the weather API can't answer (bad coords, network error, etc.)."""


def fetch_weather(origin: str) -> dict:
    """origin is a "lat,lon" string. Returns {condition, description, temp_c}."""
    lat, lon = origin.split(",")
    resp = requests.get(WEATHER_URL, params={
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
    }, timeout=10)
    if resp.status_code != 200:
        raise WeatherError(f"Open-Meteo API error {resp.status_code}: {resp.text[:200]}")
    current = resp.json()["current"]
    code = current["weather_code"]
    description = _CODES.get(code, f"code {code}")
    return {
        "condition": description,
        "description": description,
        "temp_c": current["temperature_2m"],
    }
