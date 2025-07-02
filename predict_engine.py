
# 🔄 predict_engine.py
# Coordination du bot SmartBet Pro AI

from data_collector import get_matchs_du_jour, get_stats_simulees, get_cotes_simulees
from model_predictor import evaluer_probabilites, detecter_value_bet, classer_confiance
from bankroll_manager import calcul_mise_kelly

def analyser_matchs(bankroll):
    matchs = get_matchs_du_jour()
    recommandations = []

    for match in matchs:
        stats = get_stats_simulees(match)
        proba = evaluer_probabilites(stats)
        cote = get_cotes_simulees(stats["forme_home"], stats["forme_away"])
        value = detecter_value_bet(proba, cote)

        if value:
            etoiles, poids = classer_confiance(proba)
            mise = calcul_mise_kelly(bankroll, proba, cote)

            recommandations.append({
                "match": f"{stats['home']} vs {stats['away']}",
                "proba": proba,
                "cote": cote,
                "mise": mise,
                "pronostic": f"Victoire {stats['home']}",
                "etoiles": etoiles
            })

    return recommandations
