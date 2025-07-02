# 💸 bankroll_manager.py
# Gestion de la bankroll et calcul des mises

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

HISTORIQUE_PATH = Path("historique_bankroll.json")
BANKROLL_INITIALE = 50000  # Bankroll de départ

def calcul_mise_kelly(bankroll: float, proba: float, cote: float, fraction: float = 0.25) -> float:
    """
    Calcule la mise selon le critère de Kelly fractionné
    Args:
        bankroll: Solde actuel
        proba: Probabilité estimée de succès (0-1)
        cote: Cote décimale offerte
        fraction: Fraction du Kelly à utiliser (par défaut 0.25 = 1/4 Kelly)
    Returns:
        Mise calculée arrondie
    """
    try:
        if cote <= 1:
            raise ValueError("La cote doit être > 1")
        if not 0 <= proba <= 1:
            raise ValueError("La probabilité doit être entre 0 et 1")
        
        kelly = ((cote * proba) - 1) / (cote - 1)
        mise = bankroll * max(kelly, 0) * fraction
        return round(mise, 2)  # Arrondi à 2 décimales pour les centimes
    except (ZeroDivisionError, ValueError) as e:
        print(f"Erreur calcul Kelly: {e}")
        return 0.0

def charger_historique() -> Dict:
    """
    Charge l'historique depuis le fichier JSON
    Returns:
        Dictionnaire avec solde et historique des paris
    """
    try:
        if HISTORIQUE_PATH.exists():
            with open(HISTORIQUE_PATH, "r", encoding='utf-8') as f:
                historique = json.load(f)
                # Validation des données chargées
                if "solde" not in historique or "paris" not in historique:
                    raise ValueError("Format d'historique invalide")
                return historique
    except (json.JSONDecodeError, IOError, ValueError) as e:
        print(f"Erreur chargement historique: {e}. Nouvel historique créé.")
    
    # Retourne une nouvelle bankroll si problème
    return {"solde": BANKROLL_INITIALE, "paris": []}

def sauvegarder_historique(historique: Dict) -> None:
    """
    Sauvegarde l'historique dans le fichier JSON
    Args:
        historique: Dictionnaire à sauvegarder
    """
    try:
        with open(HISTORIQUE_PATH, "w", encoding='utf-8') as f:
            json.dump(historique, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Erreur sauvegarde historique: {e}")

def mettre_a_jour_bankroll(match: str, mise: float, resultat: str, cote: float) -> float:
    """
    Met à jour la bankroll après un pari
    Args:
        match: Description du match
        mise: Montant misé
        resultat: "gagné", "perdu" ou "remboursé"
        cote: Cote du pari
    Returns:
        Nouveau solde
    """
    historique = charger_historique()
    
    # Validation des entrées
    if resultat not in ["gagné", "perdu", "remboursé"]:
        raise ValueError("Résultat doit être 'gagné', 'perdu' ou 'remboursé'")
    if mise < 0:
        raise ValueError("La mise ne peut pas être négative")
    
    # Calcul du nouveau solde
    if resultat == "gagné":
        gain = round(mise * (cote - 1), 2)  # Profit net (mise incluse dans cote)
        historique["solde"] += gain
    elif resultat == "perdu":
        historique["solde"] -= round(mise, 2)
    
    # Enregistrement du pari
    historique["paris"].append({
        "date": datetime.now().isoformat(),
        "match": match,
        "mise": mise,
        "resultat": resultat,
        "cote": cote,
        "solde_apres": historique["solde"]
    })
    
    sauvegarder_historique(historique)
    return historique["solde"]

def afficher_suivi() -> Tuple[int, float]:
    """
    Donne le suivi global des paris
    Returns:
        Tuple (nombre_total_paris, solde_actuel)
    """
    historique = charger_historique()
    return len(historique["paris"]), historique["solde"]

def afficher_statistiques() -> None:
    """
    Affiche des statistiques détaillées sur les paris
    """
    historique = charger_historique()
    paris = historique["paris"]
    
    if not paris:
        print("Aucun pari enregistré")
        return
    
    # Calcul des stats
    total_paris = len(paris)
    paris_gagnes = sum(1 for p in paris if p["resultat"] == "gagné")
    taux_reussite = (paris_gagnes / total_paris) * 100 if total_paris > 0 else 0
    profit_total = historique["solde"] - BANKROLL_INITIALE
    mise_totale = sum(p["mise"] for p in paris)
    roi = (profit_total / mise_totale) * 100 if mise_totale > 0 else 0
    
    # Affichage
    print("\n📊 STATISTIQUES PARIS 📊")
    print("=" * 50)
    print(f"Bankroll initiale: {BANKROLL_INITIALE} €")
    print(f"Bankroll actuelle: {historique['solde']:.2f} €")
    print(f"Profit total: {profit_total:.2f} €")
    print(f"Nombre total de paris: {total_paris}")
    print(f"Paris gagnés: {paris_gagnes} ({taux_reussite:.1f}%)")
    print(f"Mise totale: {mise_totale:.2f} €")
    print(f"ROI: {roi:.1f}%")
    print("=" * 50)
    
    # Derniers paris
    print("\nDerniers paris:")
    for pari in paris[-5:][::-1]:  # Affiche les 5 derniers (du plus récent)
        resultat = "✅" if pari["resultat"] == "gagné" else "❌" if pari["resultat"] == "perdu" else "➖"
        print(f"{pari['date'][:10]} - {pari['match'][:30]}... - Mise: {pari['mise']}€ - Cote: {pari['cote']} - {resultat}")

# Test des fonctions
if __name__ == "__main__":
    # Exemple d'utilisation
    bankroll = charger_historique()["solde"]
    proba = 0.55  # Probabilité estimée à 55%
    cote = 2.10   # Cote décimale
    
    mise = calcul_mise_kelly(bankroll, proba, cote)
    print(f"Mise calculée: {mise:.2f} €")
    
    # Simulation de paris
    try:
        mettre_a_jour_bankroll("PSG vs Marseille", mise, "gagné", cote)
        mettre_a_jour_bankroll("Lyon vs Nice", 100, "perdu", 1.95)
        
        total, solde = afficher_suivi()
        print(f"\nSuivi: {total} paris - Bankroll: {solde:.2f} €")
        
        afficher_statistiques()
    except Exception as e:
        print(f"Erreur: {e}")