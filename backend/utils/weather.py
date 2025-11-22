import requests

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }

    res = requests.get(url, params=params)
    data = res.json()

    w = data.get("current_weather", {})

    return {
        "temperature": w.get("temperature", 0),
        "humidity": w.get("relativehumidity", 0),
        "wind": w.get("windspeed", 0)
    }
