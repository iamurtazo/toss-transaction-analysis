import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(
    page_title="Toss Bank Transaction Analysis",
    layout="wide"
)

# Title
st.title("💰 Toss Bank Transaction Analysis Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('transactions.csv')
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df['Month'] = df['DateTime'].dt.to_period('M')
    df['Transaction_Amount'] = pd.to_numeric(df['Transaction_Amount'])
    return df

try:
    df = load_data()
    # st.success(f"✅ Data loaded successfully! {len(df)} transactions from {df['DateTime'].min().strftime('%Y-%m-%d')} to {df['DateTime'].max().strftime('%Y-%m-%d')}")
except:
    # st.error("❌ Could not load transactions.csv file. Make sure it exists in the same directory.")
    st.stop()

# Sidebar for navigation
st.sidebar.title("📊 Navigation")
analysis_type = st.sidebar.selectbox(
    "Choose Analysis",
    ["📈 Cash Flow Overview"]
)

#"💸 Monthly Spending by Remarks", "🏦 Transaction Types", "📋 Raw Data"

# Cash Flow Overview
if analysis_type == "📈 Cash Flow Overview":
    st.header("📈 Cash Flow Overview")
    
    # Categorize transactions
    income_types = ['Deposit', 'Cashback', 'Interest Deposit']
    expense_types = ['Withdrawal', 'Check Card', 'ATM Withdrawal']
    
    income_data = df[df['Transaction_Type'].isin(income_types)]
    expense_data = df[df['Transaction_Type'].isin(expense_types)]
    
    # Calculate totals
    total_income = income_data['Transaction_Amount'].sum()
    total_expenses = abs(expense_data['Transaction_Amount'].sum())
    net_flow = total_income - total_expenses
    
    # # Display metrics
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     st.metric("💰 Total Income", f"{total_income:,.0f} KRW")
    # with col2:
    #     st.metric("💸 Total Expenses", f"{total_expenses:,.0f} KRW")
    # with col3:
    #     st.metric("📊 Net Flow", f"{net_flow:,.0f} KRW")
    # with col4:
    #     st.metric("💎 Savings Rate", f"{(net_flow/total_income)*100:.1f}%")
    
    # Monthly trends
    st.subheader("Monthly Trends")
    monthly_income = income_data.groupby('Month')['Transaction_Amount'].sum()
    monthly_expenses = expense_data.groupby('Month')['Transaction_Amount'].sum().abs()
    
    # Create chart
    fig, ax = plt.subplots(figsize=(12, 6))
    months = [str(m) for m in monthly_income.index]
    
    ax.plot(months, monthly_income.values, marker='o', linewidth=3, 
            label='Income', color='#2E8B57')
    ax.plot(months, monthly_expenses.values, marker='s', linewidth=3, 
            label='Expenses', color='#DC143C')
    
    ax.set_title('Monthly Income vs Expenses Trend', fontsize=16, fontweight='bold')
    ax.set_ylabel('Amount (KRW)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Monthly breakdown table
    st.subheader("📋 Monthly Breakdown")
    monthly_data = []
    for month in monthly_income.index:
        income = monthly_income.get(month, 0)
        expenses = monthly_expenses.get(month, 0)
        net = income - expenses
        monthly_data.append({
            'Month': str(month),
            'Income (KRW)': f"{income:,.0f}",
            'Expenses (KRW)': f"{expenses:,.0f}",
            'Net (KRW)': f"{net:,.0f}"
        })
    
    st.dataframe(pd.DataFrame(monthly_data), use_container_width=True)
    
# '''
# # Monthly Spending by Remarks
# elif analysis_type == "💸 Monthly Spending by Remarks":
#     st.header("💸 Monthly Spending by Remarks")
    
#     # Focus on spending (negative amounts)
#     spending_df = df[df['Transaction_Amount'] < 0].copy()
#     spending_df['Amount_Abs'] = spending_df['Transaction_Amount'].abs()
    
#     # Month selector
#     months = sorted(spending_df['Month'].unique())
#     selected_month = st.selectbox("Select Month", [str(m) for m in months])
    
#     # Filter data for selected month
#     month_data = spending_df[spending_df['Month'].astype(str) == selected_month]
    
#     if len(month_data) > 0:
#         # Group by remarks and sum spending
#         monthly_spending = month_data.groupby('Remarks')['Amount_Abs'].sum().sort_values(ascending=False)
        
#         # Show top N categories
#         top_n = st.slider("Number of top categories to show", 5, min(20, len(monthly_spending)), 10)
#         top_spending = monthly_spending.head(top_n)
        
#         # Create horizontal bar chart
#         fig, ax = plt.subplots(figsize=(12, max(8, len(top_spending) * 0.4)))
        
#         bars = ax.barh(range(len(top_spending)), top_spending.values, 
#                        color='#DC143C', alpha=0.7, edgecolor='black', linewidth=0.5)
        
#         ax.set_yticks(range(len(top_spending)))
#         ax.set_yticklabels(top_spending.index, fontsize=10)
#         ax.set_xlabel('Spending Amount (KRW)', fontsize=12, fontweight='bold')
#         ax.set_title(f'Top Spending Categories - {selected_month}', 
#                     fontsize=16, fontweight='bold')
        
#         # Add value labels
#         for i, (bar, value) in enumerate(zip(bars, top_spending.values)):
#             ax.text(value + max(top_spending.values) * 0.01, i, 
#                    f'{value:,.0f}', 
#                    va='center', ha='left', fontsize=9, fontweight='bold')
        
#         ax.grid(axis='x', alpha=0.3, linestyle='--')
#         ax.set_axisbelow(True)
        
#         plt.tight_layout()
#         st.pyplot(fig)
        
#         # Summary stats
#         st.metric("📊 Total Monthly Spending", f"{monthly_spending.sum():,.0f} KRW")
#         st.metric("🏪 Number of Different Merchants", f"{len(monthly_spending)}")
#         st.metric("💳 Number of Transactions", f"{len(month_data)}")
        
#     else:
#         st.warning(f"No spending data found for {selected_month}")

# # # Transaction Types
# elif analysis_type == "🏦 Transaction Types":
#     st.header("🏦 Transaction Type Analysis")
    
#     # Transaction type breakdown
#     transaction_stats = df.groupby('Transaction_Type').agg({
#         'Transaction_Amount': ['count', 'sum', 'mean']
#     }).round(0)
    
#     transaction_stats.columns = ['Count', 'Total_Amount', 'Average_Amount']
    
#     # Calculate percentages
#     total_transactions = df.shape[0]
#     transaction_stats['Percentage'] = (transaction_stats['Count'] / total_transactions * 100).round(1)
    
#     st.subheader("📊 Transaction Summary")
#     st.dataframe(transaction_stats, use_container_width=True)
    
#     # Visualizations
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Transaction Count by Type")
#         fig1, ax1 = plt.subplots(figsize=(8, 6))
#         ax1.bar(transaction_stats.index, transaction_stats['Count'], 
#                 color=['#2E8B57', '#DC143C', '#FF6347', '#4682B4', '#FFD700'][:len(transaction_stats)])
#         ax1.set_title('Transaction Count by Type')
#         ax1.set_ylabel('Number of Transactions')
#         ax1.tick_params(axis='x', rotation=45)
#         plt.tight_layout()
#         st.pyplot(fig1)
    
#     with col2:
#         st.subheader("Total Amount by Type")
#         fig2, ax2 = plt.subplots(figsize=(8, 6))
#         ax2.bar(transaction_stats.index, transaction_stats['Total_Amount'], 
#                 color=['#2E8B57', '#DC143C', '#FF6347', '#4682B4', '#FFD700'][:len(transaction_stats)])
#         ax2.set_title('Total Amount by Type')
#         ax2.set_ylabel('Amount (KRW)')
#         ax2.tick_params(axis='x', rotation=45)
#         plt.tight_layout()
#         st.pyplot(fig2)

# # # Raw Data
# # elif analysis_type == "📋 Raw Data":
#     st.header("📋 Raw Transaction Data")
    
#     # Filters
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         transaction_types = st.multiselect("Transaction Types", 
#                                          df['Transaction_Type'].unique(), 
#                                          default=df['Transaction_Type'].unique())
    
#     with col2:
#         date_range = st.date_input("Date Range", 
#                                   value=[df['DateTime'].min(), df['DateTime'].max()],
#                                   min_value=df['DateTime'].min(),
#                                   max_value=df['DateTime'].max())
    
#     with col3:
#         amount_range = st.slider("Amount Range (KRW)", 
#                                int(df['Transaction_Amount'].min()), 
#                                int(df['Transaction_Amount'].max()),
#                                (int(df['Transaction_Amount'].min()), int(df['Transaction_Amount'].max())))
    
#     # Filter data
#     filtered_df = df[
#         (df['Transaction_Type'].isin(transaction_types)) &
#         (df['DateTime'].dt.date >= date_range[0]) &
#         (df['DateTime'].dt.date <= date_range[1]) &
#         (df['Transaction_Amount'] >= amount_range[0]) &
#         (df['Transaction_Amount'] <= amount_range[1])
#     ]
    
#     st.write(f"Showing {len(filtered_df)} transactions")
#     st.dataframe(filtered_df, use_container_width=True)
    
#     # Download button
#     csv = filtered_df.to_csv(index=False)
#     st.download_button(
#         label="📥 Download filtered data as CSV",
#         data=csv,
#         file_name='filtered_transactions.csv',
#         mime='text/csv',
#     )
# '''
