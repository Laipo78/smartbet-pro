import requests
from datetime import datetime

# Clés API (à remplacer si besoin)
FOOTBALL_DATA_API_KEY = "e466a37640c044bfbeaceaef804ff773"
FOOTBALL_DATA_URL = "https://api.football-data.org/v4/matches"

# 🟢 1. Récupérer les matchs du jour avec gestion d'erreur améliorée
def get_matchs_du_jour():
    today = datetime.today().strftime('%Y-%m-%d')
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    
    try:
        response = requests.get(
            f"{FOOTBALL_DATA_URL}?dateFrom={today}&dateTo={today}", 
            headers=headers,
            timeout=10  # Ajout d'un timeout
        )
        
        response.raise_for_status()  # Lève une exception pour les codes 4xx/5xx
        
        data = response.json()
        matches = data.get("matches", [])
        
        if not matches:
            print(f"Aucun match trouvé pour aujourd'hui ({today}).")
        
        return matches
        
    except requests.exceptions.HTTPError as http_err:
        print(f"Erreur HTTP: {http_err}")
        if response.status_code == 403:
            print("Problème d'authentification - Vérifiez votre clé API")
        elif response.status_code == 429:
            print("Limite de requêtes API atteinte")
    except requests.exceptions.RequestException as req_err:
        print(f"Erreur de requête: {req_err}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
    
    return []

# 🟢 2. Simulation améliorée des stats de forme
def get_stats_simulees(match):
    home = match["homeTeam"].get("name", "Inconnu")
    away = match["awayTeam"].get("name", "Inconnu")
    competition = match.get("competition", {}).get("name", "Compétition inconnue")
    
    # Base de données élargie avec plus d'équipes
    base_form = {
        "PSG": 5, "Marseille": 2, "Lyon": 4, "Nice": 3, "Monaco": 4,
        "Rennes": 3, "Brest": 2, "Lens": 3, "Auxerre": 1, "Toulouse": 3,
        "Lille": 4, "Strasbourg": 2, "Reims": 3, "Montpellier": 2,
        "Nantes": 2, "Lorient": 1, "Clermont": 1, "Troyes": 1,
        "Angers": 1, "Saint-Étienne": 2
    }
    
    return {
        "home": home,
        "away": away,
        "competition": competition,
        "forme_home": base_form.get(home, 2),
        "forme_away": base_form.get(away, 2),
        "blesses": [],
        "suspensions": [],
        "enjeu": "Classique" if "PSG" in [home, away] else "Standard"
    }

# 🟢 3. Simulation des cotes avec plus de nuances
def get_cotes_simulees(forme_home, forme_away):
    delta = forme_home - forme_away
    if delta >= 3:
        return {"1": 1.40, "N": 4.00, "2": 7.50}
    elif delta == 2:
        return {"1": 1.60, "N": 3.75, "2": 5.50}
    elif delta == 1:
        return {"1": 1.85, "N": 3.40, "2": 4.20}
    elif delta == 0:
        return {"1": 2.20, "N": 3.30, "2": 3.10}
    elif delta == -1:
        return {"1": 2.80, "N": 3.40, "2": 2.40}
    else:
        return {"1": 3.50, "N": 3.60, "2": 2.00}

# 🟢 4. Nouvelle fonction pour afficher joliment les matchs
def afficher_matchs(matches):
    if not matches:
        print("Aucun match à afficher.")
        return
    
    print("\n📅 MATCHS DU JOUR 📅")
    print("=" * 50)
    
    for i, match in enumerate(matches, 1):
        home = match["homeTeam"].get("name", "Inconnu")
        away = match["awayTeam"].get("name", "Inconnu")
        competition = match.get("competition", {}).get("name", "Compétition inconnue")
        date = match.get("utcDate", "")
        
        try:
            # Formatage de la date/heure
            if date:
                dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                date_str = dt.strftime("%H:%M")
            else:
                date_str = "Heure inconnue"
        except:
            date_str = "Heure inconnue"
        
        print(f"\n⚽ Match {i}: {home} vs {away}")
        print(f"🏆 {competition}")
        print(f"⏰ {date_str}")
        print("-" * 50)

# 🟢 5. Exécution principale
if __name__ == "__main__":
    print("Récupération des matchs en cours...")
    matches = get_matchs_du_jour()
    
    if matches:
        afficher_matchs(matches)
        
        # Exemple d'utilisation des autres fonctions
        premier_match = matches[0]
        stats = get_stats_simulees(premier_match)
        cotes = get_cotes_simulees(stats["forme_home"], stats["forme_away"])
        
        print("\n📊 Stats simulées pour le premier match:")
        print(f"Forme {stats['home']}: {stats['forme_home']}/5")
        print(f"Forme {stats['away']}: {stats['forme_away']}/5")
        
        print("\n💰 Cotes simulées:")
        print(f"Victoire {stats['home']}: {cotes['1']}")
        print(f"Nul: {cotes['N']}")
        print(f"Victoire {stats['away']}: {cotes['2']}")
    else:
        print("Aucun match disponible aujourd'hui.")