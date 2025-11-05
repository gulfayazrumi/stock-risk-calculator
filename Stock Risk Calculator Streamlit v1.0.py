import streamlit as st
import matplotlib.pyplot as plt

# --------------------------------
# Streamlit Page Setup
# --------------------------------
st.set_page_config(
    page_title="📊 Stock Risk Calculator",
    page_icon="📈",
    layout="wide"
)

# --- Force Dark Mode Styling ---
st.markdown("""
<style>
    body, .stApp { background-color: #0E1117 !important; color: #FFFFFF !important; }

    h1, h2, h3, h4, h5, h6, p, label, div, span { color: #FFFFFF !important; }

    /* Input fields */
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"], textarea {
        background-color: #262730 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #1f77b4 !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 6px 20px !important;
    }
    .stButton>button:hover { background-color: #155a8a !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1c23 !important;
        color: #FFFFFF !important;
        border-radius: 8px 8px 0 0 !important;
    }
    .stTabs [data-baseweb="tab"]:hover { background-color: #2a2d35 !important; }

    /* KPI boxes */
    .kpi-box {
        background-color: #1a1c23;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #b0b0b0;
    }
    .kpi-value {
        font-size: 1.3rem;
        font-weight: bold;
        color: #FFFFFF;
    }

</style>
""", unsafe_allow_html=True)

st.title("📊 Stock Risk Calculator (Dark Mode)")

tab1, tab2 = st.tabs(["💵 Investment-Based Calculator", "🧮 Position Sizing by Risk Limit"])

if "saved_values" not in st.session_state:
    st.session_state.saved_values = None

# ============================================================
# TAB 1
# ============================================================
with tab1:
    st.header("💵 Investment-Based Calculator")

    c1, c2, c3 = st.columns(3)
    with c1:
        stock = st.text_input("Stock Symbol", key="stock_tab1", placeholder="e.g. PSX:ABC")
    with c2:
        entry_price = st.number_input("Entry Price (PKR)", min_value=0.0, step=0.1, format="%.2f")
    with c3:
        target_price = st.number_input("Target Price (PKR)", min_value=0.0, step=0.1, format="%.2f")

    c4, c5, c6 = st.columns(3)
    with c4:
        stop_loss = st.number_input("Stop Loss (PKR)", min_value=0.0, step=0.1, format="%.2f")
    with c5:
        investment = st.number_input("Investment Amount (PKR)", min_value=0.0, step=100.0, format="%.2f")
    with c6:
        commission = st.number_input("Commission (%)", min_value=0.0, max_value=10.0, step=0.1, value=0.0, format="%.2f")

    st.markdown("---")

    if st.button("Calculate", key="calc1"):
        if entry_price > 0 and stop_loss > 0 and investment > 0:
            shares = investment / entry_price
            risk_share = entry_price - stop_loss
            total_risk = risk_share * shares
            profit = (target_price - entry_price) * shares
            rr = profit / total_risk if total_risk > 0 else 0

            st.subheader("📈 Results")

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f"<div class='kpi-box'><div class='kpi-label'>Shares</div><div class='kpi-value'>{shares:,.2f}</div></div>", unsafe_allow_html=True)
            k2.markdown(f"<div class='kpi-box'><div class='kpi-label'>Risk/Share</div><div class='kpi-value'>PKR {risk_share:,.2f}</div></div>", unsafe_allow_html=True)
            k3.markdown(f"<div class='kpi-box'><div class='kpi-label'>Total Risk</div><div class='kpi-value'>PKR {total_risk:,.2f}</div></div>", unsafe_allow_html=True)
            k4.markdown(f"<div class='kpi-box'><div class='kpi-label'>Reward/Risk</div><div class='kpi-value'>{rr:.2f}</div></div>", unsafe_allow_html=True)

            # --- Compact Chart ---
            fig, ax = plt.subplots(figsize=(3.5, 2.5))
            ax.bar(["Risk", "Reward"], [total_risk, profit], color=["#d62728", "#2ca02c"])
            ax.set_facecolor("#0E1117")
            fig.patch.set_facecolor("#0E1117")
            ax.tick_params(colors="white")
            ax.set_title("Risk vs Reward", color="white", fontsize=10)
            st.pyplot(fig)

            st.session_state.saved_values = {
                "Stock": stock,
                "Entry": entry_price,
                "Stop": stop_loss,
                "Target": target_price
            }

            st.success("✅ Saved for Position Sizing tab.")
        else:
            st.warning("⚠️ Please fill all fields.")

