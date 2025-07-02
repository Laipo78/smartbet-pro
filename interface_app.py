import streamlit as st
from datetime import datetime
import time
from data_collector import get_matchs_du_jour, get_stats_simulees, get_cotes_simulees
from model_predictor import evaluer_probabilites, detecter_value_bet, classer_confiance
from bankroll_manager import calcul_mise_kelly, mettre_a_jour_bankroll, afficher_suivi, afficher_statistiques

# Configuration de la page
st.set_page_config(
    page_title="SmartBet Pro AI",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .value-bet {
            border-left: 5px solid #4CAF50;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #f8fff8;
        }
        .header {
            color: #2c3e50;
        }
        .positive {
            color: #27ae60;
        }
        .negative {
            color: #e74c3c;
        }
    </style>
""", unsafe_allow_html=True)

# Titre principal
st.title("⚽🤖 SmartBet Pro AI")
st.markdown("### Analyse experte des matchs du jour - Version Premium")

# Sidebar - Gestion de bankroll
st.sidebar.title("💰 Gestion Bankroll")
bankroll = st.sidebar.number_input(
    "Bankroll actuelle (FCFA)",
    min_value=1000,
    value=50000,
    step=500,
    help="Définissez votre bankroll totale disponible pour les paris"
)

# Affichage des statistiques
total_paris, solde = afficher_suivi()
profit = solde - bankroll
profit_color = "positive" if profit >= 0 else "negative"

st.sidebar.markdown(f"""
    **📊 Statistiques Bankroll:**
    - **Paris enregistrés:** {total_paris}
    - **Solde actuel:** {int(solde):,} FCFA
    - **Profit:** <span class="{profit_color}">{int(profit):,} FCFA</span>
""", unsafe_allow_html=True)

# Bouton pour afficher les statistiques détaillées
if st.sidebar.button("📈 Afficher statistiques complètes"):
    afficher_statistiques()

# Paramètres d'analyse
st.sidebar.title("⚙️ Paramètres d'analyse")
min_confidence = st.sidebar.slider(
    "Confiance minimale requise",
    min_value=1,
    max_value=5,
    value=3,
    help="Filtre les paris selon leur indice de confiance"
)
min_prob = st.sidebar.slider(
    "Probabilité minimale requise (%)",
    min_value=50,
    max_value=90,
    value=60,
    step=5
)
max_bet_percent = st.sidebar.slider(
    "Mise maximale (% bankroll)",
    min_value=1,
    max_value=10,
    value=5,
    step=1
)

# Section principale
tab1, tab2 = st.tabs(["🎯 Value Bets du jour", "📚 Historique complet"])

with tab1:
    st.header("🔍 Analyse des matchs du jour")
    st.markdown("""
        Notre algorithme scanne les matchs et identifie les **value bets** - 
        paris où la cote proposée est supérieure à la probabilité réelle.
    """)

    if st.button("🚀 Lancer l'analyse des matchs", type="primary"):
        with st.spinner("Recherche des meilleurs paris en cours..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Simulation de chargement
            for percent in range(0, 101, 10):
                time.sleep(0.1)
                progress_bar.progress(percent)
                status_text.text(f"Progression: {percent}%")

            matchs = get_matchs_du_jour()
            progress_bar.empty()
            status_text.empty()

            if not matchs:
                st.warning("⚠️ Aucun match disponible aujourd'hui. Veuillez réessayer plus tard.")
            else:
                value_bets_found = 0
                
                for match in matchs:
                    stats = get_stats_simulees(match)
                    cotes = get_cotes_simulees(stats["forme_home"], stats["forme_away"])
                    proba_home = evaluer_probabilites(stats)
                    proba_away = 1 - proba_home
                    
                    # Détection value bet pour home et away
                    is_value_home = detecter_value_bet(proba_home, cotes["1"])
                    is_value_away = detecter_value_bet(proba_away, cotes["2"])
                    
                    # On prend le meilleur value bet entre home et away
                    if is_value_home or is_value_away:
                        if is_value_home and (proba_home > proba_away):
                            proba = proba_home
                            cote = cotes["1"]
                            prediction = f"Victoire {stats['home']}"
                            is_value = True
                        elif is_value_away:
                            proba = proba_away
                            cote = cotes["2"]
                            prediction = f"Victoire {stats['away']}"
                            is_value = True
                        else:
                            is_value = False
                    else:
                        is_value = False

                    if is_value:
                        etoiles, poids = classer_confiance(proba)
                        mise = calcul_mise_kelly(bankroll, proba, cote, fraction=max_bet_percent/100)
                        
                        # Filtrage selon les paramètres
                        if (etoiles >= min_confidence) and (proba >= min_prob/100):
                            value_bets_found += 1
                            
                            with st.container():
                                st.markdown(f"""
                                    <div class="value-bet">
                                        <h3>⚽ {stats['home']} vs {stats['away']} - {stats['competition']}</h3>
                                        <p><strong>📅 Date:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                                        <p><strong>🧠 Pronostic:</strong> {prediction}</p>
                                        <p><strong>📊 Probabilité estimée:</strong> {int(proba*100)}%</p>
                                        <p><strong>💸 Cote estimée:</strong> {cote:.2f}</p>
                                        <p><strong>🌟 Confiance:</strong> {"⭐" * etoiles}</p>
                                        <p><strong>💰 Valeur attendue:</strong> {(proba * cote - 1)*100:.1f}%</p>
                                        <p><strong>💼 Mise conseillée:</strong> {int(mise):,} FCFA ({mise/bankroll*100:.1f}% bankroll)</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Boutons d'action
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    if st.button(f"✅ Pari gagné - {stats['home']} vs {stats['away']}", key=f"win_{match['id']}"):
                                        mettre_a_jour_bankroll(
                                            f"{stats['home']} vs {stats['away']}",
                                            mise,
                                            "gagné",
                                            cote
                                        )
                                        st.success("Pari enregistré comme gagné!")
                                        st.experimental_rerun()
                                
                                with col2:
                                    if st.button(f"❌ Pari perdu - {stats['home']} vs {stats['away']}", key=f"lose_{match['id']}"):
                                        mettre_a_jour_bankroll(
                                            f"{stats['home']} vs {stats['away']}",
                                            mise,
                                            "perdu",
                                            cote
                                        )
                                        st.error("Pari enregistré comme perdu!")
                                        st.experimental_rerun()
                                
                                with col3:
                                    if st.button(f"➖ Remboursé - {stats['home']} vs {stats['away']}", key=f"push_{match['id']}"):
                                        mettre_a_jour_bankroll(
                                            f"{stats['home']} vs {stats['away']}",
                                            mise,
                                            "remboursé",
                                            cote
                                        )
                                        st.warning("Pari enregistré comme remboursé!")
                                        st.experimental_rerun()
                                
                                st.divider()

                if value_bets_found == 0:
                    st.info("ℹ️ Aucun value bet ne correspond à vos critères actuels. Modifiez les paramètres ou réessayez plus tard.")
                else:
                    st.success(f"🎉 {value_bets_found} value bets trouvés correspondant à vos critères!")
                    if any(proba >= 0.75 for proba in [proba_home, proba_away]):
                        st.balloons()

with tab2:
    st.header("📜 Historique des analyses")
    st.markdown("Consultez l'historique complet de vos analyses et paris")
    afficher_statistiques()