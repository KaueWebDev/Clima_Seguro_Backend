import requests

def search_city(query):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": 5
        }
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()  # dispara exceção se HTTP != 200
        return res.json()
    except Exception as e:
        print("Erro search_city:", e)
        return []
