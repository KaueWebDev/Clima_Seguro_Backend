from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.geocode import search_city
from utils.weather import get_weather
from utils.flags import get_flag_url
from utils.structures import LinkedList, Queue, Stack, HashTable
import requests

app = Flask(__name__)
CORS(app)

fila = Queue()
pilha = Stack()
lista = LinkedList()
cache = HashTable()


# --------------------------
# Normalizar nomes (global)
# --------------------------
def normalize_name(full_name):
    parts = full_name.split(",")

    city = parts[0].strip()

    state = "??"
    country = "??"

    for p in parts:
        if len(p.strip()) == 2 and p.strip().isalpha():
            state = p.strip().upper()
        if len(p.strip()) == 2 and p.strip().isalpha():
            country = p.strip().upper()

    return city, state, country


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
            name_raw = c.get("display_name", "Desconhecido")

            city, state, country = normalize_name(name_raw)

            results.append({
                "name": city,
                "state": state,
                "country": country,
                "lat": c.get("lat", ""),
                "lon": c.get("lon", ""),
                "country_code": country
            })

        return jsonify(results)

    except:
        return jsonify([]), 500


@app.route("/api/weather")
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    name = request.args.get("name", "")
    country = request.args.get("country", "")

    if not lat or not lon:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    key = f"{lat},{lon}"
    cached = cache.get(key)
    if cached:
        return jsonify(cached)

    try:
        w = get_weather(lat, lon)
    except:
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

    cache.set(key, result)
    fila.enqueue(name)
    pilha.push(name)
    lista.add(result)

    return jsonify(result)


# --------------------------
# PREVISÃO OPEN-METEO
# --------------------------
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
            "wcode": data["daily"]["weathercode"]
        }

        return jsonify(forecast)

    except:
        return jsonify({"error": "Erro inesperado"}), 500


if __name__ == "__main__":
    app.run(debug=True)
