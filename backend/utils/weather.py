
import requests

def get_weather(lat, lon):
    """
    Retorna dict com temperatura (°C), umidade (%) e vento (m/s ou km/h dependendo do endpoint).
    Usamos current_weather + hourly (relativehumidity_2m) para obter a umidade atual.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "relativehumidity_2m",
        "timezone": "auto"
    }

    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    data = res.json()

    # current weather
    cw = data.get("current_weather", {})
    temp = cw.get("temperature")  # °C
    wind = cw.get("windspeed")    # km/h by default on some responses

    # humidity: buscar no hourly pelo timestamp igual ao current_weather.time
    humidity = None
    hour = data.get("hourly", {})
    times = hour.get("time", [])
    humidities = hour.get("relativehumidity_2m", [])

    ct_time = cw.get("time")
    if ct_time and times and humidities:
        try:
            idx = times.index(ct_time)
            humidity = humidities[idx]
        except ValueError:
            # se não achou index, pega último valor disponível
            if humidities:
                humidity = humidities[-1]
    else:
        humidity = None

    return {
        "temperature": temp,
        "humidity": humidity,
        "wind": wind
    }
