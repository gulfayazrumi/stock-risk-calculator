"""
Stock Risk Calculator — v2.1 (Fixed Light Theme + Default Dark Mode)
Save as: stock_risk_calculator_v2_1.py
Run: streamlit run stock_risk_calculator_v2_1.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

st.set_page_config(page_title="Stock Risk Calculator v2.1", layout="wide", initial_sidebar_state="expanded")

# -------------------------
# Helper utilities
# -------------------------
def to_float(x):
    try:
        if not x:
            return None
        s = str(x).replace(",", "").replace("PKR", "").strip()
        return float(s)
    except Exception:
        return None

def format_pkr(x):
    if x is None:
        return "-"
    return f"PKR {x:,.2f}"

def compute_reward_risk(profit_per_share, risk_per_share):
    if profit_per_share is None or risk_per_share is None or risk_per_share == 0:
        return None
    return round(profit_per_share / risk_per_share, 2)

def safe_shares_from_investment(total_investment, entry_price):
    if not total_investment or not entry_price or entry_price <= 0:
        return None
    return int(np.floor(total_investment / entry_price))

def safe_shares_by_risk(max_risk, entry_price, stop_loss):
    if not max_risk or not entry_price or not stop_loss:
        return None, None
    risk_per_share = entry_price - stop_loss
    if risk_per_share <= 0:
        return 0, risk_per_share
    shares = int(np.floor(max_risk / risk_per_share))
    return shares, risk_per_share

# -------------------------
# Theme toggle
# -------------------------
theme = st.sidebar.radio("Theme", options=["Dark trader", "Light corporate"], index=0, key="theme_toggle")

if theme == "Dark trader":
    bg_color = "#0E1117"        # background
    panel_color = "#1C1F26"     # card/panel
    text_color = "#EAEAEA"      # readable gray-white
    accent = "#00B386"          # green accent
    plt_style = {"line": "#00B386", "pos": "#00B386", "neg": "#FF4C4C", "neutral": "#888"}
else:
    bg_color = "#F5F7FA"        # soft light gray background
    panel_color = "#FFFFFF"     # white cards
    text_color = "#1E293B"      # navy/gray readable text
    accent = "#2563EB"          # blue accent
    plt_style = {"line": "#2563EB", "pos": "#22C55E", "neg": "#EF4444", "neutral": "#475569"}

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .app-panel {{
            background-color: {panel_color};
            padding: 14px;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }}
        .muted {{
            color: #6B7280;
            font-size: 12px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Session storage
# -------------------------
if "last_trade" not in st.session_state:
    st.session_state.last_trade = None
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

# -------------------------
# Header
# -------------------------
st.markdown("<div class='app-panel'>", unsafe_allow_html=True)
st.markdown(f"### <span style='color:{accent}'>📊 Smart Stock Risk & Position Calculator — v2.1</span>", unsafe_allow_html=True)
st.markdown("<div class='muted'>Two modules: Investment-based and Risk-based. Start with blank fields — app computes only when ready.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💵 Investment-based", "🧮 Position Sizing (Risk Limit)"])

# -------------------------
# TAB 1 — Investment-based
# -------------------------
with tab1:
    st.markdown("<div class='app-panel'>", unsafe_allow_html=True)
    st.subheader("💵 Investment-based Calculator")
    st.markdown("<div class='muted'>Enter values (blank start). Save to Tab 2 when done.</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1,1])
    with c1:
        stock = st.text_input("Stock symbol", value="", placeholder="e.g. PSX:ABC")
        entry_str = st.text_input("Entry price (PKR)", value="", placeholder="e.g. 151.00")
        stop_str = st.text_input("Stop loss (PKR)", value="", placeholder="e.g. 140.00")
    with c2:
        invest_str = st.text_input("Total investment (PKR)", value="", placeholder="e.g. 50,000")
        target_str = st.text_input("Target price (PKR)", value="", placeholder="e.g. 180.00")
        comm_str = st.text_input("Commission per share (optional)", value="", placeholder="e.g. 0.00")

    entry, stop, target, invest, comm = map(to_float, [entry_str, stop_str, target_str, invest_str, comm_str or 0.0])

    shares = safe_shares_from_investment(invest, entry) if invest and entry else None
    risk_per_share = entry - stop if entry and stop else None
    profit_per_share = target - entry if target and entry else None

    adj_risk = (risk_per_share + (comm or 0)) if risk_per_share else None
    adj_profit = (profit_per_share - (comm or 0)) if profit_per_share else None

    total_risk = adj_risk * shares if adj_risk and shares else None
    total_profit = adj_profit * shares if adj_profit and shares else None
    rr_ratio = compute_reward_risk(adj_profit, adj_risk)

    st.markdown("---")
    cA, cB, cC, cD = st.columns(4)
    cA.metric("Shares", f"{shares}" if shares else "-")
    cB.metric("Risk/share", f"{risk_per_share:.2f}" if risk_per_share else "-")
    cC.metric("Profit/share", f"{profit_per_share:.2f}" if profit_per_share else "-")
    cD.metric("Reward : Risk", f"{rr_ratio:.2f}" if rr_ratio else "-")

    st.markdown("---")
    col_graph1, col_graph2 = st.columns([1,1])
    with col_graph1:
        st.caption("📉 Risk vs Profit (compact)")
        fig, ax = plt.subplots(figsize=(5,3))
        labels, values = [], []
        if total_risk:
            labels.append("Total Risk")
            values.append(total_risk)
        if total_profit:
            labels.append("Total Profit")
            values.append(total_profit)
        if values:
            colors = [plt_style["neg"], plt_style["pos"]]
            ax.bar(labels, values, color=colors[:len(values)])
            for i, v in enumerate(values):
                ax.text(i, v + max(1, abs(v)*0.01), f"{v:,.0f}", ha="center", fontsize=9)
            ax.set_ylabel("PKR")
        else:
            ax.text(0.5, 0.5, "Enter inputs to view", ha="center", va="center")
        st.pyplot(fig)

    with col_graph2:
        st.caption("📈 Price vs P&L (compact)")
        fig2, ax2 = plt.subplots(figsize=(5,3))
        if entry and stop and target:
            prices = np.linspace(min(stop, entry, target)*0.95, max(stop, entry, target)*1.05, 120)
            pnl = prices - entry
            ax2.plot(prices, pnl, color=plt_style["line"])
            ax2.axvline(entry, ls="--", color=plt_style["neutral"], label="Entry")
            ax2.axvline(stop, ls="--", color=plt_style["neg"], label="Stop")
            ax2.axvline(target, ls="--", color=plt_style["pos"], label="Target")
            ax2.legend(fontsize=8)
        else:
            ax2.text(0.5, 0.5, "Need entry/stop/target", ha="center", va="center")
        st.pyplot(fig2)

    st.markdown("---")
    if st.button("💾 Save values to Tab 2"):
        st.session_state.last_trade = {"Stock": stock, "Entry": entry, "Stop": stop, "Target": target, "Investment": invest}
        st.success("Saved — open Tab 2.")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# TAB 2 — Position Sizing
# -------------------------
with tab2:
    st.markdown("<div class='app-panel'>", unsafe_allow_html=True)
    st.subheader("🧮 Position Sizing by Risk Limit")
    st.markdown("<div class='muted'>Enter your max risk in PKR or % of capital. Imports data from Tab 1 if saved.</div>", unsafe_allow_html=True)

    last = st.session_state.last_trade or {}
    c1, c2 = st.columns([1,1])
    with c1:
        stock2 = st.text_input("Stock", value=last.get("Stock", ""), placeholder="e.g. PSX:ABC")
        entry2_str = st.text_input("Entry price (PKR)", value=(str(last.get("Entry") or "")))
        stop2_str = st.text_input("Stop loss (PKR)", value=(str(last.get("Stop") or "")))
        target2_str = st.text_input("Target price (PKR)", value=(str(last.get("Target") or "")))
    with c2:
        risk_mode = st.radio("Risk mode", ["PKR (absolute)", "% of capital"])
        if risk_mode == "PKR (absolute)":
            maxrisk_str = st.text_input("Max risk (PKR)", value="", placeholder="e.g. 5000")
            capital_str = pct_str = ""
        else:
            capital_str = st.text_input("Capital (PKR)", value="", placeholder="e.g. 100000")
            pct_str = st.text_input("Risk % of capital", value="", placeholder="e.g. 2")
            maxrisk_str = ""

    entry2, stop2, target2, maxrisk, capital2, pct = map(to_float, [entry2_str, stop2_str, target2_str, maxrisk_str, capital_str, pct_str or 0])

    if risk_mode == "% of capital" and capital2 and pct:
        maxrisk = (pct / 100.0) * capital2

    if entry2 and stop2 and maxrisk:
        shares2, risk_per_share2 = safe_shares_by_risk(maxrisk, entry2, stop2)
        invest2 = shares2 * entry2 if shares2 else None
        profit_per_share2 = target2 - entry2 if target2 and entry2 else None
        total_profit2 = profit_per_share2 * shares2 if profit_per_share2 and shares2 else None
        rr_ratio2 = compute_reward_risk(profit_per_share2, risk_per_share2)

        st.markdown("---")
        cX, cY, cZ, cW = st.columns(4)
        cX.metric("Shares to buy", f"{shares2}")
        cY.metric("Investment (PKR)", format_pkr(invest2))
        cZ.metric("Risk/share", f"{risk_per_share2:.2f}")
        cW.metric("Reward : Risk", f"{rr_ratio2:.2f}" if rr_ratio2 else "-")

        st.markdown("---")
        cG1, cG2 = st.columns(2)
        with cG1:
            st.caption("Position visualization")
            fig3, ax3 = plt.subplots(figsize=(5,3))
            ax3.bar(["Shares"], [shares2], color=plt_style["line"])
            ax3.set_ylabel("Shares")
            st.pyplot(fig3)
        with cG2:
            st.caption("Expected P&L (compact)")
            fig4, ax4 = plt.subplots(figsize=(5,3))
            if entry2 and stop2 and target2:
                prices = np.linspace(stop2*0.95, target2*1.05, 120)
                pnl = (prices - entry2) * shares2
                ax4.plot(prices, pnl, color=plt_style["line"])
                ax4.axhline(0, color=plt_style["neutral"], lw=0.8)
                ax4.axvline(entry2, ls="--", color=plt_style["neutral"])
                ax4.axvline(stop2, ls="--", color=plt_style["neg"])
                ax4.axvline(target2, ls="--", color=plt_style["pos"])
            st.pyplot(fig4)

    st.markdown("</div>", unsafe_allow_html=True)
