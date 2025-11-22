from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.geocode import search_city
from utils.weather import get_weather
from utils.flags import get_flag_url
from utils.structures import LinkedList, Queue, Stack, HashTable

app = Flask(__name__)
CORS(app)

fila = Queue(limit=10)
pilha = Stack()
lista = LinkedList()
cache = HashTable()


@app.route("/")
def home():
    return "API ON — Open-Meteo + Estruturas"


@app.route("/api/autocomplete")
def autocomplete():
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])

    try:
        cities = search_city(query)
    except Exception as e:
        return jsonify([]), 500

    results = []
    for c in cities:
        results.append({
            "name": c.get("display_name"),
            "lat": c.get("lat"),
            "lon": c.get("lon"),
            "country": c.get("address", {}).get("country_code", "").upper()
        })

    return jsonify(results)


@app.route("/api/weather")
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    name = request.args.get("name", None)
    country = request.args.get("country", "")

    if not lat or not lon:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    key = f"{lat},{lon}"

    # cache
    cached = cache.get(key)
    if cached:
        # se o frontend quiser mostrar o nome enviado, priorizamos name se fornecido
        if name:
            cached = dict(cached)  # shallow copy
            cached["city"] = name
            cached["country"] = country
            cached["flag"] = get_flag_url(country)
        return jsonify(cached)

    try:
        w = get_weather(lat, lon)
    except Exception as e:
        return jsonify({"error": "Erro ao buscar tempo"}), 500

    result = {
        "city": name or "Local Desconhecido",
        "country": country,
        "flag": get_flag_url(country),
        "temp": w.get("temperature"),
        "humidity": w.get("humidity"),
        "wind": w.get("wind"),
        "description": "Condição atual"
    }

    cache.set(key, result)
    fila.enqueue(result["city"])
    pilha.push(result["city"])
    lista.add(result)

    return jsonify(result)


# Debug routes
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
    app.run(debug=True, host="0.0.0.0")
