
import streamlit as st
from data_collector import get_matchs_du_jour, get_stats_simulees, get_cotes_simulees
from model_predictor import evaluer_probabilites, detecter_value_bet, classer_confiance
from bankroll_manager import calcul_mise_kelly, mettre_a_jour_bankroll, afficher_suivi

st.set_page_config(page_title="SmartBet Pro AI", layout="centered")
st.title("⚽🤖 SmartBet Pro AI – Analyse experte des matchs du jour")

# 💼 Bankroll
st.sidebar.title("💰 Paramètres de bankroll")
bankroll = st.sidebar.number_input("Bankroll actuelle (FCFA)", min_value=1000, value=50000, step=500)

# 📊 Résumé bankroll
total_paris, solde = afficher_suivi()
st.sidebar.markdown(f"**📄 Paris enregistrés :** {total_paris}")
st.sidebar.markdown(f"**💼 Solde actuel :** {int(solde)} FCFA")

# ⚙️ Lancer l’analyse
if st.button("🔍 Analyser les matchs du jour"):
    with st.spinner("Analyse des données en cours..."):
        matchs = get_matchs_du_jour()
        if not matchs:
            st.warning("Aucun match récupéré. Réessaie plus tard.")
        else:
            for match in matchs:
                stats = get_stats_simulees(match)
                cote = get_cotes_simulees(stats["forme_home"], stats["forme_away"])
                proba = evaluer_probabilites(stats)
                is_value = detecter_value_bet(proba, cote)
                etoiles, poids = classer_confiance(proba)
                mise = calcul_mise_kelly(bankroll, proba, cote)

                if is_value:
                    st.markdown(f"### ⚽ {stats['home']} vs {stats['away']}")
                    st.markdown(f"- 🧠 **Pronostic : Victoire {stats['home']}**")
                    st.markdown(f"- 📊 **Probabilité estimée : {int(proba * 100)}%**")
                    st.markdown(f"- 💸 **Cote estimée : {cote}**")
                    st.markdown(f"- 🌟 **Indice de confiance : {etoiles}**")
                    st.markdown(f"- 💼 **Mise conseillée : {mise} FCFA**")
                    if proba >= 0.70:
                        st.balloons()
                    st.divider()
