# 🚀 interface_app.py
# Interface Streamlit

import streamlit as st
from datetime import datetime
import time
from predict_engine import PredictEngine
from bankroll_manager import BankrollManager

# Initialisation des classes
predict_engine = PredictEngine()
bankroll_manager = BankrollManager()

# Configuration de la page
st.set_page_config(
    page_title="SmartBet Pro AI",
    layout="wide",
    page_icon="⚽"
)

# Style CSS
st.markdown("""
    <style>
        .value-bet {border-left: 5px solid #4CAF50; padding: 1rem; margin-bottom: 1rem;}
        .positive {color: #27ae60;}
        .negative {color: #e74c3c;}
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("⚽🤖 SmartBet Pro AI")
    
    # Sidebar
    with st.sidebar:
        st.title("💰 Gestion Bankroll")
        bankroll = st.number_input("Bankroll (FCFA)", min_value=1000, value=50000, step=500)
        
        total_paris, solde = bankroll_manager.afficher_suivi()
        profit = solde - bankroll
        st.markdown(f"""
            **📊 Statistiques:**
            - Paris: {total_paris}
            - Solde: {int(solde):,} FCFA
            - Profit: <span class="{'positive' if profit >= 0 else 'negative'}">{int(profit):,} FCFA</span>
        """, unsafe_allow_html=True)
        
        st.title("⚙️ Paramètres")
        min_confidence = st.slider("Confiance min", 1, 5, 3)
        min_prob = st.slider("Probabilité min (%)", 50, 90, 60)
    
    # Analyse des matchs
    if st.button("🔍 Analyser les matchs"):
        with st.spinner("Analyse en cours..."):
            time.sleep(1)  # Simulation de chargement
            recommandations = predict_engine.analyser_matchs(bankroll)
            
            if not recommandations:
                st.warning("Aucun value bet trouvé")
            else:
                for reco in recommandations:
                    if (len(reco["confiance"]) >= min_confidence and 
                       (reco["proba"] >= min_prob/100)):
                        with st.container():
                            st.markdown(f"""
                                <div class="value-bet">
                                    <h3>{reco['match']} - {reco['competition']}</h3>
                                    <p>📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                                    <p>🧠 {reco['pronostic']}</p>
                                    <p>📊 Probabilité: {reco['proba']:.0%}</p>
                                    <p>💰 Cote: {reco['cote']:.2f}</p>
                                    <p>🌟 Confiance: {reco['confiance']}</p>
                                    <p>💵 Mise conseillée: {reco['mise']:,.2f} FCFA</p>
                                </div>
                            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()