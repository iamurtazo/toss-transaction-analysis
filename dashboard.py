"""
Transaction Analysis Dashboard
Interactive Streamlit dashboard for visualizing financial transaction data.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="Transaction Analysis Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #f8f9fa;
        border-left: 4px solid #0b5394;
        padding: 1.5rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
    }
    .insight-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
    }
    .insight-text {
        font-size: 1rem;
        color: #444;
        line-height: 1.6;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        background-color: #0b5394;
        color: white;
        font-weight: 600;
    }
    .divider {
        margin: 3rem 0;
        border-top: 2px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

@st.cache_data
def load_and_process_data(uploaded_file):
    """Load and process the uploaded Excel file."""
    # Read Excel file
    df = pd.read_excel(uploaded_file, sheet_name=0, skiprows=8)
    
    # Rename columns to English
    df = df.rename(columns={
        '거래 일시': 'Date',
        '적요': 'Remarks',
        '거래 유형': 'Transaction_Type',
        '거래 기관': 'Bank_Name',
        '계좌번호': 'Account_Number',
        '거래 금액': 'Transaction_Amount',
        '거래 후 잔액': 'Balance',
        '메모': 'Memo'
    })
    
    # Drop unnecessary columns
    df = df.drop(columns=['Unnamed: 0', 'Memo'], errors='ignore')
    df["Account_Number"] = df["Account_Number"].fillna(0).astype(int)
    
    # Translate transaction types
    df['Transaction_Type'] = df['Transaction_Type'].replace({
        '체크카드결제': 'Check Card',
        '입금': 'Deposit',
        '출금': 'Withdrawal',
        '프로모션입금': 'Cashback',
        '오픈뱅킹': 'Open Banking',
        '이자입금': 'Interest Deposit',
        'ATM출금': 'ATM Withdrawal',
        'KB국민은행': 'KB Bank',
        'BC카드': 'ATM Deposit'
    })
    
    # Parse dates
    df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d %H:%M:%S')
    df['Time'] = df['Date'].dt.time
    df['DateTime'] = df['Date']
    df['Date'] = df['Date'].dt.date
    df['Year'] = pd.to_datetime(df['DateTime']).dt.year
    df['Month'] = pd.to_datetime(df['DateTime']).dt.month
    df['MonthYear'] = pd.to_datetime(df['DateTime']).dt.to_period('M')
    
    # Ensure numeric
    df['Transaction_Amount'] = pd.to_numeric(df['Transaction_Amount'], errors='coerce')
    
    return df


def filter_data_by_period(df, year=None, month=None):
    """Filter dataframe by selected year and month."""
    filtered_df = df.copy()
    
    if year and year != "All":
        filtered_df = filtered_df[filtered_df['Year'] == year]
    
    if month and month != "All":
        filtered_df = filtered_df[filtered_df['Month'] == month]
    
    return filtered_df


def calculate_kpis(df):
    """Calculate key performance indicators."""
    total_income = df[df['Transaction_Amount'] > 0]['Transaction_Amount'].sum()
    total_expenses = abs(df[df['Transaction_Amount'] < 0]['Transaction_Amount'].sum())
    net_flow = total_income - total_expenses
    savings_rate = (net_flow / total_income * 100) if total_income > 0 else 0
    avg_transaction = df['Transaction_Amount'].mean()
    total_transactions = len(df)
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_flow': net_flow,
        'savings_rate': savings_rate,
        'avg_transaction': avg_transaction,
        'total_transactions': total_transactions
    }


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_kpi_dashboard(kpis):
    """Create KPI dashboard visualization."""
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis('off')
    
    metrics = [
        ('Total Income', f"₩{kpis['total_income']:,.0f}", '#0b5394'),
        ('Total Expenses', f"₩{kpis['total_expenses']:,.0f}", '#990000'),
        ('Net Flow', f"₩{kpis['net_flow']:,.0f}", '#2E8B57' if kpis['net_flow'] >= 0 else '#DC143C'),
        ('Savings Rate', f"{kpis['savings_rate']:.1f}%", '#9370DB'),
    ]
    
    x_positions = [0.125, 0.375, 0.625, 0.875]
    
    for (label, value, color), x_pos in zip(metrics, x_positions):
        # Background box
        rect = plt.Rectangle((x_pos - 0.11, 0.2), 0.22, 0.6, 
                             facecolor=color, alpha=0.15, transform=ax.transAxes)
        ax.add_patch(rect)
        
        # Value text
        ax.text(x_pos, 0.65, value, transform=ax.transAxes,
                ha='center', va='center', fontsize=18, fontweight='bold', color=color)
        
        # Label text
        ax.text(x_pos, 0.35, label, transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='#555')
    
    return fig


def create_cash_flow_pie(df):
    """Create cash flow pie chart."""
    income = df[df['Transaction_Amount'] > 0]['Transaction_Amount'].sum()
    expenses = abs(df[df['Transaction_Amount'] < 0]['Transaction_Amount'].sum())
    
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['#0b5394', '#990000']
    explode = (0.05, 0.05)
    
    wedges, texts, autotexts = ax.pie([income, expenses], 
                                       labels=['Income', 'Expenses'],
                                       colors=colors, 
                                       autopct='%1.1f%%',
                                       startangle=90, 
                                       explode=explode,
                                       shadow=True)
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    ax.set_title('Overall Cash Flow Distribution', fontsize=14, fontweight='bold', pad=20)
    return fig


def create_monthly_income_expenses(df):
    """Create horizontal bar chart of monthly income vs expenses."""
    df_copy = df.copy()
    df_copy['Month'] = pd.to_datetime(df_copy['DateTime']).dt.to_period('M')
    
    income_data = df_copy[df_copy['Transaction_Amount'] > 0]
    expense_data = df_copy[df_copy['Transaction_Amount'] < 0]
    
    monthly_income = income_data.groupby('Month')['Transaction_Amount'].sum()
    monthly_expenses = expense_data.groupby('Month')['Transaction_Amount'].sum().abs()
    
    months = [str(m) for m in monthly_income.index]
    y = np.arange(len(months))
    height = 0.35
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(months) * 0.4)))
    
    bars1 = ax.barh(y + height/2, monthly_income.values, height,
                    label='Income', color='#0b5394', alpha=0.8)
    bars2 = ax.barh(y - height/2, monthly_expenses.values, height,
                    label='Expenses', color='#990000', alpha=0.8)
    
    # Smart label positioning
    max_income = max(monthly_income.values) if len(monthly_income) > 0 else 1
    max_expense = max(monthly_expenses.values) if len(monthly_expenses) > 0 else 1
    
    for bar in bars1:
        width = bar.get_width()
        if width > max_income * 0.15:
            ax.text(width * 0.95, bar.get_y() + bar.get_height()/2,
                   f'₩{width:,.0f}', ha='right', va='center',
                   color='white', fontweight='bold', fontsize=9)
        else:
            ax.text(width + max_income * 0.02, bar.get_y() + bar.get_height()/2,
                   f'₩{width:,.0f}', ha='left', va='center',
                   color='#0b5394', fontweight='bold', fontsize=9)
    
    for bar in bars2:
        width = bar.get_width()
        if width > max_expense * 0.15:
            ax.text(width * 0.95, bar.get_y() + bar.get_height()/2,
                   f'₩{width:,.0f}', ha='right', va='center',
                   color='white', fontweight='bold', fontsize=9)
        else:
            ax.text(width + max_expense * 0.02, bar.get_y() + bar.get_height()/2,
                   f'₩{width:,.0f}', ha='left', va='center',
                   color='#990000', fontweight='bold', fontsize=9)
    
    ax.set_title('Monthly Income vs Expenses', fontsize=14, fontweight='bold')
    ax.set_xlabel('Amount (KRW)', fontsize=11)
    ax.set_ylabel('Month', fontsize=11)
    ax.set_yticks(y)
    ax.set_yticklabels(months)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    return fig


def create_monthly_net_income(df):
    """Create bar chart of monthly net income."""
    df_copy = df.copy()
    df_copy['Month'] = pd.to_datetime(df_copy['DateTime']).dt.to_period('M')
    
    monthly_net = df_copy.groupby('Month')['Transaction_Amount'].sum()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#2E8B57' if x >= 0 else '#DC143C' for x in monthly_net.values]
    
    bars = ax.bar(range(len(monthly_net)), monthly_net.values, color=colors, alpha=0.7)
    
    ax.set_title('Monthly Net Income', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month', fontsize=11)
    ax.set_ylabel('Net Amount (KRW)', fontsize=11)
    ax.set_xticks(range(len(monthly_net)))
    ax.set_xticklabels([str(m) for m in monthly_net.index], rotation=45)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, monthly_net.values)):
        label_y = val + (max(abs(monthly_net.values)) * 0.02 if val >= 0 else -max(abs(monthly_net.values)) * 0.02)
        ax.text(i, label_y, f'₩{val:,.0f}', ha='center',
               va='bottom' if val >= 0 else 'top', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    return fig


def create_transaction_types(df):
    """Create transaction type analysis chart."""
    transaction_stats = df.groupby('Transaction_Type').agg({
        'Transaction_Amount': ['count', 'sum']
    })
    transaction_stats.columns = ['Count', 'Total_Amount']
    transaction_stats = transaction_stats.sort_values('Count', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(transaction_stats) * 0.4)))
    
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(transaction_stats)))
    bars = ax.barh(range(len(transaction_stats)), transaction_stats['Count'],
                   color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)
    
    ax.set_title('Transaction Count by Type', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of Transactions', fontsize=11)
    ax.set_yticks(range(len(transaction_stats)))
    ax.set_yticklabels(transaction_stats.index, fontsize=10)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, transaction_stats['Count'])):
        ax.text(val + max(transaction_stats['Count']) * 0.01, i, f'{int(val):,}',
               va='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    return fig


def create_spending_by_remarks(df, is_negative=True):
    """Create spending/deposits by remarks chart."""
    if is_negative:
        filtered_df = df[df['Transaction_Amount'] < 0].copy()
        filtered_df['Amount'] = filtered_df['Transaction_Amount'].abs()
        title = 'Top Spending by Remarks (Expenses)'
        color = '#990000'
    else:
        filtered_df = df[df['Transaction_Amount'] > 0].copy()
        filtered_df['Amount'] = filtered_df['Transaction_Amount']
        title = 'Top Income by Remarks (Deposits)'
        color = '#0b5394'
    
    remarks_sum = filtered_df.groupby('Remarks')['Amount'].sum().sort_values(ascending=True).tail(15)
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(remarks_sum) * 0.3)))
    
    bars = ax.barh(range(len(remarks_sum)), remarks_sum.values,
                   color=color, alpha=0.7, edgecolor='darkred' if is_negative else 'darkblue')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Amount (KRW)', fontsize=11)
    ax.set_yticks(range(len(remarks_sum)))
    ax.set_yticklabels(remarks_sum.index, fontsize=9)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, val in enumerate(remarks_sum.values):
        ax.text(val + max(remarks_sum.values) * 0.01, i, f'₩{val:,.0f}',
               va='center', fontweight='bold', fontsize=8)
    
    plt.tight_layout()
    return fig


def create_hourly_histogram(df):
    """Create bar chart histogram of transaction frequency by hour of day."""
    df_copy = df.copy()
    df_copy['Hour'] = pd.to_datetime(df_copy['DateTime']).dt.hour
    hourly_counts = df_copy['Hour'].value_counts().sort_index()
    
    # Create histogram
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.bar(hourly_counts.index, hourly_counts.values, color='#351c75', alpha=0.7)
    
    ax.set_title('Transaction Frequency by Hour of Day', fontsize=16, fontweight='bold')
    ax.set_xlabel('Hour of Day (24-hour format)', fontsize=14)
    ax.set_ylabel('Number of Transactions', fontsize=14)
    
    # Set x-axis to show all 24 hours
    ax.set_xticks(range(0, 24))
    ax.set_xlim(-0.5, 23.5)
    
    # Add value labels on bars
    for i, v in hourly_counts.items():
        ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    # Header
    st.markdown('<p class="main-header">💰 Transaction Analysis Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive financial insights from your transaction data</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader("Upload transactions Excel file", type=['xlsx', 'xls'])
        
        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            
            # Load data
            df = load_and_process_data(uploaded_file)
            
            st.header("📅 Time Period Filter")
            
            # Year selection
            years = sorted(df['Year'].unique(), reverse=True)
            current_year = datetime.now().year
            default_year_idx = years.index(current_year) if current_year in years else 0
            
            selected_year = st.selectbox(
                "Select Year",
                ["All"] + years,
                index=default_year_idx + 1 if default_year_idx == 0 else default_year_idx
            )
            
            # Month selection
            if selected_year != "All":
                months_in_year = sorted(df[df['Year'] == selected_year]['Month'].unique())
                current_month = datetime.now().month
                month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                             7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
                
                month_options = ["All"] + [f"{month_names[m]} ({m})" for m in months_in_year]
                
                try:
                    default_month_idx = months_in_year.index(current_month) + 1
                except:
                    default_month_idx = 0
                
                selected_month_str = st.selectbox("Select Month", month_options, index=default_month_idx)
                
                if selected_month_str == "All":
                    selected_month = "All"
                else:
                    selected_month = int(selected_month_str.split('(')[1].strip(')'))
            else:
                selected_month = "All"
            
            # Filter data
            filtered_df = filter_data_by_period(df, selected_year, selected_month)
            
            st.info(f"📊 Analyzing {len(filtered_df)} transactions")
            
            # Calculate KPIs
            kpis = calculate_kpis(filtered_df)
            
        else:
            st.info("👆 Please upload your transaction file to begin")
            return
    
    # Main content area
    if uploaded_file:
        # Display period
        period_str = "All Time"
        if selected_year != "All":
            period_str = f"Year {selected_year}"
            if selected_month != "All":
                period_str += f" - Month {selected_month}"
        
        st.markdown(f"### 📈 Analysis Period: **{period_str}**")
        st.markdown("---")
        
        # 1. KPI Dashboard
        st.markdown("### 🎯 Key Performance Indicators")
        kpi_fig = create_kpi_dashboard(kpis)
        st.pyplot(kpi_fig)
        plt.close()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # 2. Cash Flow Pie Chart
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<p class="insight-title">💵 Overall Cash Flow</p>', unsafe_allow_html=True)
            st.markdown('<p class="insight-text">This visualization shows the proportion of your total income versus expenses. A healthy financial situation typically shows a larger income portion, indicating positive cash flow and savings potential.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Key metrics
            st.metric("Net Flow", f"₩{kpis['net_flow']:,.0f}", 
                     delta=f"{kpis['savings_rate']:.1f}% savings rate")
        
                with col2:
            pie_fig = create_cash_flow_pie(filtered_df)
            st.pyplot(pie_fig)
            plt.close()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # 3. Monthly Income vs Expenses
        col1, col2 = st.columns([1, 1])
                with col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<p class="insight-title">📊 Monthly Income vs Expenses</p>', unsafe_allow_html=True)
            st.markdown('<p class="insight-text">Track your monthly financial flow side-by-side. Blue bars represent income (deposits), while red bars show expenses (withdrawals). Look for patterns where income consistently exceeds expenses for sustainable financial health.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
                with col2:
            monthly_fig = create_monthly_income_expenses(filtered_df)
            st.pyplot(monthly_fig)
            plt.close()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # 4. Monthly Net Income
        col1, col2 = st.columns([1, 1])
                with col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<p class="insight-title">📈 Monthly Net Income Trend</p>', unsafe_allow_html=True)
            st.markdown('<p class="insight-text">This chart displays your net cash flow (income minus expenses) for each month. Green bars indicate months where you saved money, while red bars show months where expenses exceeded income. Use this to identify seasonal patterns or problematic periods.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
                with col2:
            net_fig = create_monthly_net_income(filtered_df)
            st.pyplot(net_fig)
            plt.close()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # 5. Transaction Types
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<p class="insight-title">🔄 Transaction Types Breakdown</p>', unsafe_allow_html=True)
            st.markdown('<p class="insight-text">Understand where your transactions are coming from. This shows the volume of different transaction types like deposits, withdrawals, card payments, and cashback. High card payment counts might indicate opportunities for better cashback rewards.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            types_fig = create_transaction_types(filtered_df)
            st.pyplot(types_fig)
            plt.close()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # 6. Top Expenses
        col1, col2 = st.columns([1, 1])
                with col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<p class="insight-title">💸 Top Spending Categories</p>', unsafe_allow_html=True)
            st.markdown('<p class="insight-text">Your biggest expense categories ranked by total amount spent. This helps identify where most of your money goes and which areas offer the best opportunities for cost reduction or budget optimization.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
                with col2:
            expenses_fig = create_spending_by_remarks(filtered_df, is_negative=True)
            st.pyplot(expenses_fig)
            plt.close()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # 7. Top Income Sources
        col1, col2 = st.columns([1, 1])
                with col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<p class="insight-title">💰 Top Income Sources</p>', unsafe_allow_html=True)
            st.markdown('<p class="insight-text">Your primary sources of income ranked by total received. Understanding your income sources helps with financial planning and identifying your most reliable revenue streams.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
                with col2:
            income_fig = create_spending_by_remarks(filtered_df, is_negative=False)
            st.pyplot(income_fig)
            plt.close()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # 8. Hourly Transaction Pattern
        col1, col2 = st.columns([1, 1])
                with col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown('<p class="insight-title">⏰ Hourly Transaction Patterns</p>', unsafe_allow_html=True)
            st.markdown('<p class="insight-text">Discover when you are most financially active throughout the day. Each bar represents the number of transactions at that hour. This can reveal spending habits like lunch purchases, evening shopping, or payment processing times.</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
                with col2:
            hourly_fig = create_hourly_histogram(filtered_df)
            st.pyplot(hourly_fig)
            plt.close()

# Footer



