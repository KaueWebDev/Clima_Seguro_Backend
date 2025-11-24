import requests

# Função responsável por pesquisar cidades usando
def search_city(query):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": 5
        }
        
        headers = {"User-Agent": "ClimaSeguroApp/1.0 (meuemail@dominio.com)"}
        
        res = requests.get(url, params=params, headers=headers, timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("Erro search_city:", e)
        return []
