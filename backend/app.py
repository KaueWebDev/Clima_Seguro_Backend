from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.geocode import search_city
from utils.weather import get_weather
from utils.flags import get_flag_url
from utils.structures import LinkedList, Queue, Stack, HashTable

app = Flask(__name__)
CORS(app)

fila = Queue()
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

    cities = search_city(query)
    results = []

    for c in cities:
        results.append({
            "name": c["display_name"],
            "lat": c["lat"],
            "lon": c["lon"],
            "country": c["address"].get("country_code", "").upper()
        })

    return jsonify(results)


@app.route("/api/weather")
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    name = request.args.get("name", "Local Desconhecido")
    country = request.args.get("country", "")

    key = f"{lat},{lon}"

    cached = cache.get(key)
    if cached:
        return jsonify(cached)

    w = get_weather(lat, lon)

    result = {
        "city": name,
        "country": country,
        "flag": get_flag_url(country),
        "temp": w["temperature"],
        "humidity": w["humidity"],
        "wind": w["wind"],
        "description": "Condição atual"
    }

    cache.set(key, result)
    fila.enqueue(name)
    pilha.push(name)
    lista.add(result)

    return jsonify(result)


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
