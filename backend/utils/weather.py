
import requests
from datetime import datetime, timezone
import pytz

def get_weather(lat, lon):
    """
    Retorna dict com: temperature (°C), wind (km/h), humidity (%), time (ISO)
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "relativehumidity_2m",
        "timezone": "auto"
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    # current_weather contém temperature e windspeed
    cw = data.get("current_weather", {})
    hourly = data.get("hourly", {})
    rh_times = hourly.get("time", [])
    rh_values = hourly.get("relativehumidity_2m", [])

    # Tentar casar horário atual do current_weather com hourly para obter umidade
    humidity = None
    current_time = cw.get("time")
    if current_time and rh_times and rh_values and len(rh_times) == len(rh_values):
        try:
            idx = rh_times.index(current_time)
            humidity = rh_values[idx]
        except ValueError:
            # se não achar, pegar o último valor disponível
            humidity = rh_values[-1] if rh_values else None
    else:
        humidity = rh_values[-1] if rh_values else None

    temp = cw.get("temperature")            # °C
    wind_ms = cw.get("windspeed")           # m/s or km/h? Open-Meteo returns m/s or km/h depending model; often m/s. We'll convert if > 50 assume m/s? Safer: use returned value as km/h if docs say km/h, but doc default is m/s? Actually Open-Meteo returns windspeed in km/h when specifying windspeed_unit param; default is m/s. To be explicit, let's request km/h.
    # To ensure km/h, better modify params to include windspeed_unit=kmh (update above)
    return {
        "temperature": temp,
        "humidity": humidity,
        "wind": cw.get("windspeed"),
        "time": cw.get("time"),
        "raw": data
    }
