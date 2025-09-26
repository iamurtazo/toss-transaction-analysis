# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("📊 Monthly Cash Flow Dashboard")

# Load data
df = pd.read_csv("transactions.csv")

# Parse date and create month column
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df['Month'] = df['DateTime'].dt.to_period('M')

# Categorize transactions
income_types = ['Deposit', 'Cashback', 'Interest Deposit']
expense_types = ['Withdrawal', 'Check Card', 'ATM Withdrawal']

income_data = df[df['Transaction_Type'].isin(income_types)]
expense_data = df[df['Transaction_Type'].isin(expense_types)]

# Calculate monthly totals
monthly_income = income_data.groupby('Month')['Transaction_Amount'].sum()
monthly_expenses = expense_data.groupby('Month')['Transaction_Amount'].sum().abs()

# Function for pie chart labels
def autopct_format(values):
    def inner_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return f"{pct:.1f}%\n{val:,.0f} KRW"
    return inner_autopct

# Let user pick a month
months = monthly_income.index
selected_month = st.selectbox("Select a month", months.astype(str))

# Filter for selected month
income = monthly_income.get(selected_month, 0)
expenses = monthly_expenses.get(selected_month, 0)

if income > 0 or expenses > 0:
    sizes = [income, expenses]
    colors = ['#2E8B57', '#DC143C']  # Green, Red
    labels = ['Income', 'Expenses']

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        colors=colors,
        autopct=autopct_format(sizes),
        startangle=90,
        explode=(0.05, 0.05)
    )
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    ax.set_title(f"Cash Flow - {selected_month}", fontsize=14, fontweight='bold')
    st.pyplot(fig)
else:
    st.info(f"No data available for {selected_month}")
