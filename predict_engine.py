# 🔄 predict_engine.py
# Moteur intelligent de recommandation de paris sportifs

from typing import List, Dict, Optional
import logging
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Modules personnalisés
from data_collector import get_matchs_du_jour, get_stats_simulees, get_cotes_simulees
from model_predictor import (
    evaluer_probabilites, 
    detecter_value_bet, 
    classer_confiance,
    simulate_match_outcome
)
from bankroll_manager import calcul_mise_kelly

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('predict_engine.log'),
        logging.StreamHandler()
    ]
)

class PredictionEngine:
    def __init__(self):
        self.cache_matchs = None
        self.last_update = None
        self.cache_duration = 3600  # 1 heure en secondes

    def _should_refresh_cache(self) -> bool:
        """Détermine si le cache doit être rafraîchi"""
        if self.cache_matchs is None or self.last_update is None:
            return True
        return (datetime.now() - self.last_update).total_seconds() > self.cache_duration

    def _get_match_data(self, force_refresh: bool = False) -> List[Dict]:
        """Récupère les données des matchs avec système de cache"""
        if not force_refresh and not self._should_refresh_cache():
            logging.info("Utilisation des données en cache")
            return self.cache_matchs

        try:
            logging.info("Mise à jour des données des matchs...")
            start_time = time.time()
            
            with ThreadPoolExecutor() as executor:
                matchs_data = list(executor.map(self._process_single_match, get_matchs_du_jour()))
            
            self.cache_matchs = [m for m in matchs_data if m is not None]
            self.last_update = datetime.now()
            
            logging.info(f"Données mises à jour. {len(self.cache_matchs)} matchs analysés en {time.time()-start_time:.2f}s")
            return self.cache_matchs
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des matchs: {e}")
            return self.cache_matchs or []

    def _process_single_match(self, match: Dict) -> Optional[Dict]:
        """Traite un seul match et retourne les données analysées"""
        try:
            stats = get_stats_simulees(match)
            proba = evaluer_probabilites(stats)
            cotes = get_cotes_simulees(stats["forme_home"], stats["forme_away"])
            simulation = simulate_match_outcome(proba)
            
            return {
                "match_info": match,
                "stats": stats,
                "proba": proba,
                "cotes": cotes,
                "simulation": simulation
            }
        except Exception as e:
            logging.warning(f"Erreur lors du traitement d'un match: {e}")
            return None

    def analyser_matchs(
        self,
        bankroll: float,
        min_confidence: int = 3,
        min_value_threshold: float = 0.05,
        max_bet_percent: float = 0.05
    ) -> List[Dict]:
        """
        Analyse tous les matchs et génère des recommandations de paris
        
        Args:
            bankroll: Bankroll totale disponible
            min_confidence: Niveau de confiance minimum (1-5)
            min_value_threshold: Seuil minimum de valeur attendue
            max_bet_percent: Pourcentage maximum de la bankroll à miser
            
        Returns:
            Liste des recommandations de paris
        """
        try:
            matchs_data = self._get_match_data()
            recommandations = []
            
            for data in matchs_data:
                try:
                    pronostic, value_bet = self._evaluer_pronostic(data, min_value_threshold)
                    
                    if value_bet and pronostic["confidence"][0] >= min_confidence:
                        pronostic["mise"] = self._calculer_mise_optimale(
                            bankroll,
                            pronostic["proba"],
                            pronostic["cote"],
                            max_bet_percent
                        )
                        recommandations.append(pronostic)
                        
                except Exception as e:
                    logging.warning(f"Erreur lors de l'analyse d'un match: {e}")
                    continue
            
            # Tri des recommandations par valeur attendue décroissante
            recommandations.sort(
                key=lambda x: (x["proba"] * x["cote"] - 1), 
                reverse=True
            )
            
            logging.info(f"Généré {len(recommandations)} recommandations de paris")
            return recommandations
            
        except Exception as e:
            logging.error(f"Erreur critique dans l'analyse: {e}")
            return []

    def _evaluer_pronostic(self, match_data: Dict, min_value: float) -> Tuple[Dict, bool]:
        """
        Évalue un pronostic pour un match donné
        
        Args:
            match_data: Données complètes du match
            min_value: Seuil de valeur attendue minimum
            
        Returns:
            Tuple (pronostic, is_value_bet)
        """
        stats = match_data["stats"]
        proba = match_data["proba"]
        cotes = match_data["cotes"]
        simulation = match_data["simulation"]
        
        # Détection du meilleur value bet (1/N/2)
        best_bet = self._trouver_meilleur_pronostic(proba, cotes, simulation, min_value)
        
        if best_bet:
            pronostic_type, cote, proba_corrected = best_bet
            value_bet = True
            
            pronostic = {
                "match": f"{stats['home']} vs {stats['away']}",
                "competition": stats.get("competition", "Inconnu"),
                "date": match_data["match_info"].get("utcDate", ""),
                "pronostic": self._get_pronostic_text(pronostic_type, stats),
                "proba": proba_corrected,
                "cote": cote,
                "value": proba_corrected * cote - 1,
                "confidence": classer_confiance(proba_corrected),
                "simulation": simulation,
                "stats": {
                    "forme_home": stats["forme_home"],
                    "forme_away": stats["forme_away"],
                    "blessures": len(stats.get("blesses", [])),
                    "enjeu": stats.get("enjeu", "Standard")
                }
            }
            
            return pronostic, value_bet
        
        return None, False

    def _trouver_meilleur_pronostic(self, proba_home, cotes, simulation, min_value):
        """
        Trouve le meilleur pronostic parmi les 3 possibilités (1/N/2)
        """
        probas = {
            "1": proba_home,
            "N": simulation["N"],
            "2": 1 - proba_home
        }
        
        best_bet = None
        best_value = min_value
        
        for outcome in ["1", "N", "2"]:
            cote = cotes.get(outcome, 1.0)
            proba = probas[outcome]
            value = proba * cote - 1
            
            if value > best_value:
                best_value = value
                best_bet = (outcome, cote, proba)
        
        return best_bet

    def _get_pronostic_text(self, pronostic_type, stats):
        """Génère le texte du pronostic"""
        if pronostic_type == "1":
            return f"Victoire {stats['home']}"
        elif pronostic_type == "2":
            return f"Victoire {stats['away']}"
        else:
            return "Match nul"

    def _calculer_mise_optimale(self, bankroll, proba, cote, max_bet_percent):
        """
        Calcule la mise optimale avec contraintes de bankroll
        """
        mise_kelly = calcul_mise_kelly(bankroll, proba, cote)
        mise_max = bankroll * max_bet_percent
        return min(mise_kelly, mise_max)

    def get_match_stats(self, match_id: str) -> Optional[Dict]:
        """Récupère les statistiques détaillées pour un match spécifique"""
        if self.cache_matchs is None:
            self._get_match_data()
        
        for match in self.cache_matchs or []:
            if match["match_info"].get("id") == match_id:
                return match
        return None

# Interface simplifiée pour compatibilité ascendante
def analyser_matchs(bankroll: float) -> List[Dict]:
    """Interface simplifiée pour les anciens codes"""
    engine = PredictionEngine()
    return engine.analyser_matchs(bankroll)

# Exemple d'utilisation
if __name__ == "__main__":
    engine = PredictionEngine()
    
    # Analyse avec paramètres avancés
    recommandations = engine.analyser_matchs(
        bankroll=10000,
        min_confidence=3,
        min_value_threshold=0.07,
        max_bet_percent=0.03
    )
    
    print("\n🔎 Recommandations de paris:")
    for i, reco in enumerate(recommandations, 1):
        print(f"\n⚽ Match {i}: {reco['match']} ({reco['competition']})")
        print(f"📅 Date: {reco.get('date', 'Inconnue')}")
        print(f"🧠 Pronostic: {reco['pronostic']}")
        print(f"📊 Probabilité: {reco['proba']:.0%}")
        print(f"💰 Cote: {reco['cote']:.2f}")
        print(f"⭐ Confiance: {reco['confidence'][0]}")
        print(f"💵 Mise conseillée: {reco['mise']:.2f} €")
        print(f"📈 Valeur attendue: {reco['value']:.1%}")