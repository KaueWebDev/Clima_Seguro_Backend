import requests
from config import OPENWEATHER_API_KEY

def get_weather(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}&lang=pt_br"
    )
    response = requests.get(url)
    return response.json()
