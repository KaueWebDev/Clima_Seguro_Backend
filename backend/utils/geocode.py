
import requests

def search_city(query, limit=6):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": query,
        "count": limit,
        "language": "pt",
        "format": "json"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    # open-meteo returns 'results' list
    return data.get("results", [])
