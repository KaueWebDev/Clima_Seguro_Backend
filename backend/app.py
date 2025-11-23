from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.geocode import search_city
from utils.weather import get_weather
from utils.flags import get_flag_url
from utils.structures import LinkedList, Queue, Stack, HashTable
import requests  # necessário para o forecast

app = Flask(__name__)
CORS(app)

# Estruturas de dados
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

    try:
        cities = search_city(query)
        results = []
        for c in cities:
            addr = c.get("address", {})
            results.append({
                "name": c.get("display_name", "Desconhecido"),
                "lat": c.get("lat", ""),
                "lon": c.get("lon", ""),
                "country_code": addr.get("country_code", "").upper()
            })
        return jsonify(results)
    except Exception as e:
        return jsonify([]), 500


@app.route("/api/weather")
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    name = request.args.get("name", "Local Desconhecido")
    country = request.args.get("country", "")

    if not lat or not lon:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    key = f"{lat},{lon}"

    # Verifica cache
    cached = cache.get(key)
    if cached:
        return jsonify(cached)

    try:
        w = get_weather(lat, lon)
    except Exception:
        return jsonify({"error": "Falha ao obter dados do clima"}), 500

    result = {
        "city": name,
        "country": country,
        "flag": get_flag_url(country),
        "temp": w["temperature"],
        "humidity": w["humidity"],
        "wind": w["wind"],
        "description": w["description"]
    }

    # Atualiza estruturas de dados
    cache.set(key, result)
    fila.enqueue(name)
    pilha.push(name)
    lista.add(result)

    return jsonify(result)


# 🔥 NOVA ROTA — PREVISÃO COMPLETA OPEN-METEO
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

        r = requests.get(url)
        data = r.json()

        if "daily" not in data:
            return jsonify({"error": "Falha ao obter previsão"}), 500

        forecast = {
            "time": data["daily"]["time"],
            "tmax": data["daily"]["temperature_2m_max"],
            "tmin": data["daily"]["temperature_2m_min"],
            "wcode": data["daily"]["weathercode"],
        }

        return jsonify(forecast)

    except Exception:
        return jsonify({"error": "Erro inesperado"}), 500


# Rotas de debug
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
