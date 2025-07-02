# 📊 model_predictor.py
# Analyse statistique avancée et prédiction des matchs

from typing import Tuple, Dict
import numpy as np
from scipy.stats import poisson
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
import joblib
import os

MODEL_PATH = "models/betting_model_v2.pkl"
TEAM_STATS_CACHE = {}

class PredictionModel:
    def __init__(self):
        self.model = self._load_or_train_model()
        self.feature_importances = None
        
    def _load_or_train_model(self):
        """Charge un modèle existant ou en entraîne un nouveau"""
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print("Modèle pré-entraîné chargé")
        else:
            model = self._train_new_model()
            joblib.dump(model, MODEL_PATH)
            print("Nouveau modèle entraîné et sauvegardé")
        return model
    
    def _train_new_model(self):
        """Entraîne un nouveau modèle avec des données simulées"""
        # Ici vous devriez remplacer par votre vrai jeu de données
        X_train, y_train = self._generate_simulated_data()
        
        model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # Calibration pour avoir de meilleures probabilités
        calibrated_model = CalibratedClassifierCV(model, method='isotonic', cv=3)
        calibrated_model.fit(X_train, y_train)
        
        self.feature_importances = pd.DataFrame({
            'feature': X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return calibrated_model
    
    def _generate_simulated_data(self):
        """Génère des données simulées pour l'exemple"""
        # À remplacer par votre vrai pipeline de données
        np.random.seed(42)
        n_samples = 5000
        
        data = {
            'forme_home': np.random.randint(1, 6, n_samples),
            'forme_away': np.random.randint(1, 6, n_samples),
            'derniers_resultats_home': np.random.uniform(0.2, 0.8, n_samples),
            'derniers_resultats_away': np.random.uniform(0.2, 0.8, n_samples),
            'classement_home': np.random.randint(1, 20, n_samples),
            'classement_away': np.random.randint(1, 20, n_samples),
            'confrontations_directes': np.random.uniform(0.3, 0.7, n_samples),
            'blesses_home': np.random.randint(0, 5, n_samples),
            'blesses_away': np.random.randint(0, 5, n_samples)
        }
        
        X = pd.DataFrame(data)
        y = (X['forme_home'] + 0.5*X['derniers_resultats_home'] - 0.3*X['blesses_home'] > 
             X['forme_away'] + 0.5*X['derniers_resultats_away'] - 0.3*X['blesses_away']).astype(int)
        
        return X, y

def evaluer_probabilites(stats: Dict, use_advanced_model: bool = True) -> float:
    """
    Calcule la probabilité de victoire à domicile avec deux approches :
    1. Modèle avancé (si use_advanced_model=True et données disponibles)
    2. Méthode heuristique simplifiée (fallback)
    
    Args:
        stats: Dictionnaire contenant les statistiques du match
        use_advanced_model: Booléen pour utiliser le modèle ML
        
    Returns:
        Probabilité estimée [0-1]
    """
    try:
        if use_advanced_model and 'advanced_stats' in stats:
            # Utilisation du modèle ML avec toutes les features
            model = PredictionModel().model
            X_pred = pd.DataFrame([stats['advanced_stats']])
            proba = model.predict_proba(X_pred)[0][1]
            return round(np.clip(proba, 0.4, 0.85), 2)  # Bornes réalistes
    except Exception as e:
        print(f"Erreur modèle avancé, utilisation fallback: {e}")
    
    # Fallback: méthode heuristique
    base_prob = 0.5
    delta_forme = (stats["forme_home"] - stats["forme_away"]) / 5.0
    home_advantage = 0.1  # Avantage terrain
    
    proba = base_prob + delta_forme + home_advantage
    
    # Ajustements supplémentaires
    if stats.get("enjeu") == "Classique":
        proba += 0.05  # Surperformance dans les classiques
        
    if len(stats.get("blesses", [])) > 2:
        proba -= 0.05
        
    return round(np.clip(proba, 0.45, 0.8), 2)

def detecter_value_bet(proba: float, cote: float, threshold: float = 0.05) -> bool:
    """
    Détecte les value bets avec une marge de sécurité.
    
    Args:
        proba: Probabilité estimée [0-1]
        cote: Cote décimale offerte
        threshold: Seuil de valeur attendue minimum
        
    Returns:
        True si value bet détecté
    """
    if cote <= 1.0:
        return False
        
    valeur_attendue = proba * cote - 1
    proba_implicite = 1 / cote
    marge_securite = proba - proba_implicite
    
    return (valeur_attendue >= threshold) and (marge_securite >= 0.03)

def classer_confiance(proba: float) -> Tuple[str, float]:
    """
    Classe la confiance dans le pronostic selon une échelle non linéaire.
    
    Args:
        proba: Probabilité estimée [0-1]
        
    Returns:
        Tuple (étoiles, poids pour bankroll)
    """
    if proba >= 0.78:
        return "⭐⭐⭐⭐⭐", 1.0  # Très haute confiance
    elif proba >= 0.73:
        return "⭐⭐⭐⭐", 0.8    # Haute confiance
    elif proba >= 0.68:
        return "⭐⭐⭐", 0.6      # Confiance moyenne
    elif proba >= 0.63:
        return "⭐⭐", 0.4        # Confiance limitée
    elif proba >= 0.55:
        return "⭐", 0.2         # Faible confiance
    else:
        return "✖️", 0.0        # A éviter

def simulate_match_outcome(home_prob: float, n_simulations: int = 10000) -> Dict:
    """
    Simule les résultats possibles du match avec distribution de Poisson.
    
    Args:
        home_prob: Probabilité de victoire à domicile
        n_simulations: Nombre de simulations
        
    Returns:
        Dictionnaire avec probabilités des différents résultats
    """
    # Estimation des buts moyens
    home_goals = 1.2 + (home_prob - 0.5) * 1.5
    away_goals = 1.2 - (home_prob - 0.5) * 1.2
    
    home_wins = 0
    draws = 0
    away_wins = 0
    
    for _ in range(n_simulations):
        hg = poisson.rvs(home_goals)
        ag = poisson.rvs(away_goals)
        
        if hg > ag:
            home_wins += 1
        elif hg == ag:
            draws += 1
        else:
            away_wins += 1
    
    return {
        "1": home_wins / n_simulations,
        "N": draws / n_simulations,
        "2": away_wins / n_simulations,
        "goals_home": home_goals,
        "goals_away": away_goals
    }

# Test des fonctions
if __name__ == "__main__":
    test_stats = {
        "forme_home": 4,
        "forme_away": 2,
        "enjeu": "Classique",
        "blesses": ["joueur1", "joueur2"],
        "advanced_stats": {
            "forme_home": 4,
            "forme_away": 2,
            "derniers_resultats_home": 0.7,
            "derniers_resultats_away": 0.4,
            "classement_home": 3,
            "classement_away": 8,
            "confrontations_directes": 0.6,
            "blesses_home": 2,
            "blesses_away": 0
        }
    }
    
    proba = evaluer_probabilites(test_stats)
    print(f"Probabilité estimée: {proba:.2f}")
    
    cote = 2.10
    is_value = detecter_value_bet(proba, cote)
    print(f"Value bet: {is_value}")
    
    etoiles, poids = classer_confiance(proba)
    print(f"Confiance: {etoiles} (poids: {poids})")
    
    simulation = simulate_match_outcome(proba)
    print("\nSimulation des résultats:")
    print(f"Victoire domicile: {simulation['1']:.1%}")
    print(f"Nul: {simulation['N']:.1%}")
    print(f"Victoire extérieur: {simulation['2']:.1%}")
    print(f"Buts moyens (domicile/extérieur): {simulation['goals_home']:.1f}/{simulation['goals_away']:.1f}")