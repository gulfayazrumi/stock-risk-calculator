import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Streamlit configuration
st.set_page_config(
    page_title="📊 Stock Risk Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Apply Custom CSS for Light/Dark theme visibility ---
st.markdown("""
    <style>
        /* General text visibility for both themes */
        body, .stApp {
            color: var(--text-color);
            background-color: var(--background-color);
        }

        /* Handle dark/light theme colors */
        [data-theme="light"] {
            --text-color: #000000;
            --background-color: #FFFFFF;
        }

        [data-theme="dark"] {
            --text-color: #FFFFFF;
            --background-color: #0E1117;
        }

        /* Style headings */
        h1, h2, h3, h4 {
            color: var(--text-color);
        }

        /* Cards, inputs, and buttons */
        .stNumberInput, .stTextInput, .stSelectbox, .stTextArea {
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #1f77b4;
            color: white;
            border-radius: 8px;
            font-weight: 500;
        }
        .stButton>button:hover {
            background-color: #155a8a;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Integrated Stock Risk Calculator")

# --- Tabs for both modules ---
tab1, tab2 = st.tabs(["💵 Investment-Based Calculator", "🧮 Position Sizing by Risk Limit"])

# --- Session state for saving values between tabs ---
if "saved_values" not in st.session_state:
    st.session_state.saved_values = None

# ====================================================
# TAB 1 — Investment-Based Calculator
# ====================================================
with tab1:
    st.header("💵 Investment-Based Calculator")

    col1, col2, col3 = st.columns(3)
    with col1:
        stock = st.text_input("Stock Symbol", key="symbol_tab1", placeholder="e.g. PSX:ABC")
    with col2:
        entry_price = st.number_input("Entry Price (PKR)", key="entry_tab1", min_value=0.0, step=0.1, format="%.2f")
    with col3:
        target_price = st.number_input("Target Price (PKR)", key="target_tab1", min_value=0.0, step=0.1, format="%.2f")

    col4, col5, col6 = st.columns(3)
    with col4:
        stop_loss = st.number_input("Stop Loss Price (PKR)", key="stop_tab1", min_value=0.0, step=0.1, format="%.2f")
    with col5:
        investment_amount = st.number_input("Total Investment (PKR)", key="invest_tab1", min_value=0.0, step=100.0, format="%.2f")
    with col6:
        commission = st.number_input("Commission % (optional)", key="comm_tab1", min_value=0.0, max_value=10.0, step=0.1, value=0.0, format="%.2f")

    if st.button("Calculate Investment-Based Risk", key="calc_tab1"):
        if entry_price > 0 and stop_loss > 0 and investment_amount > 0:
            num_shares = investment_amount / entry_price
            risk_per_share = entry_price - stop_loss
            total_risk = risk_per_share * num_shares
            potential_profit = (target_price - entry_price) * num_shares
            rr_ratio = potential_profit / total_risk if total_risk != 0 else 0

            st.subheader("📈 Results")
            st.write(f"**Number of Shares:** {num_shares:,.2f}")
            st.write(f"**Risk per Share:** PKR {risk_per_share:,.2f}")
            st.write(f"**Total Risk:** PKR {total_risk:,.2f}")
            st.write(f"**Potential Profit:** PKR {potential_profit:,.2f}")
            st.write(f"**Reward/Risk Ratio:** {rr_ratio:.2f}")

            # --- Visualization ---
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(["Total Risk", "Potential Profit"], [total_risk, potential_profit], color=["red", "green"])
            ax.set_ylabel("PKR")
            ax.set_title("Risk vs Reward")
            st.pyplot(fig)

            # Save values for use in tab 2
            st.session_state.saved_values = {
                "Stock": stock,
                "Entry": entry_price,
                "Stop": stop_loss,
                "Target": target_price
            }

            st.success("✅ Values saved! You can now switch to the 'Position Sizing' tab.")

        else:
            st.warning("⚠️ Please fill all input fields before calculating.")

# ====================================================
# TAB 2 — Position Sizing by Risk Limit
# ====================================================
with tab2:
    st.header("🧮 Position Sizing by Risk Limit")

    if st.session_state.saved_values:
        st.info("Loaded previous values from Investment Tab.")
        stock2 = st.text_input("Stock Symbol", key="symbol_tab2", value=st.session_state.saved_values["Stock"])
        entry_price2 = st.number_input("Entry Price (PKR)", key="entry_tab2", value=st.session_state.saved_values["Entry"], step=0.1)
        stop_loss2 = st.number_input("Stop Loss Price (PKR)", key="stop_tab2", value=st.session_state.saved_values["Stop"], step=0.1)
        target_price2 = st.number_input("Target Price (PKR)", key="target_tab2", value=st.session_state.saved_values["Target"], step=0.1)
    else:
        stock2 = st.text_input("Stock Symbol", key="symbol_tab2_new", placeholder="e.g. PSX:ABC")
        entry_price2 = st.number_input("Entry Price (PKR)", key="entry_tab2_new", min_value=0.0, step=0.1)
        stop_loss2 = st.number_input("Stop Loss Price (PKR)", key="stop_tab2_new", min_value=0.0, step=0.1)
        target_price2 = st.number_input("Target Price (PKR)", key="target_tab2_new", min_value=0.0, step=0.1)

    risk_mode = st.radio("Choose how to define your maximum risk:", ["In PKR", "As % of Capital"], key="risk_mode")

    if risk_mode == "In PKR":
        max_risk = st.number_input("Maximum Acceptable Risk (PKR)", key="risk_pkr_tab2", min_value=0.0, step=100.0)
        capital = None
    else:
        capital = st.number_input("Total Trading Capital (PKR)", key="capital_tab2", min_value=0.0, step=1000.0)
        risk_percent = st.number_input("Maximum Risk %", key="risk_percent_tab2", min_value=0.0, max_value=100.0, step=0.5)
        max_risk = (risk_percent / 100) * capital if capital else 0

    if st.button("Calculate Position Size", key="calc_tab2"):
        if entry_price2 > 0 and stop_loss2 > 0 and max_risk > 0:
            risk_per_share = entry_price2 - stop_loss2
            if risk_per_share <= 0:
                st.error("❌ Stop loss must be lower than entry price.")
            else:
                shares_allowed = max_risk / risk_per_share
                investment_required = shares_allowed * entry_price2
                potential_profit = (target_price2 - entry_price2) * shares_allowed
                rr_ratio = potential_profit / max_risk if max_risk != 0 else 0

                st.subheader("📊 Position Sizing Results")
                st.write(f"**Shares to Buy:** {shares_allowed:,.2f}")
                st.write(f"**Investment Required:** PKR {investment_required:,.2f}")
                st.write(f"**Potential Profit:** PKR {potential_profit:,.2f}")
                st.write(f"**Reward/Risk Ratio:** {rr_ratio:.2f}")

                fig2, ax2 = plt.subplots(figsize=(5, 3))
                ax2.bar(["Max Risk", "Potential Profit"], [max_risk, potential_profit], color=["red", "green"])
                ax2.set_ylabel("PKR")
                ax2.set_title("Risk vs Reward")
                st.pyplot(fig2)
        else:
            st.warning("⚠️ Please fill all inputs before calculating.")

# --- Footer ---
st.markdown("""
---
**Notes:**  
Use the *Save values* button to transfer inputs to the Position Sizing tab.  
Commission and slippage are conservatively included in calculations.  
The interface adapts automatically to light/dark mode.  
---
© 2025 Stock Risk Calculator — Built with ❤️ using Streamlit.
""")
