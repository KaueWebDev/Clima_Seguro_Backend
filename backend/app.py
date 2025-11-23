from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.geocode import search_city
from utils.weather import get_weather
from utils.flags import get_flag_url
from utils.structures import LinkedList, Queue, Stack, HashTable
import requests

app = Flask(__name__)
CORS(app)

# Estruturas
fila = Queue()
pilha = Stack()
lista = LinkedList()
cache = HashTable()


# Mapeamento estado completo -> sigla (PT-BR)
_STATES_PT_BR = {
    "acre": "AC", "alagoas": "AL", "amapá": "AP", "amapa": "AP", "amazonas": "AM",
    "bahia": "BA", "ceará": "CE", "ceara": "CE", "distrito federal": "DF",
    "espírito santo": "ES", "espirito santo": "ES", "goiás": "GO", "goias": "GO",
    "maranhão": "MA", "maranhao": "MA", "mato grosso": "MT", "mato grosso do sul": "MS",
    "minas gerais": "MG", "pará": "PA", "para": "PA", "paraíba": "PB", "paraiba": "PB",
    "paraná": "PR", "parana": "PR", "pernambuco": "PE", "piauí": "PI", "piaui": "PI",
    "rio de janeiro": "RJ", "rio grande do norte": "RN", "rio grande do sul": "RS",
    "rondônia": "RO", "rondonia": "RO", "roraima": "RR", "santa catarina": "SC",
    "são paulo": "SP", "sao paulo": "SP", "sergipe": "SE", "tocantins": "TO"
}


def extract_city_state_country_from_address(addr):
    """
    Recebe o objeto 'address' do Nominatim (search_city) e tenta extrair
    cidade, sigla do estado (UF) e country_code (BR, PT, US, etc).
    Retorna (city, uf_or_empty, country_code_or_empty).
    """
    if not isinstance(addr, dict):
        return ("Desconhecido", "", "")

    # Cidade pode aparecer em vários campos
    city = (addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("municipality")
            or addr.get("county")
            or addr.get("hamlet")
            or addr.get("locality")
            or addr.get("village")
            or "").strip()

    # Estado pode vir como 'state' (nome completo)
    state_full = (addr.get("state") or "").strip()
    uf = ""
    if state_full:
        uf = _STATES_PT_BR.get(state_full.lower(), "")

    # country_code (ex: 'br', 'pt', 'us')
    country_code = (addr.get("country_code") or "").strip().upper()

    return (city if city else "Desconhecido", uf, country_code)


def format_location_for_output(city, uf, country_code):
    """
    Formata a string final a ser mostrada no frontend:
    - Se uf presente e country_code presente: "Cidade — UF, CC"
    - Se uf ausente e country_code presente: "Cidade — CC"
    - Se nenhum: "Cidade"
    """
    if country_code:
        if uf:
            return f"{city} — {uf}, {country_code}"
        else:
            return f"{city} — {country_code}"
    else:
        if uf:
            return f"{city} — {uf}"
        return city


@app.route("/")
def home():
    return "API ON — Open-Meteo + Estruturas"


@app.route("/api/autocomplete")
def autocomplete():
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])

    try:
        cities = search_city(query)  # espera lista de resultados do Nominatim
        results = []
        seen = set()

        for c in cities:
            addr = c.get("address", {}) or {}
            lat = c.get("lat", "")
            lon = c.get("lon", "")

            city, uf, country_code = extract_city_state_country_from_address(addr)

            name_display = format_location_for_output(city, uf, country_code)

            # chave única para deduplicar: nome+uf+country+lat+lon (coordenadas evitam mesmona cidade em diferentes lugares)
            key = f"{city}|{uf}|{country_code}|{lat}|{lon}"
            if key in seen:
                continue
            seen.add(key)

            results.append({
                "name": name_display,
                "lat": lat,
                "lon": lon,
                "country_code": country_code
            })

        return jsonify(results)
    except Exception as e:
        # log opcional: print(e)
        return jsonify([]), 500


@app.route("/api/weather")
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    # name e country podem ser enviados pelo frontend, mas não são obrigatórios
    name = request.args.get("name", "")
    country = request.args.get("country", "")

    if not lat or not lon:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    key = f"{lat},{lon}"

    # cache simples
    cached = cache.get(key)
    if cached:
        return jsonify(cached)

    try:
        w = get_weather(lat, lon)  # espera dict com keys: temperature, humidity, wind, description
    except Exception:
        return jsonify({"error": "Falha ao obter dados do clima"}), 500

    # Tenta normalizar o nome exibido:
    display_name = name
    if not display_name:
        # tenta pegar via reverse geocode? para simplicidade, apenas usa coordenadas como fallback
        display_name = f"{lat},{lon}"

    result = {
        "city": display_name,
        "country": country or "",
        "flag": get_flag_url(country) if country else "",
        "temp": w.get("temperature"),
        "humidity": w.get("humidity"),
        "wind": w.get("wind"),
        "description": w.get("description")
    }

    cache.set(key, result)
    fila.enqueue(display_name)
    pilha.push(display_name)
    lista.add(result)

    return jsonify(result)


@app.route("/api/forecast")
def forecast():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    try:
        url = (
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,weathercode"
            "&timezone=auto"
        )

        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        if "daily" not in data:
            return jsonify({"error": "Falha ao obter previsão"}), 500

        forecast = {
            "time": data["daily"].get("time", []),
            "tmax": data["daily"].get("temperature_2m_max", []),
            "tmin": data["daily"].get("temperature_2m_min", []),
            "wcode": data["daily"].get("weathercode", []),
        }

        return jsonify(forecast)
    except Exception:
        return jsonify({"error": "Erro inesperado"}), 500


# Rotas de debug (mantive)
@app.route("/debug/queue")
def ver_fila():
    return jsonify(fila.get_all())


@app.route("/debug/stack")
def ver_pilha():
    return jsonify(pilha.get_all())


@app.route("/debug/list")
def ver_lista():
    return jsonify(lista.to_list())


@app.route("/debug/cache")
def ver_cache():
    return jsonify(cache.data)


if __name__ == "__main__":
    app.run(debug=True)
