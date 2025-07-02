# 💰 bankroll_manager.py
# Gestion de la bankroll

import json
from pathlib import Path
from typing import Dict, Tuple
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankrollManager:
    def __init__(self, file_path: str = "historique_bankroll.json"):
        self.HISTORIQUE_PATH = Path(file_path)
        self.BANKROLL_INITIALE = 10000

    def calcul_mise_kelly(self, bankroll: float, proba: float, cote: float, fraction: float = 0.25) -> float:
        """Calcule la mise selon Kelly"""
        try:
            if cote <= 1 or not 0 <= proba <= 1:
                raise ValueError("Paramètres invalides")
            kelly = ((cote * proba) - 1) / (cote - 1)
            return round(bankroll * max(kelly, 0) * fraction, 2)
        except Exception as e:
            logger.error(f"Erreur calcul Kelly: {e}")
            return 0.0

    def charger_historique(self) -> Dict:
        """Charge l'historique des paris"""
        try:
            if self.HISTORIQUE_PATH.exists():
                with open(self.HISTORIQUE_PATH, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "solde" in data and "paris" in data:
                        return data
        except Exception as e:
            logger.error(f"Erreur chargement historique: {e}")
        return {"solde": self.BANKROLL_INITIALE, "paris": []}

    def sauvegarder_historique(self, data: Dict) -> None:
        """Sauvegarde l'historique"""
        try:
            with open(self.HISTORIQUE_PATH, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Erreur sauvegarde historique: {e}")

    def mettre_a_jour_bankroll(self, match: str, mise: float, resultat: str, cote: float) -> float:
        """Met à jour la bankroll"""
        try:
            historique = self.charger_historique()
            
            if resultat not in ["gagné", "perdu", "remboursé"] or mise < 0:
                raise ValueError("Paramètres invalides")
            
            if resultat == "gagné":
                historique["solde"] += round(mise * (cote - 1), 2)
            elif resultat == "perdu":
                historique["solde"] -= round(mise, 2)
            
            historique["paris"].append({
                "date": datetime.now().isoformat(),
                "match": match,
                "mise": mise,
                "resultat": resultat,
                "cote": cote,
                "solde_apres": historique["solde"]
            })
            
            self.sauvegarder_historique(historique)
            return historique["solde"]
        except Exception as e:
            logger.error(f"Erreur mise à jour bankroll: {e}")
            return self.charger_historique()["solde"]

    def afficher_suivi(self) -> Tuple[int, float]:
        """Retourne les stats de suivi"""
        historique = self.charger_historique()
        return len(historique["paris"]), historique["solde"]