
import requests


def get_coordinates(city):
    """Convert city name into latitude and longitude."""

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    location = data["results"][0]

    return {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "name": location["name"],
        "country": location.get("country", "")
    }


def get_air_quality(latitude, longitude):
    """Fetch current air-quality measurements."""

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "pm10",
            "pm2_5",
            "carbon_monoxide",
            "nitrogen_dioxide",
            "ozone",
            "us_aqi"
        ],
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    return data.get("current")
