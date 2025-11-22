from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.weather import get_weather
from utils.geocode import search_city
from utils.flags import get_flag_url
from utils.structures import LinkedList, Queue, Stack, HashTable

app = Flask(__name__)
CORS(app)

# ----------------- ESTRUTURAS DE DADOS -----------------
pesquisas_fila = Queue()           # últimas pesquisas
historico_pilha = Stack()          # histórico completo
previsoes_lista = LinkedList()     # previsões salvas
cache_tempo = HashTable()          # cache de tempo


@app.route("/")
def home():
    return "API de Previsão do Tempo Online!"


@app.route("/api/autocomplete")
def autocomplete():
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])

    cities = search_city(query)
    results = []

    for c in cities:
        results.append({
            "name": c.get("display_name"),
            "lat": c.get("lat"),
            "lon": c.get("lon"),
            "country_code": c.get("address", {}).get("country_code", "").upper()
        })

    return jsonify(results)


@app.route("/api/weather")
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    chave = f"{lat},{lon}"

    # ---------------- CACHE (TABELA HASH) ----------------
    dados_cache = cache_tempo.get(chave)
    if dados_cache:
        print("✔ Usando cache")
        return jsonify(dados_cache)

    # ---------------- CONSULTA NORMAL --------------------
    data = get_weather(lat, lon)

    country_code = data["sys"]["country"]
    flag = get_flag_url(country_code)
    icon_code = data["weather"][0]["icon"]

    result = {
        "city": data["name"],
        "country": country_code,
        "flag": flag,
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "description": data["weather"][0]["description"],
        "icon": icon_code
    }

    # Salvar no cache
    cache_tempo.set(chave, result)

    # ---------------- FILA (últimas pesquisas) ----------------
    pesquisas_fila.enqueue(result["city"])

    # ---------------- PILHA (histórico) ----------------
    historico_pilha.push(result["city"])

    # ---------------- LISTA LIGADA (previsões) ----------------
    previsoes_lista.add(result)

    return jsonify(result)


# ---------- ROTAS PARA VER AS ESTRUTURAS (opcional) ----------
@app.route("/api/debug/queue")
def fila_view():
    return jsonify(pesquisas_fila.get_all())

@app.route("/api/debug/stack")
def pilha_view():
    return jsonify(historico_pilha.get_all())

@app.route("/api/debug/list")
def lista_view():
    return jsonify(previsoes_lista.to_list())

@app.route("/api/debug/cache")
def cache_view():
    return jsonify(cache_tempo.table)


if __name__ == "__main__":
    app.run(debug=True)
