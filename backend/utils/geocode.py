import requests

def search_city(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5
    }
    res = requests.get(url, params=params)
    return res.json()
