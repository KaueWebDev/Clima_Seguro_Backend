
import requests

def search_city(query, limit=5):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": limit
    }
    headers = {
        "User-Agent": "ClimaSeguro/1.0 (contact@example.com)"
    }
    res = requests.get(url, params=params, headers=headers, timeout=10)
    res.raise_for_status()
    return res.json()
