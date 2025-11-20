import requests

def search_city(query):
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=5"
    response = requests.get(url)
    return response.json()
