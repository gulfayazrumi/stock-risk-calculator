import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ============ PAGE CONFIG ============ #
st.set_page_config(
    page_title="📈 Stock Risk Calculator",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS for dark theme
st.markdown("""
    <style>
    body {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #0E1117;
    }
    h1, h2, h3, h4, h5 {
        color: #00B4D8;
    }
    .result-box {
        background-color: #1A1C23;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============ MAIN APP ============ #
st.title("📊 Integrated Stock Risk Calculator")
st.caption("💼 Includes both Investment-based and Risk-based calculations — all in one place.")

# Tabs
tab1, tab2 = st.tabs(["💵 Investment-based Calculator", "🧮 Position Sizing by Risk Limit"])

# ============ TAB 1 - INVESTMENT BASED ============ #
with tab1:
    st.header("💵 Investment-based Calculator")

    st.info("Enter your total investment, target price, and stop loss to calculate risk, reward, and potential profit.")

    col1, col2 = st.columns(2)
    with col1:
        total_investment = st.number_input("💰 Total Investment (PKR)", min_value=0.0, step=100.0, format="%.2f")
        entry_price = st.number_input("📈 Entry Price (PKR)", min_value=0.0, step=0.1, format="%.2f")
    with col2:
        stop_loss = st.number_input("📉 Stop Loss Price (PKR)", min_value=0.0, step=0.1, format="%.2f")
        target_price = st.number_input("🎯 Target Price (PKR)", min_value=0.0, step=0.1, format="%.2f")

    if total_investment and entry_price and stop_loss and target_price:
        shares = total_investment / entry_price if entry_price else 0
        risk_per_share = entry_price - stop_loss
        reward_per_share = target_price - entry_price
        total_risk = risk_per_share * shares
        total_reward = reward_per_share * shares
        reward_risk_ratio = total_reward / total_risk if total_risk != 0 else 0

        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
        st.subheader("📈 Results")
        st.write(f"**Shares:** {shares:,.2f}")
        st.write(f"**Risk per Share:** PKR {risk_per_share:,.2f}")
        st.write(f"**Total Risk:** PKR {total_risk:,.2f}")
        st.write(f"**Potential Profit:** PKR {total_reward:,.2f}")
        st.write(f"**Reward/Risk Ratio:** {reward_risk_ratio:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Graph
        st.subheader("📊 Risk vs Reward Chart")
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(["Total Risk", "Total Reward"], [total_risk, total_reward], color=['#FF4B4B', '#00C853'])
        ax.set_ylabel("PKR")
        ax.set_title("Risk & Reward Comparison")
        st.pyplot(fig)

# ============ TAB 2 - POSITION SIZING BY RISK ============ #
with tab2:
    st.header("🧮 Position Sizing by Risk Limit")
    st.info("Enter your maximum acceptable risk (in PKR or %) and the app will calculate how many shares you can buy.")

    col1, col2, col3 = st.columns(3)
    with col1:
        max_risk_pkr = st.number_input("💸 Max Risk (PKR)", min_value=0.0, step=100.0, format="%.2f", key="risk_pkr")
    with col2:
        capital = st.number_input("🏦 Total Capital (PKR)", min_value=0.0, step=1000.0, format="%.2f", key="capital")
    with col3:
        risk_percent = st.number_input("📊 Max Risk (% of Capital)", min_value=0.0, max_value=100.0, step=0.5, format="%.2f", key="risk_pct")

    entry_price2 = st.number_input("📈 Entry Price (PKR)", min_value=0.0, step=0.1, format="%.2f", key="entry2")
    stop_loss2 = st.number_input("📉 Stop Loss (PKR)", min_value=0.0, step=0.1, format="%.2f", key="stop2")
    target_price2 = st.number_input("🎯 Target Price (PKR)", min_value=0.0, step=0.1, format="%.2f", key="target2")

    effective_risk = max_risk_pkr or (capital * (risk_percent / 100))
    risk_per_share2 = entry_price2 - stop_loss2 if entry_price2 and stop_loss2 else 0
    shares_allowed = effective_risk / risk_per_share2 if risk_per_share2 > 0 else 0
    potential_profit = (target_price2 - entry_price2) * shares_allowed if shares_allowed > 0 else 0
    reward_risk_ratio2 = (potential_profit / effective_risk) if effective_risk > 0 else 0

    if effective_risk and entry_price2 and stop_loss2:
        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
        st.subheader("📊 Position Sizing Results")
        st.write(f"**Allowed Risk:** PKR {effective_risk:,.2f}")
        st.write(f"**Risk per Share:** PKR {risk_per_share2:,.2f}")
        st.write(f"**Maximum Shares:** {shares_allowed:,.2f}")
        st.write(f"**Potential Profit:** PKR {potential_profit:,.2f}")
        st.write(f"**Reward/Risk Ratio:** {reward_risk_ratio2:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("📉 Risk Visualization")
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.bar(["Risk", "Profit"], [effective_risk, potential_profit], color=['#FF1744', '#00E676'])
        ax2.set_ylabel("PKR")
        ax2.set_title("Risk vs Profit Potential")
        st.pyplot(fig2)
