from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.structures import LinkedList, Queue, Stack, HashTable
from utils.weather import get_weather
from utils.geocode import search_city
from utils.flags import get_flag_url

app = Flask(__name__)
CORS(app)

# Estruturas de histórico
queue_history = Queue()
stack_history = Stack()
list_history = LinkedList()
cache = HashTable()

@app.route("/api/weather")
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    city = request.args.get("city", "Desconhecido")
    state = request.args.get("state", "")
    country = request.args.get("country", "")

    if not lat or not lon:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    # Cache key
    key = f"{lat},{lon}"
    cached = cache.get(key)
    if cached:
        return jsonify(cached)

    # Busca clima real
    try:
        w = get_weather(lat, lon)
    except Exception:
        return jsonify({"error": "Falha ao obter dados do clima"}), 500

    result = {
        "city": city,
        "state": state,
        "country": country,
        "flag": get_flag_url(country),
        "temp": w["temperature"],
        "humidity": w["humidity"],
        "wind": w["wind"],
        "description": w["description"]
    }

    # Atualiza histórico
    history_entry = f"{city}, {state}, {country}"
    queue_history.enqueue(history_entry)
    stack_history.push(history_entry)
    list_history.add(history_entry)

    # Atualiza cache
    cache.set(key, result)
    return jsonify(result)

@app.route("/api/forecast")
def forecast():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    try:
        import requests
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        )
        r = requests.get(url)
        data = r.json()
        forecast = {
            "time": data["daily"]["time"],
            "tmax": data["daily"]["temperature_2m_max"],
            "tmin": data["daily"]["temperature_2m_min"],
            "wcode": data["daily"]["weathercode"],
        }
        return jsonify(forecast)
    except Exception:
        return jsonify({"error": "Erro ao obter forecast"}), 500

# Histórico
@app.route("/history/queue")
def get_queue():
    return jsonify(queue_history.get_all())

@app.route("/history/stack")
def get_stack():
    return jsonify(stack_history.get_all())

@app.route("/history/list")
def get_list():
    return jsonify(list_history.to_list())

@app.route("/api/autocomplete")
def autocomplete():
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])

    try:
        cities = search_city(query)
        results = []
        for c in cities[:2]:  # só 2 resultados
            addr = c.get("address", {})
            results.append({
                "name": c.get("display_name", "Desconhecido"),
                "lat": c.get("lat", ""),
                "lon": c.get("lon", ""),
                "country_code": addr.get("country_code", "").upper()
            })
        return jsonify(results)
    except Exception:
        return jsonify([]), 500

if __name__ == "__main__":
    app.run(debug=True)
