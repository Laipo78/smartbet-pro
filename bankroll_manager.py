
# 💸 bankroll_manager.py
# Gestion de la bankroll et calcul des mises

import json
from pathlib import Path

HISTORIQUE_PATH = Path("historique_bankroll.json")

def calcul_mise_kelly(bankroll, proba, cote, fraction=0.25):
    try:
        kelly = ((cote * proba) - 1) / (cote - 1)
        mise = bankroll * max(kelly, 0) * fraction
        return round(mise, 0)
    except ZeroDivisionError:
        return 0

def charger_historique():
    if HISTORIQUE_PATH.exists():
        with open(HISTORIQUE_PATH, "r") as f:
            return json.load(f)
    return {"solde": 50000, "paris": []}

def sauvegarder_historique(historique):
    with open(HISTORIQUE_PATH, "w") as f:
        json.dump(historique, f, indent=4)

def mettre_a_jour_bankroll(match, mise, resultat, cote):
    historique = charger_historique()
    if resultat == "gagné":
        gain = mise * cote
        historique["solde"] += gain - mise
    elif resultat == "perdu":
        historique["solde"] -= mise
    else:  # remboursé
        pass
    historique["paris"].append({
        "match": match,
        "mise": mise,
        "resultat": resultat,
        "cote": cote
    })
    sauvegarder_historique(historique)
    return historique["solde"]

def afficher_suivi():
    historique = charger_historique()
    total_paris = len(historique["paris"])
    solde = historique["solde"]
    return total_paris, solde
