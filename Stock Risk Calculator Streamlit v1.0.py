import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -------------------------------
# APP CONFIG
# -------------------------------
plt.style.use('dark_background')
st.set_page_config(page_title="📊 Stock Risk Calculator", layout="centered")

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1 style='text-align:center; color:#00FFFF;'>📊 Stock Risk Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Analyze your risk, reward, and position size instantly</p>", unsafe_allow_html=True)
st.divider()

# -------------------------------
# SIDEBAR - INPUTS
# -------------------------------
st.sidebar.header("⚙️ Input Parameters")

currency = st.sidebar.selectbox("Currency", ["PKR", "USD"])
symbol = "₨" if currency == "PKR" else "$"

entry_price = st.sidebar.number_input(f"Entry Price ({symbol})", min_value=0.0, value=150.0, step=0.1)
stop_loss = st.sidebar.number_input(f"Stop Loss ({symbol})", min_value=0.0, value=140.0, step=0.1)
target_price = st.sidebar.number_input(f"Target Price ({symbol})", min_value=0.0, value=165.0, step=0.1)
capital = st.sidebar.number_input(f"Total Capital ({symbol})", min_value=0.0, value=200000.0, step=1000.0)
risk_percent = st.sidebar.slider("Risk per Trade (%)", min_value=0.5, max_value=10.0, value=2.0)

# -------------------------------
# CALCULATIONS
# -------------------------------
risk_per_trade = capital * (risk_percent / 100)
risk_per_share = entry_price - stop_loss
reward_per_share = target_price - entry_price
reward_risk_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
shares = risk_per_trade / risk_per_share if risk_per_share > 0 else 0
total_risk = shares * risk_per_share
potential_profit = shares * reward_per_share

# -------------------------------
# RESULTS SECTION
# -------------------------------
st.subheader("📈 Results")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Shares", value=f"{shares:.2f}")
with col2:
    st.metric(label="Risk / Share", value=f"{symbol} {risk_per_share:.2f}")
with col3:
    st.metric(label="Total Risk", value=f"{symbol} {total_risk:,.2f}")

col4, col5 = st.columns(2)
with col4:
    st.metric(label="Reward / Risk Ratio", value=f"{reward_risk_ratio:.2f}")
with col5:
    st.metric(label="Potential Profit", value=f"{symbol} {potential_profit:,.2f}")

# -------------------------------
# CHART SECTION
# -------------------------------
st.markdown("### 📊 Risk vs Reward Visualization")

fig, ax = plt.subplots(figsize=(6, 3))
bars = ax.bar(["Stop Loss", "Entry", "Target"], [stop_loss, entry_price, target_price],
              color=['#FF4B4B', '#4BC0C0', '#00FF88'])
ax.set_ylabel(f"Price ({symbol})", color='white')
ax.set_title("Trade Setup Overview", color='cyan')
ax.tick_params(colors='white')

for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}",
            ha='center', va='bottom', color='white', fontsize=10)

st.pyplot(fig)

# -------------------------------
# EXPORT FUNCTIONS
# -------------------------------
results_data = {
    "Metric": ["Shares", "Risk/Share", "Total Risk", "Reward/Risk", "Potential Profit"],
    "Value": [f"{shares:.2f}", f"{symbol}{risk_per_share:.2f}",
              f"{symbol}{total_risk:,.2f}", f"{reward_risk_ratio:.2f}",
              f"{symbol}{potential_profit:,.2f}"]
}
df_results = pd.DataFrame(results_data)

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def generate_pdf(df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(180, 800, "Stock Risk Calculator Report")
    c.setFont("Helvetica", 11)
    c.drawString(50, 770, f"Currency: {currency}")
    c.drawString(50, 755, f"Capital: {symbol}{capital:,.2f}")
    c.drawString(50, 740, f"Risk per Trade: {risk_percent:.2f}%")

    y = 700
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Metric")
    c.drawString(250, y, "Value")
    c.line(50, y-2, 400, y-2)
    c.setFont("Helvetica", 11)

    for i, row in df.iterrows():
        y -= 20
        c.drawString(50, y, row["Metric"])
        c.drawString(250, y, row["Value"])

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

csv_data = convert_df_to_csv(df_results)
pdf_data = generate_pdf(df_results)

st.download_button(
    label="⬇️ Download Results (CSV)",
    data=csv_data,
    file_name="stock_risk_results.csv",
    mime="text/csv"
)

st.download_button(
    label="🧾 Download PDF Report",
    data=pdf_data,
    file_name="stock_risk_report.pdf",
    mime="application/pdf"
)

# -------------------------------
# FOOTER
# -------------------------------
st.divider()
st.markdown(
    "<p style='text-align:center; color:gray; font-size:13px;'>© 2025 Stock Risk Calculator v1.2 — Develop By Gul Fayaz Rumi🧠</p>",
    unsafe_allow_html=True
)
