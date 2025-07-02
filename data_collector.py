
import requests
from datetime import datetime

# Clés API (à remplacer si besoin)
FOOTBALL_DATA_API_KEY = "e466a37640c044bfbeaceaef804ff773"
FOOTBALL_DATA_URL = "https://api.football-data.org/v4/matches"

# 🟢 1. Récupérer les matchs du jour
def get_matchs_du_jour():
    today = datetime.today().strftime('%Y-%m-%d')
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    try:
        response = requests.get(f"{FOOTBALL_DATA_URL}?dateFrom={today}&dateTo={today}", headers=headers)
        if response.status_code == 200:
            return response.json().get("matches", [])
        else:
            print("Erreur API Football-Data:", response.status_code)
            return []
    except Exception as e:
        print("Erreur de connexion :", e)
        return []

# 🟢 2. Simulation simple des stats de forme pour démarrer
def get_stats_simulees(match):
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    base_form = {
        "PSG": 5, "Marseille": 2, "Lyon": 4, "Nice": 3, "Monaco": 4,
        "Rennes": 3, "Brest": 2, "Lens": 3, "Auxerre": 1, "Toulouse": 3
    }
    return {
        "home": home,
        "away": away,
        "forme_home": base_form.get(home, 2),
        "forme_away": base_form.get(away, 2),
        "blesses": [],
        "suspensions": [],
        "enjeu": "Classique"
    }

# 🟢 3. Simulation des cotes réelles si pas d’API de bookmaker
def get_cotes_simulees(forme_home, forme_away):
    delta = forme_home - forme_away
    if delta >= 2:
        return 1.60
    elif delta == 1:
        return 1.85
    elif delta == 0:
        return 2.20
    else:
        return 2.80
