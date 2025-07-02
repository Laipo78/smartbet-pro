# 📊 model_predictor.py
# Analyse statistique et prédiction

from typing import Tuple
import numpy as np
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelPredictor:
    @staticmethod
    def evaluer_probabilites(stats: dict) -> float:
        """Calcule la probabilité de victoire"""
        try:
            base = 0.5
            delta = (stats["forme_home"] - stats["forme_away"]) / 5.0
            proba = base + delta + 0.1  # Avantage domicile
            
            # Ajustements contextuels
            if stats.get("enjeu") == "Classique":
                proba += 0.05
            if len(stats.get("blesses", [])) > 2:
                proba -= 0.05
                
            return np.clip(proba, 0.45, 0.8)
        except Exception as e:
            logger.error(f"Erreur calcul proba: {e}")
            return 0.5

    @staticmethod
    def detecter_value_bet(proba: float, cote: float, threshold: float = 0.05) -> bool:
        """Détecte les value bets"""
        return False if cote <= 1.0 else (proba * cote - 1) >= threshold

    @staticmethod
    def classer_confiance(proba: float) -> Tuple[str, float]:
        """Classe la confiance du pronostic"""
        if proba >= 0.75: return "⭐⭐⭐⭐⭐", 1.0
        elif proba >= 0.70: return "⭐⭐⭐⭐", 0.8
        elif proba >= 0.65: return "⭐⭐⭐", 0.6
        elif proba >= 0.60: return "⭐⭐", 0.4
        elif proba >= 0.55: return "⭐", 0.2
        return "✖️", 0.0