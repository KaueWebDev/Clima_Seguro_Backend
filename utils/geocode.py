import requests

def search_city(query):
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=5&addressdetails=1"
    response = requests.get(url, headers={"User-Agent": "ClimaSeguro-App"})
    return response.json()
