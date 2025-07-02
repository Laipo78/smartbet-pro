# 📊 data_collector.py
# Collecte des données des matchs

import requests
from datetime import datetime
from typing import List, Dict
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, api_key: str = "votre_cle_api"):
        self.API_KEY = api_key
        self.BASE_URL = "https://api.football-data.org/v4/"
        self.cache = None
        self.last_update = None

    def get_matchs_du_jour(self) -> List[Dict]:
        """Récupère les matchs du jour avec cache"""
        try:
            today = datetime.today().strftime('%Y-%m-%d')
            headers = {"X-Auth-Token": self.API_KEY}
            
            response = requests.get(
                f"{self.BASE_URL}matches?dateFrom={today}&dateTo={today}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            self.cache = response.json().get("matches", [])
            self.last_update = datetime.now()
            return self.cache
            
        except Exception as e:
            logger.error(f"Erreur API: {e}")
            return self.cache or []

    @staticmethod
    def get_stats_simulees(match: Dict) -> Dict:
        """Génère des statistiques simulées"""
        home = match.get("homeTeam", {}).get("name", "Inconnu")
        away = match.get("awayTeam", {}).get("name", "Inconnu")
        
        base_form = {
            "PSG": 5, "Marseille": 4, "Lyon": 3, "Nice": 4, "Monaco": 3,
            "Rennes": 3, "Lille": 4, "Brest": 2, "Lens": 3, "Reims": 2
        }
        
        return {
            "home": home,
            "away": away,
            "competition": match.get("competition", {}).get("name", "Inconnu"),
            "forme_home": base_form.get(home, 2),
            "forme_away": base_form.get(away, 2),
            "blesses": [],
            "enjeu": "Classique" if {home, away} == {"PSG", "Marseille"} else "Standard"
        }

    @staticmethod
    def get_cotes_simulees(forme_home: int, forme_away: int) -> Dict[str, float]:
        """Génère des cotes simulées"""
        delta = forme_home - forme_away
        return {
            (delta >= 2): {"1": 1.6, "N": 3.8, "2": 5.5},
            (delta == 1): {"1": 1.85, "N": 3.5, "2": 4.2},
            (delta == 0): {"1": 2.2, "N": 3.3, "2": 3.1},
            (delta == -1): {"1": 2.8, "N": 3.4, "2": 2.4}
        }.get(True, {"1": 3.5, "N": 3.6, "2": 2.0})