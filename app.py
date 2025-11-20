from flask import Flask, request, jsonify
from utils.weather import get_weather
from utils.geocode import search_city
from utils.flags import get_flag_url

app = Flask(name)

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

    data = get_weather(lat, lon)

    country_code = data["sys"]["country"]
    flag = get_flag_url(country_code)

    result = {
        "city": data["name"],
        "country": country_code,
        "flag": flag,
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "description": data["weather"][0]["description"],
        "icon": f"https://openweathermap.org/img/wn/%7Bdata['weather'][0]['icon']%7D@2x.png"
    }

    return jsonify(result)

if name == "main":
    app.run(debug=True)