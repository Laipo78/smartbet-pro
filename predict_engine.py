# 🔄 predict_engine.py
# Moteur de recommandation

from typing import List, Dict
import logging
from data_collector import DataCollector
from model_predictor import ModelPredictor
from bankroll_manager import BankrollManager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictEngine:
    def __init__(self):
        self.data_collector = DataCollector()
        self.model_predictor = ModelPredictor()
        self.bankroll_manager = BankrollManager()

    def analyser_matchs(self, bankroll: float) -> List[Dict]:
        """Analyse les matchs et génère des recommandations"""
        try:
            matchs = self.data_collector.get_matchs_du_jour()
            recommandations = []
            
            for match in matchs:
                try:
                    stats = self.data_collector.get_stats_simulees(match)
                    proba = self.model_predictor.evaluer_probabilites(stats)
                    cotes = self.data_collector.get_cotes_simulees(stats["forme_home"], stats["forme_away"])
                    
                    for outcome, cote in cotes.items():
                        proba_outcome = proba if outcome == "1" else (1 - proba) if outcome == "2" else 0.3
                        
                        if self.model_predictor.detecter_value_bet(proba_outcome, cote):
                            etoiles, _ = self.model_predictor.classer_confiance(proba_outcome)
                            mise = self.bankroll_manager.calcul_mise_kelly(bankroll, proba_outcome, cote)
                            
                            recommandations.append({
                                "match": f"{stats['home']} vs {stats['away']}",
                                "competition": stats.get("competition", "Inconnu"),
                                "pronostic": self._get_pronostic_text(outcome, stats),
                                "proba": proba_outcome,
                                "cote": cote,
                                "mise": mise,
                                "confiance": etoiles,
                                "value": proba_outcome * cote - 1
                            })
                except Exception as e:
                    logger.warning(f"Erreur analyse match: {e}")
            
            return sorted(recommandations, key=lambda x: x["value"], reverse=True)
        except Exception as e:
            logger.error(f"Erreur analyse globale: {e}")
            return []

    @staticmethod
    def _get_pronostic_text(outcome: str, stats: Dict) -> str:
        """Génère le texte du pronostic"""
        return {
            "1": f"Victoire {stats['home']}",
            "2": f"Victoire {stats['away']}",
            "N": "Match nul"
        }.get(outcome, "Pronostic indisponible")