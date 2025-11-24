import requests

# Mapeamento dos códigos do Open-Meteo para descrição
weather_map = {
    0: "Céu limpo",
    1: "Parcialmente nublado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina com gelo",
    51: "Chuva leve",
    53: "Chuva moderada",
    55: "Chuva intensa",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva forte",
    71: "Neve leve",
    73: "Neve moderada",
    75: "Neve forte",
    80: "Chuva de pancadas",
    81: "Chuva de pancadas forte",
    82: "Chuva de pancadas muito forte",
    95: "Trovoada",
    96: "Trovoada com granizo leve",
    99: "Trovoada com granizo forte"
}

# Função que consulta dados de clima atual no Open-Meteo
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "relative_humidity_2m",
        "timezone": "auto"
    }

     # Envia a requisição HTTP usando GET
    res = requests.get(url, params=params)
    data = res.json()  # Converte JSON da resposta em dict Python

    # Obtém dados do clima atual
    current = data.get("current_weather", {})
    if not current:
        return {
            "temperature": 0,
            "humidity": 0,
            "wind": 0,
            "description": "Condição desconhecida"
        }

    # Umidade atual (hora mais próxima)
    humidity_list = data.get("hourly", {}).get("relative_humidity_2m", [])
    humidity = humidity_list[0] if humidity_list else 0

    # Converte weathercode em descrição
    weather_code = current.get("weathercode", 0)
    description = weather_map.get(weather_code, "Condição atual")

    # Retorna dados organizados para o frontend
    return {
        "temperature": current.get("temperature", 0),
        "humidity": humidity,
        "wind": current.get("windspeed", 0),
        "description": description
    }
