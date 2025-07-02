
# 📊 model_predictor.py
# Analyse statistique et prédiction des issues probables

def evaluer_probabilites(stats):
    # Calcule une probabilité simplifiée basée sur la forme
    delta = stats["forme_home"] - stats["forme_away"]
    base = 0.55 + 0.05 * delta
    return round(max(0.45, min(base, 0.80)), 2)  # Bornes de sécurité

def detecter_value_bet(proba, cote):
    proba_implicite = 1 / cote
    return proba > proba_implicite

def classer_confiance(proba):
    if proba >= 0.75:
        return "⭐⭐⭐⭐⭐", 1.0
    elif proba >= 0.70:
        return "⭐⭐⭐⭐", 0.8
    elif proba >= 0.65:
        return "⭐⭐⭐", 0.6
    elif proba >= 0.60:
        return "⭐⭐", 0.4
    else:
        return "⭐", 0.2
