"""
Integrated Stock Risk Calculator - Streamlit App (Two Tabs)
-----------------------------------------------------------
Save this file as `stock_risk_calculator_streamlit.py` and run:

    pip install streamlit pandas numpy matplotlib
    streamlit run stock_risk_calculator_streamlit.py

Features:
- Tab 1: Investment-based Risk & Reward Calculator (enter total money to invest)
- Tab 2: Position Sizing by Risk Limit (enter max acceptable risk in PKR or % of capital)
- Tabs share values (auto-import last calculation); missing inputs are requested interactively
- Graphs: P&L line, Risk vs Reward bar, Position size visualization
- CSV export and session trade log
- Designed for Pakistani traders (PKR) with clear UI and guidance
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

st.set_page_config(page_title="Stock Risk Calculator (Integrated)", layout="wide")

# ---------------- Helper functions ----------------

def calc_shares_from_investment(total_investment, current_price):
    if current_price <= 0:
        return 0
    return int(total_investment // current_price)


def calc_shares_by_risk(max_risk, entry_price, stop_loss):
    risk_per_share = entry_price - stop_loss
    if risk_per_share <= 0:
        return 0, risk_per_share
    shares = int(np.floor(max_risk / risk_per_share))
    return shares, risk_per_share


def calc_metrics(entry_price, stop_loss, target_price, shares, commission=0.0, slippage=0.0):
    risk_per_share = entry_price - stop_loss
    profit_per_share = target_price - entry_price

    # Include commission/slippage into effective per-share cost for conservative calc
    adj_risk_per_share = risk_per_share + commission + slippage
    adj_profit_per_share = profit_per_share - commission - slippage

    total_risk = adj_risk_per_share * shares
    total_profit = adj_profit_per_share * shares

    reward_risk_ratio = None
    if adj_risk_per_share > 0:
        reward_risk_ratio = round(adj_profit_per_share / adj_risk_per_share, 3)

    return {
        'risk_per_share': risk_per_share,
        'adj_risk_per_share': adj_risk_per_share,
        'profit_per_share': profit_per_share,
        'adj_profit_per_share': adj_profit_per_share,
        'total_risk': total_risk,
        'total_profit': total_profit,
        'reward_risk_ratio': reward_risk_ratio
    }


def format_pkr(x):
    return f"PKR {x:,.2f}"

# ---------------- Session storage helpers ----------------

if 'last_trade' not in st.session_state:
    st.session_state['last_trade'] = None

if 'trade_log' not in st.session_state:
    st.session_state['trade_log'] = []

# ---------------- UI ----------------

st.title("📊 Integrated Stock Risk Calculator")
st.markdown("Two modules in one app: Investment-based calculations and Risk-based position sizing. Values entered in one tab can be imported into the other.")

# Create tabs
tab1, tab2 = st.tabs(["💵 Investment-based Calculator", "🧮 Position Sizing by Risk Limit"])

# ---------------- Tab 1: Investment-based Calculator ----------------
with tab1:
    st.header("💵 Investment-based Risk & Reward Calculator")
    col1, col2 = st.columns([2,2])

    with col1:
        stock_name = st.text_input("Stock name / symbol", value=(st.session_state['last_trade']['Stock'] if st.session_state['last_trade'] else "PSX:ABC"))
        total_investment = st.number_input("Total amount to invest (PKR)", min_value=0.0, value=(st.session_state['last_trade']['Investment'] if st.session_state['last_trade'] else 50000.0), step=100.0)
        current_price = st.number_input("Current/Entry Price (PKR)", min_value=0.0, value=(st.session_state['last_trade']['Current Price'] if st.session_state['last_trade'] else 150.0), step=0.1)
        commission = st.number_input("Commission per share (est., PKR)", min_value=0.0, value=0.0, step=0.01)
        slippage = st.number_input("Slippage per share (est., PKR)", min_value=0.0, value=0.0, step=0.01)

    with col2:
        stop_loss = st.number_input("Stop Loss Price (PKR)", min_value=0.0, value=(st.session_state['last_trade']['Stop Loss'] if st.session_state['last_trade'] else 140.0), step=0.1)
        target_price = st.number_input("Target Price (PKR)", min_value=0.0, value=(st.session_state['last_trade']['Target Price'] if st.session_state['last_trade'] else 180.0), step=0.1)
        max_position_pct = st.number_input("Max % of portfolio to use for this position (0 = no cap)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

    # Calculations
    shares = calc_shares_from_investment(total_investment, current_price)
    required_investment = shares * current_price

    metrics = calc_metrics(current_price, stop_loss, target_price, shares, commission, slippage)

    # Display key results
    st.markdown("---")
    st.subheader("Results")
    colA, colB, colC = st.columns(3)
    colA.metric("Calculated Shares", f"{shares}")
    colB.metric("Required Investment", format_pkr(required_investment))
    colC.metric("Total Risk (if stop hit)", format_pkr(metrics['total_risk']))

    colD, colE, colF = st.columns(3)
    colD.metric("Risk per Share", format_pkr(metrics['risk_per_share']))
    colE.metric("Total Profit (if target hit)", format_pkr(metrics['total_profit']))
    if metrics['reward_risk_ratio'] is not None:
        colF.success(f"Reward:Risk = {metrics['reward_risk_ratio']} : 1")
    else:
        colF.info("Reward:Risk = N/A")

    if max_position_pct > 0:
        cap_amount = (max_position_pct/100.0) * total_investment
        allowed_shares = int(np.floor(cap_amount / current_price))
        if shares > allowed_shares:
            st.warning(f"Shares reduced to {allowed_shares} to respect your max {max_position_pct}% portfolio rule.")
            shares = allowed_shares
            required_investment = shares * current_price
            metrics = calc_metrics(current_price, stop_loss, target_price, shares, commission, slippage)

    # Summary table
    summary = {
        'Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Stock': stock_name,
        'Investment': total_investment,
        'Current Price': current_price,
        'Stop Loss': stop_loss,
        'Target Price': target_price,
        'Shares': shares,
        'Commission': commission,
        'Slippage': slippage,
        'Total Risk': metrics['total_risk'],
        'Total Profit': metrics['total_profit'],
        'Reward:Risk': metrics['reward_risk_ratio']
    }

    df_summary = pd.DataFrame([summary])
    st.dataframe(df_summary.style.format({
        'Investment':'{:,.2f}','Current Price':'{:,.2f}','Stop Loss':'{:,.2f}','Target Price':'{:,.2f}',
        'Total Risk':'{:,.2f}','Total Profit':'{:,.2f}','Reward:Risk':'{:,.2f}'
    }))

    st.download_button("⬇️ Download this summary (CSV)", df_summary.to_csv(index=False), file_name=f"{stock_name}_summary_{datetime.date.today()}.csv")

    # Save to session as last_trade for import in Tab2
    if st.button("Save values for use in Position Sizing tab"):
        st.session_state['last_trade'] = summary
        st.success("Saved. Switch to the Position Sizing tab to import these values.")

    # P&L Chart
    st.markdown("---")
    st.subheader("Charts")
    col1c, col2c = st.columns([1,1])
    with col1c:
        st.caption("P&L per share line chart")
        prices = np.linspace(min(stop_loss, current_price, target_price) * 0.9, max(stop_loss, current_price, target_price) * 1.1, 300)
        pnl_per_share = prices - current_price
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(prices, pnl_per_share)
        ax.axvline(current_price, linestyle='--', label='Entry')
        ax.axvline(stop_loss, color='red', linestyle='--', label='Stop Loss')
        ax.axvline(target_price, color='green', linestyle='--', label='Target')
        ax.set_xlabel('Price (PKR)')
        ax.set_ylabel('P&L per share (PKR)')
        ax.legend()
        st.pyplot(fig)

    with col2c:
        st.caption('Total risk vs total profit')
        fig2, ax2 = plt.subplots(figsize=(5,3))
        bars = ax2.bar(['Total Risk', 'Total Profit'], [metrics['total_risk'], metrics['total_profit']])
        for bar in bars:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, yval + max(100, abs(yval)*0.01), f"{yval:,.0f}", ha='center', va='bottom')
        st.pyplot(fig2)

    st.markdown("---")
    st.write("Notes: Use the 'Save values' button to transfer these inputs to the Position Sizing tab. Commission and slippage are included conservatively in calculations.")

# ---------------- Tab 2: Position Sizing by Risk Limit ----------------
with tab2:
    st.header("🧮 Position Sizing by Risk Limit")
    st.markdown("Enter the maximum amount you are willing to lose on this trade (in PKR or as a % of your capital). The app will calculate how many shares you can buy so that your loss does not exceed this amount if stop loss is hit.")

    # Try to prefill from last_trade if present
    last = st.session_state['last_trade']

    col1, col2 = st.columns([2,2])
    with col1:
        stock2 = st.text_input("Stock (prefilled from Tab1 if saved)", value=(last['Stock'] if last else "PSX:ABC"))
        entry_price2 = st.number_input("Entry Price (PKR)", min_value=0.0, value=(last['Current Price'] if last else 150.0), step=0.1)
        stop_loss2 = st.number_input("Stop Loss Price (PKR)", min_value=0.0, value=(last['Stop Loss'] if last else 140.0), step=0.1)
        target2 = st.number_input("Target Price (PKR) (for profit projection)", min_value=0.0, value=(last['Target Price'] if last else 180.0), step=0.1)

    with col2:
        capital2 = st.number_input("Capital / Portfolio Value (PKR) — used if choosing % option", min_value=0.0, value=(last['Investment'] if last else 100000.0), step=100.0)

        risk_input_type = st.radio("Specify max risk as:", options=["PKR (absolute)", "% of Capital"], index=0)
        if risk_input_type == "PKR (absolute)":
            max_risk_pk = st.number_input("Max risk (PKR)", min_value=0.0, value=5000.0, step=100.0)
            computed_max_risk = max_risk_pk
        else:
            percent = st.number_input("Max risk % of capital (e.g. enter 2 for 2%)", min_value=0.0, max_value=100.0, value=2.0, step=0.1)
            computed_max_risk = (percent / 100.0) * capital2
            st.write(f"Computed max risk = {format_pkr(computed_max_risk)}")

    # If any required inputs missing, ask user
    missing = []
    if entry_price2 <= 0:
        missing.append('Entry Price')
    if stop_loss2 <= 0:
        missing.append('Stop Loss')
    if computed_max_risk <= 0:
        missing.append('Max Risk')

    if missing:
        st.warning(f"Please provide the following values: {', '.join(missing)}")

    # Calculate shares by risk
    shares_by_risk, raw_risk_per_share = calc_shares_by_risk(computed_max_risk, entry_price2, stop_loss2)

    metrics2 = calc_metrics(entry_price2, stop_loss2, target2, shares_by_risk)
    required_investment2 = shares_by_risk * entry_price2

    st.markdown("---")
    st.subheader("Position Sizing Results")
    col1r, col2r, col3r = st.columns(3)
    col1r.metric("Shares (by risk)", f"{shares_by_risk}")
    col2r.metric("Estimated Investment Required", format_pkr(required_investment2))
    col3r.metric("Total Risk (if stop hit)", format_pkr(metrics2['total_risk']))

    col4r, col5r = st.columns(2)
    col4r.metric("Risk per Share (raw)", format_pkr(raw_risk_per_share))
    if metrics2['reward_risk_ratio'] is not None:
        col5r.success(f"Reward:Risk = {metrics2['reward_risk_ratio']} : 1")
    else:
        col5r.info("Reward:Risk = N/A")

    # Warnings and checks
    st.markdown("---")
    st.subheader("Checks & Guidance")
    if raw_risk_per_share <= 0:
        st.error("Stop Loss must be lower than Entry Price. Cannot compute shares by risk.")
    elif shares_by_risk == 0:
        st.warning("Computed shares is 0 — either max risk is too small or entry-stop difference is too big.")
    else:
        st.success("Position sizing computed. Review investment required and risk before placing the trade.")

    if required_investment2 > capital2:
        st.warning(f"Required investment {format_pkr(required_investment2)} exceeds your capital {format_pkr(capital2)}.")

    # Option to adjust to affordable shares
    if st.button("Adjust shares to fit available capital"):
        affordable_shares = int(np.floor(capital2 / entry_price2))
        shares_by_risk = min(shares_by_risk, affordable_shares)
        metrics2 = calc_metrics(entry_price2, stop_loss2, target2, shares_by_risk)
        required_investment2 = shares_by_risk * entry_price2
        st.success(f"Shares adjusted to {shares_by_risk} (affordable with capital).")

    # Export & save
    summary2 = {
        'Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Stock': stock2,
        'Entry Price': entry_price2,
        'Stop Loss': stop_loss2,
        'Target Price': target2,
        'Shares by Risk': shares_by_risk,
        'Required Investment': required_investment2,
        'Max Risk Used': computed_max_risk,
        'Total Risk': metrics2['total_risk'],
        'Total Profit': metrics2['total_profit'],
        'Reward:Risk': metrics2['reward_risk_ratio']
    }

    df_summary2 = pd.DataFrame([summary2])
    st.dataframe(df_summary2.style.format({
        'Entry Price':'{:,.2f}','Stop Loss':'{:,.2f}','Target Price':'{:,.2f}','Required Investment':'{:,.2f}',
        'Max Risk Used':'{:,.2f}','Total Risk':'{:,.2f}','Total Profit':'{:,.2f}','Reward:Risk':'{:,.2f}'
    }))

    st.download_button("⬇️ Download Position Size Summary (CSV)", df_summary2.to_csv(index=False), file_name=f"position_size_{stock2}_{datetime.date.today()}.csv")

    if st.button("Save this position sizing to session log"):
        st.session_state['trade_log'].append(summary2)
        st.success("Saved to session trade log.")

    # Charts for Tab2
    st.markdown("---")
    st.subheader("Charts: Position Sizing & Risk Visualization")
    c1, c2 = st.columns(2)

    with c1:
        st.caption("Shares by risk and affordable shares visualization")
        bars_x = ['Shares by risk']
        bars_y = [shares_by_risk]
        # affordable
        affordable = int(np.floor(capital2 / entry_price2)) if entry_price2 > 0 else 0
        bars_x.append('Affordable shares')
        bars_y.append(affordable)
        fig3, ax3 = plt.subplots(figsize=(6,3))
        bars = ax3.bar(bars_x, bars_y, color=['orange','blue'])
        for bar in bars:
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{int(bar.get_height())}", ha='center')
        ax3.set_ylabel('Number of shares')
        st.pyplot(fig3)

    with c2:
        st.caption('Projected P&L for computed shares')
        prices = np.linspace(stop_loss2 * 0.95, target2 * 1.05, 200)
        pnl_per_share = prices - entry_price2
        pnl_total = pnl_per_share * shares_by_risk
        fig4, ax4 = plt.subplots(figsize=(6,3))
        ax4.plot(prices, pnl_total)
        ax4.axvline(entry_price2, linestyle='--', label='Entry')
        ax4.axvline(stop_loss2, color='red', linestyle='--', label='Stop')
        ax4.axvline(target2, color='green', linestyle='--', label='Target')
        ax4.set_xlabel('Price (PKR)')
        ax4.set_ylabel('Projected P&L (PKR)')
        ax4.legend()
        st.pyplot(fig4)

# ---------------- Global Trade Log display ----------------
st.markdown("---")
st.header("🗂️ Session Trade Log")
if len(st.session_state['trade_log']) > 0:
    df_log_all = pd.DataFrame(st.session_state['trade_log'])
    st.dataframe(df_log_all)
    st.download_button("⬇️ Download full session trade log (CSV)", df_log_all.to_csv(index=False), file_name=f"trade_log_{datetime.date.today()}.csv")
else:
    st.info("No trades saved to the session log yet. You can save from either tab.")

st.caption("This tool helps with calculations and risk management. It is educational and not financial advice. Always do your own due diligence before placing trades.")
