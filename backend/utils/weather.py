import requests

def get_weather(lat, lon):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        w = res.json().get("current_weather", {})
        return {
            "temperature": w.get("temperature", 0),
            "wind": w.get("windspeed", 0),
            "humidity": 0  # Open-Meteo não retorna umidade em current_weather
        }
    except Exception as e:
        print("Erro get_weather:", e)
        return {"temperature": 0, "wind": 0, "humidity": 0}
