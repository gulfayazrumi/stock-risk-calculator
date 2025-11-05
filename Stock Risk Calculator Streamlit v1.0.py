import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =================== PAGE CONFIG =================== #
st.set_page_config(
    page_title="📈 Stock Risk Calculator Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =================== CUSTOM STYLES =================== #
st.markdown("""
    <style>
    body {
        background-color: #0E1117;
        color: #E0E0E0;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #00B4D8;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1C23;
        border-radius: 8px;
        padding: 10px 20px;
        color: #E0E0E0;
        transition: 0.3s;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00B4D8 !important;
        color: black !important;
        font-weight: 700;
    }
    .result-card {
        background-color: #1A1C23;
        padding: 18px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 180, 216, 0.15);
        margin-top: 20px;
    }
    .metric-label {
        color: #A0A0A0;
        font-size: 13px;
        text-transform: uppercase;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 600;
        margin-top: 4px;
    }
    .chart-title {
        color: #00B4D8;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
        text-align: center;
    }
    .stButton>button {
        background-color: #00B4D8;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #0096C7;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# =================== APP TITLE =================== #
st.title("📊 Stock Risk Calculator — Professional Edition")
st.caption("💼 Analyze investment risk, reward, and position sizing with precision and clarity.")

# =================== TABS =================== #
tab1, tab2, tab3 = st.tabs(["💰 Long Trade", "🧮 Risk Position Sizing", "📉 Short Trade"])

# =================== TAB 1: LONG TRADE =================== #
with tab1:
    st.subheader("💵 Long (Buy) Trade Calculator")
    st.markdown("Analyze your **buy-side trade** — when you buy low and sell higher for profit.")

    col1, col2 = st.columns(2)
    with col1:
        total_investment = st.number_input("💰 Total Investment (PKR)", min_value=0.0, step=100.0, format="%.2f")
        entry_price = st.number_input("📈 Entry Price (PKR)", min_value=0.0, step=0.1, format="%.2f")
    with col2:
        stop_loss = st.number_input("📉 Stop Loss (PKR)", min_value=0.0, step=0.1, format="%.2f")
        target_price = st.number_input("🎯 Target Price (PKR)", min_value=0.0, step=0.1, format="%.2f")

    if total_investment and entry_price and stop_loss and target_price:
        shares = total_investment / entry_price if entry_price else 0
        risk_per_share = entry_price - stop_loss
        reward_per_share = target_price - entry_price
        total_risk = risk_per_share * shares
        total_reward = reward_per_share * shares
        reward_risk_ratio = total_reward / total_risk if total_risk != 0 else 0

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("### 📈 Long Trade Results")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown("<div class='metric-label'>Shares</div>", unsafe_allow_html=True)
        c1.markdown(f"<div class='metric-value'>{shares:,.2f}</div>", unsafe_allow_html=True)
        c2.markdown("<div class='metric-label'>Risk/Share</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-value'>PKR {risk_per_share:,.2f}</div>", unsafe_allow_html=True)
        c3.markdown("<div class='metric-label'>Total Risk</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-value'>PKR {total_risk:,.2f}</div>", unsafe_allow_html=True)
        c4.markdown("<div class='metric-label'>Profit</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-value'>PKR {total_reward:,.2f}</div>", unsafe_allow_html=True)
        c5.markdown("<div class='metric-label'>Reward/Risk</div>", unsafe_allow_html=True)
        c5.markdown(f"<div class='metric-value'>{reward_risk_ratio:,.2f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h4 class='chart-title'>📊 Risk vs Reward</h4>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5, 2.8))
        ax.bar(["Total Risk", "Total Profit"], [total_risk, total_reward], color=['#FF4B4B', '#00C853'], alpha=0.9)
        ax.set_ylabel("PKR")
        ax.grid(alpha=0.2)
        st.pyplot(fig)

# =================== TAB 2: POSITION SIZING =================== #
with tab2:
    st.subheader("🧮 Risk-based Position Sizing")
    st.markdown("Calculate the number of shares to buy based on your **risk tolerance** (PKR or %).")

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
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Position Sizing Results")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown("<div class='metric-label'>Allowed Risk</div>", unsafe_allow_html=True)
        c1.markdown(f"<div class='metric-value'>PKR {effective_risk:,.2f}</div>", unsafe_allow_html=True)
        c2.markdown("<div class='metric-label'>Risk/Share</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-value'>PKR {risk_per_share2:,.2f}</div>", unsafe_allow_html=True)
        c3.markdown("<div class='metric-label'>Max Shares</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-value'>{shares_allowed:,.2f}</div>", unsafe_allow_html=True)
        c4.markdown("<div class='metric-label'>Profit</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-value'>PKR {potential_profit:,.2f}</div>", unsafe_allow_html=True)
        c5.markdown("<div class='metric-label'>Reward/Risk</div>", unsafe_allow_html=True)
        c5.markdown(f"<div class='metric-value'>{reward_risk_ratio2:,.2f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h4 class='chart-title'>📉 Risk vs Profit</h4>", unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(5, 2.8))
        ax2.bar(["Risk", "Profit"], [effective_risk, potential_profit], color=['#FF1744', '#00E676'], alpha=0.9)
        ax2.set_ylabel("PKR")
        ax2.grid(alpha=0.2)
        st.pyplot(fig2)

# =================== TAB 3: SHORT TRADE =================== #
with tab3:
    st.subheader("📉 Short (Sell First) Trade Calculator")
    st.markdown("Analyze a **short-side trade** — when you sell high and aim to buy back lower.")

    col1, col2 = st.columns(2)
    with col1:
        total_investment_short = st.number_input("💰 Total Investment (PKR)", min_value=0.0, step=100.0, format="%.2f", key="short_inv")
        entry_price_short = st.number_input("📉 Entry Price (Sell)", min_value=0.0, step=0.1, format="%.2f", key="short_entry")
    with col2:
        stop_loss_short = st.number_input("🛑 Stop Loss (PKR)", min_value=0.0, step=0.1, format="%.2f", key="short_stop")
        target_price_short = st.number_input("🎯 Target Buyback Price (PKR)", min_value=0.0, step=0.1, format="%.2f", key="short_target")

    if total_investment_short and entry_price_short and stop_loss_short and target_price_short:
        shares_short = total_investment_short / entry_price_short if entry_price_short else 0
        risk_per_share_short = stop_loss_short - entry_price_short
        reward_per_share_short = entry_price_short - target_price_short
        total_risk_short = risk_per_share_short * shares_short
        total_reward_short = reward_per_share_short * shares_short
        reward_risk_ratio_short = total_reward_short / total_risk_short if total_risk_short != 0 else 0

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("### 📉 Short Trade Results")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown("<div class='metric-label'>Shares</div>", unsafe_allow_html=True)
        c1.markdown(f"<div class='metric-value'>{shares_short:,.2f}</div>", unsafe_allow_html=True)
        c2.markdown("<div class='metric-label'>Risk/Share</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-value'>PKR {risk_per_share_short:,.2f}</div>", unsafe_allow_html=True)
        c3.markdown("<div class='metric-label'>Total Risk</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-value'>PKR {total_risk_short:,.2f}</div>", unsafe_allow_html=True)
        c4.markdown("<div class='metric-label'>Profit</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-value'>PKR {total_reward_short:,.2f}</div>", unsafe_allow_html=True)
        c5.markdown("<div class='metric-label'>Reward/Risk</div>", unsafe_allow_html=True)
        c5.markdown(f"<div class='metric-value'>{reward_risk_ratio_short:,.2f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h4 class='chart-title'>📊 Short Trade — Risk vs Reward</h4>", unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(5, 2.8))
        ax3.bar(["Total Risk", "Total Profit"], [total_risk_short, total_reward_short], color=['#FF4B4B', '#00E676'], alpha=0.9)
        ax3.set_ylabel("PKR")
        ax3.grid(alpha=0.2)
        st.pyplot(fig3)
