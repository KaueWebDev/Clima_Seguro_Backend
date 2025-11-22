import requests

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }

    res = requests.get(url, params=params)
    w = res.json()["current"]

    return {
        "temperature": w["temperature_2m"],
        "humidity": w["relative_humidity_2m"],
        "wind": w["wind_speed_10m"],
    }
