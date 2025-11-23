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


def format_city_name(result):
    """
    Converte:
    'Maceió, Região Geográfica..., Alagoas, Região Nordeste, Brasil'
    para:
    'Maceió - AL, BR'
    """
    addr = result.get("address", {})

    city = (
        addr.get("city")
        or addr.get("town")
        or addr.get("village")
        or addr.get("municipality")
        or result.get("name", "").split(",")[0]
    )

    state_code = addr.get("ISO3166-2-lvl4", "")
    if state_code:
        state_code = state_code.split("-")[-1]

    country_code = addr.get("country_code", "").upper()

    final_name = f"{city} - {state_code}, {country_code}".strip()
    return final_name


@app.route("/")
def home():
    return "API ON — Open-Meteo + Estruturas"


@app.route("/api/autocomplete")
def autocomplete():
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])

    try:
        results = []
        seen = set()

        cities = search_city(query)

        for c in cities:
            formatted = format_city_name(c)

            if formatted in seen:
                continue
            seen.add(formatted)

            addr = c.get("address", {})

            results.append({
                "name": formatted,
                "lat": c.get("lat", ""),
                "lon": c.get("lon", ""),
                "country_code": addr.get("country_code", "").upper()
            })
        return jsonify(results)

    except Exception as e:
        print("Erro:", e)
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