# ============================================================
# TAB 2
# ============================================================
with tab2:
    st.header("🧮 Position Sizing by Risk Limit")

    if st.session_state.saved_values:
        stock2 = st.text_input("Stock Symbol", value=st.session_state.saved_values["Stock"])
        entry2 = st.number_input("Entry Price (PKR)", value=st.session_state.saved_values["Entry"], step=0.1)
        stop2 = st.number_input("Stop Loss (PKR)", value=st.session_state.saved_values["Stop"], step=0.1)
        target2 = st.number_input("Target Price (PKR)", value=st.session_state.saved_values["Target"], step=0.1)
    else:
        stock2 = st.text_input("Stock Symbol", placeholder="e.g. PSX:ABC")
        entry2 = st.number_input("Entry Price (PKR)", min_value=0.0, step=0.1)
        stop2 = st.number_input("Stop Loss (PKR)", min_value=0.0, step=0.1)
        target2 = st.number_input("Target Price (PKR)", min_value=0.0, step=0.1)

    risk_mode = st.radio("Select Risk Mode", ["In PKR", "As % of Capital"])

    if risk_mode == "In PKR":
        max_risk = st.number_input("Max Risk (PKR)", min_value=0.0, step=100.0)
    else:
        capital = st.number_input("Total Capital (PKR)", min_value=0.0, step=1000.0)
        risk_percent = st.number_input("Risk %", min_value=0.0, max_value=100.0, step=0.5)
        max_risk = (risk_percent / 100) * capital if capital else 0

    st.markdown("---")

    if st.button("Calculate", key="calc2"):
        if entry2 > 0 and stop2 > 0 and max_risk > 0:
            risk_per_share = entry2 - stop2
            if risk_per_share <= 0:
                st.error("❌ Stop Loss must be less than Entry Price.")
            else:
                shares_allowed = max_risk / risk_per_share
                invest_req = shares_allowed * entry2
                profit = (target2 - entry2) * shares_allowed
                rr = profit / max_risk if max_risk > 0 else 0

                st.subheader("📊 Position Sizing Results")

                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"<div class='kpi-box'><div class='kpi-label'>Shares</div><div class='kpi-value'>{shares_allowed:,.2f}</div></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='kpi-box'><div class='kpi-label'>Investment</div><div class='kpi-value'>PKR {invest_req:,.2f}</div></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='kpi-box'><div class='kpi-label'>Potential Profit</div><div class='kpi-value'>PKR {profit:,.2f}</div></div>", unsafe_allow_html=True)
                c4.markdown(f"<div class='kpi-box'><div class='kpi-label'>Reward/Risk</div><div class='kpi-value'>{rr:.2f}</div></div>", unsafe_allow_html=True)

                fig2, ax2 = plt.subplots(figsize=(3.5, 2.5))
                ax2.bar(["Max Risk", "Profit"], [max_risk, profit], color=["#d62728", "#2ca02c"])
                ax2.set_facecolor("#0E1117")
                fig2.patch.set_facecolor("#0E1117")
                ax2.tick_params(colors="white")
                ax2.set_title("Risk vs Reward", color="white", fontsize=10)
                st.pyplot(fig2)
        else:
            st.warning("⚠️ Please fill all inputs.")

st.markdown("---")
st.markdown("<p style='text-align:center;color:#888;'>© 2025 Stock Risk Calculator — Develop By Gul Fayaz Rumi</p>", unsafe_allow_html=True)
