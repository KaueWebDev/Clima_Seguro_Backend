# utils/weather.py
import requests
from datetime import datetime, timezone, timedelta

# Mapeamento simples de weathercode (Open-Meteo) para descrição e ícone genérico
WEATHERCODE_MAP = {
    0: ("Clear sky", "01d"),
    1: ("Mainly clear", "02d"),
    2: ("Partly cloudy", "03d"),
    3: ("Overcast", "04d"),
    45: ("Fog", "50d"),
    48: ("Depositing rime fog", "50d"),
    51: ("Light drizzle", "09d"),
    53: ("Moderate drizzle", "09d"),
    55: ("Dense drizzle", "09d"),
    56: ("Light freezing drizzle", "09d"),
    57: ("Dense freezing drizzle", "09d"),
    61: ("Slight rain", "10d"),
    63: ("Moderate rain", "10d"),
    65: ("Heavy rain", "10d"),
    66: ("Light freezing rain", "10d"),
    67: ("Heavy freezing rain", "10d"),
    71: ("Slight snow fall", "13d"),
    73: ("Moderate snow fall", "13d"),
    75: ("Heavy snow fall", "13d"),
    80: ("Rain showers", "09d"),
    81: ("Moderate rain showers", "09d"),
    82: ("Violent rain showers", "09d"),
    95: ("Thunderstorm", "11d"),
    96: ("Thunderstorm with slight hail", "11d"),
    99: ("Thunderstorm with heavy hail", "11d"),
}

def _map_weathercode(code):
    return WEATHERCODE_MAP.get(code, ("Unknown", "01d"))

def _nearest_hour_index(times, target_iso):
    # times: list of ISO strings
    # target_iso: ISO string (e.g., "2023-11-01T12:34")
    # retorna índice do horário mais próximo
    # convertendo para datetime para comparar
    from datetime import datetime
    fmt = "%Y-%m-%dT%H:%M"
    try:
        target = datetime.fromisoformat(target_iso[:16])
    except Exception:
        target = datetime.utcnow()
    best_idx = 0
    best_diff = None
    for i, t in enumerate(times):
        try:
            dt = datetime.fromisoformat(t[:16])
        except Exception:
            continue
        diff = abs((dt - target).total_seconds())
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_idx = i
    return best_idx

def get_weather(lat, lon, timezone_param="auto"):
    """
    Consulta Open-Meteo e retorna um dict com campos compatíveis com o app.
    - lat, lon: strings ou floats
    - timezone_param: "auto" ou fuso horário (ex: "Europe/London")
    """
    base = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        # pedimos hourly relative humidity para pegar o valor mais próximo do horário atual
        "hourly": "relativehumidity_2m,weathercode",
        "timezone": timezone_param
    }

    resp = requests.get(base, params=params, timeout=10)
    resp.raise_for_status()
    j = resp.json()

    # current_weather existe com temp e windspeed e weathercode
    cw = j.get("current_weather", {})
    temp = cw.get("temperature")                # Celsius
    wind = cw.get("windspeed")                  # km/h
    weathercode = cw.get("weathercode", 0)
    time_now = cw.get("time")                   # ISO string

    # pegar umidade do hourly mais próximo
    humidity = None
    hourly = j.get("hourly", {})
    times = hourly.get("time", [])
    humidities = hourly.get("relativehumidity_2m", [])
    if times and humidities:
        idx = _nearest_hour_index(times, time_now or "")
        try:
            humidity = humidities[idx]
        except Exception:
            humidity = None

    description, icon = _map_weathercode(weathercode)

    # Montamos uma estrutura simples compatível com o que o app espera (adaptável)
    return {
        "name": None,  # nome da cidade se o frontend enviar; mantemos None aqui
        "sys": {
            "country": None
        },
        "weather": [
            {
                "id": weathercode,
                "main": description,
                "description": description,
                "icon": icon
            }
        ],
        "main": {
            "temp": temp,
            "humidity": humidity
        },
        "wind": {
            "speed": wind
        },
        "raw_open_meteo": j
    }
