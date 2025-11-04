import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Toss Transaction Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Korean font setup for matplotlib
plt.rcParams['font.family'] = ['AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Data loading
@st.cache_data
def load_data():
    """Load and preprocess transaction data"""
    df = pd.read_csv('transactions.csv')
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df['Month'] = df['DateTime'].dt.to_period('M')
    df['Day'] = df['DateTime'].dt.date
    df['DayOfWeek'] = df['DateTime'].dt.day_name()
    df['Hour'] = df['DateTime'].dt.hour
    df['Transaction_Amount'] = pd.to_numeric(df['Transaction_Amount'])
    return df

# Load data
try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    data_loaded = False
    st.stop()

# Categorize transactions
income_types = ['Deposit', 'Cashback', 'Interest Deposit']
expense_types = ['Withdrawal', 'Check Card', 'ATM Withdrawal']

income_data = df[df['Transaction_Type'].isin(income_types)]
expense_data = df[df['Transaction_Type'].isin(expense_types)]

# Sidebar navigation
st.sidebar.markdown("### 💰 Toss Transaction Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["📊 Executive Summary", "💰 Income Analysis", "💸 Spending Analysis", 
     "⏱️ Patterns & Behavior", "📋 Raw Data"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Date filter in sidebar
st.sidebar.markdown("### 📅 Filter by Period")
date_option = st.sidebar.selectbox(
    "Select Period",
    ["All Time", "Last Month", "Last 3 Months", "Custom Range"]
)

if date_option == "Custom Range":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("From", df['DateTime'].min())
    with col2:
        end_date = st.date_input("To", df['DateTime'].max())
    
    filtered_df = df[(df['DateTime'].dt.date >= start_date) & (df['DateTime'].dt.date <= end_date)]
elif date_option == "Last Month":
    last_month = df['DateTime'].max() - timedelta(days=30)
    filtered_df = df[df['DateTime'] >= last_month]
elif date_option == "Last 3 Months":
    last_3_months = df['DateTime'].max() - timedelta(days=90)
    filtered_df = df[df['DateTime'] >= last_3_months]
else:
    filtered_df = df

# Update categorized data based on filter
filtered_income = filtered_df[filtered_df['Transaction_Type'].isin(income_types)]
filtered_expense = filtered_df[filtered_df['Transaction_Type'].isin(expense_types)]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Data Range:** {df['DateTime'].min().strftime('%Y-%m-%d')} to {df['DateTime'].max().strftime('%Y-%m-%d')}")
st.sidebar.markdown(f"**📝 Total Transactions:** {len(filtered_df):,}")

# ============================================================================
# PAGE 1: EXECUTIVE SUMMARY
# ============================================================================
if page == "📊 Executive Summary":
    st.markdown('<p class="main-header">📊 Executive Summary</p>', unsafe_allow_html=True)
    
    # Calculate key metrics
    total_income = filtered_income['Transaction_Amount'].sum()
    total_expenses = abs(filtered_expense['Transaction_Amount'].sum())
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    
    # Hero Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Income",
            value=f"{total_income:,.0f} KRW",
            help="Total deposits, cashback, and interest"
        )
    
    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=f"{total_expenses:,.0f} KRW",
            help="Total withdrawals and card payments"
        )
    
    with col3:
        st.metric(
            label="📈 Net Savings",
            value=f"{net_savings:,.0f} KRW",
            delta=f"{net_savings:,.0f} KRW",
            help="Income minus expenses"
        )
    
    with col4:
        st.metric(
            label="💎 Savings Rate",
            value=f"{savings_rate:.1f}%",
            delta=f"{savings_rate:.1f}%",
            help="Percentage of income saved"
        )
    
    st.markdown("---")
    
    # AI Insights
    st.subheader("🤖 Smart Insights")
    
    # Generate insights
    insights = []
    
    # Insight 1: Savings performance
    if savings_rate > 20:
        insights.append(f"✅ **Excellent savings!** You're saving {savings_rate:.1f}% of your income - well above the recommended 20%.")
    elif savings_rate > 10:
        insights.append(f"👍 **Good savings rate** at {savings_rate:.1f}%. Consider increasing to 20% or more.")
    elif savings_rate > 0:
        insights.append(f"⚠️ **Low savings rate** at {savings_rate:.1f}%. Try to increase your savings.")
    else:
        insights.append(f"🚨 **Warning:** You're spending more than you earn! Negative savings of {net_savings:,.0f} KRW.")
    
    # Insight 2: Top spending
    if len(filtered_expense) > 0:
        top_expense = filtered_expense.groupby('Remarks')['Transaction_Amount'].sum().abs().sort_values(ascending=False)
        if len(top_expense) > 0:
            insights.append(f"💳 **Top spending:** {top_expense.index[0]} ({top_expense.iloc[0]:,.0f} KRW)")
    
    # Insight 3: Top income source
    if len(filtered_income) > 0:
        top_income = filtered_income.groupby('Remarks')['Transaction_Amount'].sum().sort_values(ascending=False)
        if len(top_income) > 0:
            insights.append(f"💰 **Main income source:** {top_income.index[0]} ({top_income.iloc[0]:,.0f} KRW)")
    
    # Insight 4: Transaction frequency
    avg_daily_transactions = len(filtered_df) / max((filtered_df['DateTime'].max() - filtered_df['DateTime'].min()).days, 1)
    insights.append(f"📊 **Activity level:** {avg_daily_transactions:.1f} transactions per day on average")
    
    # Insight 5: Balance trend
    if len(filtered_df) > 0 and 'Balance' in filtered_df.columns:
        start_balance = filtered_df.sort_values('DateTime').iloc[0]['Balance']
        end_balance = filtered_df.sort_values('DateTime').iloc[-1]['Balance']
        balance_change = end_balance - start_balance
        if balance_change > 0:
            insights.append(f"📈 **Balance growing:** Increased by {balance_change:,.0f} KRW in this period")
        elif balance_change < 0:
            insights.append(f"📉 **Balance declining:** Decreased by {abs(balance_change):,.0f} KRW in this period")
    
    # Display insights
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Monthly Trend Chart
    st.subheader("📈 Monthly Income vs Expenses Trend")
    
    monthly_income = filtered_income.groupby('Month')['Transaction_Amount'].sum()
    monthly_expenses = filtered_expense.groupby('Month')['Transaction_Amount'].sum().abs()
    
    if len(monthly_income) > 0 and len(monthly_expenses) > 0:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        months = [str(m) for m in monthly_income.index]
        
        ax.plot(months, monthly_income.values, marker='o', linewidth=3,
                label='Income', color='#198754', markersize=8)
        ax.plot(months, monthly_expenses.values, marker='s', linewidth=3,
                label='Expenses', color='#DC143C', markersize=8)
        
        ax.set_title('Monthly Income vs Expenses Trend', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Amount (KRW)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(axis='x', rotation=45)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No monthly data available for the selected period")
    
    # Monthly Breakdown Table
    st.subheader("📋 Monthly Breakdown")
    
    if len(monthly_income) > 0:
        monthly_data = []
        for month in monthly_income.index:
            income = monthly_income.get(month, 0)
            expenses = monthly_expenses.get(month, 0)
            net = income - expenses
            rate = (net / income * 100) if income > 0 else 0
            monthly_data.append({
                'Month': str(month),
                'Income (KRW)': f"{income:,.0f}",
                'Expenses (KRW)': f"{expenses:,.0f}",
                'Net (KRW)': f"{net:,.0f}",
                'Savings Rate': f"{rate:.1f}%"
            })
        
        st.dataframe(pd.DataFrame(monthly_data), use_container_width=True)
    else:
        st.info("No monthly breakdown available for the selected period")

# Continue with other pages in next message...



