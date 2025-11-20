import requests

def search_city(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 5
    }

    headers = {
        "User-Agent": "weather-app-render/1.0 (contact: example@example.com)"
    }

    response = requests.get(url, params=params, headers=headers)

    return response.json()
