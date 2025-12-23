"""
Transaction Analysis Script
Processes transaction data and generates comprehensive financial visualizations.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter


# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_FILE = "latest_transactions.xlsx"
CSV_OUTPUT = "transactions.csv"
EXCEL_OUTPUT = "formatted_transactions.xlsx"
VISUALS_DIR = "visuals"

# Set up matplotlib for Korean characters (Mac)
plt.rcParams['font.family'] = ['AppleGothic', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

def load_and_clean_data():
    """Load Excel file, clean and standardize the data."""
    print("📊 Loading and cleaning data...")
    
    # Read Excel file
    df = pd.read_excel(INPUT_FILE, sheet_name=0, skiprows=8)
    
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
    df = df.drop(columns=['Unnamed: 0', 'Memo'])
    
    # Fill NA and convert account numbers
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
    
    # Parse datetime and split into Date and Time
    df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d %H:%M:%S')
    df['Time'] = df['Date'].dt.time
    df['Date'] = df['Date'].dt.date
    
    # Reorder columns
    df = df[['Date', 'Time'] + [col for col in df.columns if col not in ['Date', 'Time']]]
    
    # Save to CSV and Excel
    df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8")
    df.to_excel(EXCEL_OUTPUT, index=False)
    
    print(f"✅ Data saved to {CSV_OUTPUT} and {EXCEL_OUTPUT}")
    return df


def prepare_dataframe(csv_path=CSV_OUTPUT):
    """Load CSV and prepare datetime columns."""
    df = pd.read_csv(csv_path)
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df['Transaction_Amount'] = pd.to_numeric(df['Transaction_Amount'])
    df['Month'] = df['DateTime'].dt.to_period('M')
    df['Hour'] = df['DateTime'].dt.hour
    return df


# ============================================================================
# KPI CALCULATION FUNCTIONS
# ============================================================================

def calculate_kpis(df):
    """Calculate key performance indicators."""
    kpis = {
        'current_balance': df['Balance'].iloc[0],
        'total_transactions': len(df),
        'total_deposits': df[df['Transaction_Amount'] > 0]['Transaction_Amount'].sum(),
        'total_withdrawals': abs(df[df['Transaction_Amount'] < 0]['Transaction_Amount'].sum()),
        'total_cashback': df[df['Transaction_Type'] == 'Cashback']['Transaction_Amount'].sum(),
        'total_interest': df[df['Transaction_Type'] == 'Interest Deposit']['Transaction_Amount'].sum()
    }
    
    print("\n=== FINANCIAL KPIs ===")
    print(f"Current Balance: ₩{kpis['current_balance']:,.0f}")
    print(f"Total Deposits: ₩{kpis['total_deposits']:,.0f}")
    print(f"Total Withdrawals: ₩{kpis['total_withdrawals']:,.0f}")
    print(f"Net Flow: ₩{kpis['total_deposits'] - kpis['total_withdrawals']:,.0f}")
    print(f"Total Transactions: {kpis['total_transactions']}")
    print(f"Cashback: ₩{kpis['total_cashback']:,.0f}")
    print(f"Interest: ₩{kpis['total_interest']:,.0f}")
    
    return kpis


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def ensure_visuals_directory():
    """Create visuals directory if it doesn't exist."""
    os.makedirs(VISUALS_DIR, exist_ok=True)


def draw_kpi_dashboard(kpis):
    """Draw KPI dashboard with rounded boxes."""
    print("\n📈 Generating KPI dashboard...")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Configure KPIs: [Label, Value, Color, x, y, width, height]
    kpi_configs = [
        ["TOTAL DEPOSITS", f"₩{kpis['total_deposits']:,.0f}", "#0b5394", 5, 55, 43, 35],
        ["TOTAL WITHDRAWALS", f"₩{kpis['total_withdrawals']:,.0f}", "#990000", 52, 55, 43, 35],
        ["CURRENT BALANCE", f"₩{kpis['current_balance']:,.0f}", "#4682B4", 5, 10, 20, 35],
        ["TX COUNT", f"{kpis['total_transactions']}", "#708090", 28.5, 10, 20, 35],
        ["CASHBACK", f"₩{kpis['total_cashback']:,.0f}", "#DAA520", 52, 10, 20, 35],
        ["INTEREST", f"₩{kpis['total_interest']:,.0f}", "#20B2AA", 75.5, 10, 20, 35],
    ]
    
    for label, val, color, x, y, w, h in kpi_configs:
        # Rounded rectangle background
        p_bbox = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=3",
                                ec="none", fc=color, alpha=0.15)
        ax.add_patch(p_bbox)
        
        # Colored accent bar
        ax.add_patch(plt.Rectangle((x, y), 1.5, h, color=color, alpha=0.8))
        
        # Label and value text
        ax.text(x + 3, y + h - 8, label, fontsize=10, fontweight='bold', color=color, va='top')
        v_size = 18 if len(val) < 12 else 14
        ax.text(x + 3, y + h - 18, val, fontsize=v_size, fontweight='black', color='#333333', va='top')
    
    plt.title("FINANCIAL SUMMARY OVERVIEW", fontsize=16, fontweight='bold', pad=20, loc='left', color='#222222')
    plt.savefig(f'{VISUALS_DIR}/dashboard_kpis.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ KPI dashboard saved")


def plot_cash_flow_pie_chart(df):
    """Generate pie chart showing income vs expenses."""
    print("\n📊 Generating cash flow pie chart...")
    
    total_income = df[df['Transaction_Amount'] > 0]['Transaction_Amount'].sum()
    total_expense = abs(df[df['Transaction_Amount'] < 0]['Transaction_Amount'].sum())
    
    def make_autopct(values):
        def autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f'{pct:.1f}%\n{val:,} KRW'
        return autopct
    
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(
        [total_income, total_expense],
        labels=['Income', 'Expenses'],
        colors=['#0b5394', '#990000'],
        autopct=make_autopct([total_income, total_expense]),
        startangle=90,
        explode=(0.05, 0.05)
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)
    
    ax.set_title('Overall Cash Flow Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{VISUALS_DIR}/cash_flow_pie_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Pie chart saved")


def plot_monthly_income_expenses(df):
    """Generate horizontal bar chart for monthly income vs expenses."""
    print("\n📊 Generating monthly income vs expenses chart...")
    
    income = df[df['Transaction_Amount'] > 0].groupby('Month')['Transaction_Amount'].sum()
    expense = df[df['Transaction_Amount'] < 0].groupby('Month')['Transaction_Amount'].sum().abs()
    
    # Align months
    all_months = sorted(list(set(income.index) | set(expense.index)))
    income = income.reindex(all_months, fill_value=0)
    expense = expense.reindex(all_months, fill_value=0)
    
    # Helper function for bar annotations
    def annotate_bars(ax, bars, color_text):
        max_val = max(b.get_width() for b in bars)
        for bar in bars:
            w = bar.get_width()
            if w == 0:
                continue
            inside = w > max_val * 0.15
            x_pos = w * 0.95 if inside else w + (max_val * 0.02)
            ax.text(x_pos, bar.get_y() + bar.get_height()/2, f'{w:,.0f}',
                   ha='right' if inside else 'left', va='center',
                   color='white' if inside else color_text,
                   fontweight='bold', fontsize=9)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    y, h = np.arange(len(all_months)), 0.35
    
    b1 = ax.barh(y + h/2, income, h, label='Income', color='#0b5394', alpha=0.85)
    b2 = ax.barh(y - h/2, expense, h, label='Expenses', color='#990000', alpha=0.85)
    
    annotate_bars(ax, b1, '#0b5394')
    annotate_bars(ax, b2, '#990000')
    
    ax.set_title('Monthly Income vs Expenses', fontsize=14, fontweight='bold')
    ax.set_yticks(y)
    ax.set_yticklabels([str(m) for m in all_months])
    ax.legend()
    ax.grid(True, alpha=0.2, axis='x')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(f'{VISUALS_DIR}/monthly_income_expenses_bar.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Monthly chart saved")


def plot_transaction_types(df):
    """Generate bar chart showing total amount by transaction type."""
    print("\n📊 Generating transaction types chart...")
    
    transaction_stats = df.groupby('Transaction_Type').agg({
        'Transaction_Amount': ['count', 'sum']
    }).round(0)
    transaction_stats.columns = ['Count', 'Total_Amount']
    
    # Define colors
    type_colors = {
        'Deposit': '#0b5394', 'Withdrawal': '#990000', 'Check Card': '#FF6347',
        'ATM Deposit': '#3CB371', 'KB Bank': '#66CDAA', 'ATM Withdrawal': '#CD5C5C',
        'Open Banking': '#20B2AA', 'Cashback': '#FFD700', 'Interest Deposit': '#48D1CC'
    }
    
    # Sort by absolute amount
    amount_sorted = transaction_stats.copy()
    amount_sorted['Abs_Amount'] = amount_sorted['Total_Amount'].abs()
    amount_sorted = amount_sorted.sort_values('Abs_Amount', ascending=False)
    colors_plot = [type_colors.get(t, '#808080') for t in amount_sorted.index]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars = plt.bar(range(len(amount_sorted)), amount_sorted['Abs_Amount'],
                   color=colors_plot, alpha=0.9, edgecolor='white', linewidth=0.5, width=0.7)
    
    plt.title('Total Amount by Transaction Type', fontsize=18, fontweight='bold', pad=30, color='#333333')
    plt.ylabel('Amount (KRW)', fontsize=12, fontweight='bold', labelpad=15)
    plt.xlabel('Transaction Type', fontsize=12, fontweight='bold', labelpad=15)
    plt.xticks(range(len(amount_sorted)), amount_sorted.index, rotation=45, ha='right', fontsize=10)
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tick_params(axis='both', which='both', length=0)
    plt.grid(axis='y', alpha=0.2, linestyle='--', color='gray')
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Add value labels
    max_val = amount_sorted['Abs_Amount'].max()
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (max_val * 0.01),
                f'{int(height):,}', ha='center', va='bottom',
                fontweight='bold', fontsize=10, color='#444444')
    
    plt.ylim(0, max_val * 1.15)
    plt.tight_layout()
    plt.savefig(f'{VISUALS_DIR}/total_amount_by_type.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Transaction types chart saved")


def plot_monthly_net_income(df):
    """Generate vertical bar chart showing monthly net income (income - expenses)."""
    print("\n📊 Generating monthly net income chart...")
    
    # Calculate monthly income and expenses
    income = df[df['Transaction_Amount'] > 0].groupby('Month')['Transaction_Amount'].sum()
    expense = df[df['Transaction_Amount'] < 0].groupby('Month')['Transaction_Amount'].sum().abs()
    
    # Align months and calculate net income
    all_months = sorted(list(set(income.index) | set(expense.index)))
    income = income.reindex(all_months, fill_value=0)
    expense = expense.reindex(all_months, fill_value=0)
    net_income = income - expense
    
    # Create the bar chart
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Prepare data for plotting
    x_pos = np.arange(len(all_months))
    colors = ['#0b5394' if val >= 0 else '#990000' for val in net_income]
    
    # Create bars
    bars = ax.bar(x_pos, net_income, color=colors, alpha=0.85, width=0.6, edgecolor='white', linewidth=1)
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, net_income)):
        height = bar.get_height()
        label_y = height + (max(abs(net_income)) * 0.03) if height >= 0 else height - (max(abs(net_income)) * 0.03)
        va_align = 'bottom' if height >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2., label_y,
                f'₩{int(val):,}',
                ha='center', va=va_align, fontweight='bold', fontsize=11, color='#333333')
    
    # Styling
    ax.set_title('Monthly Net Income', fontsize=18, fontweight='bold', pad=20)
    ax.set_ylabel('Amount (KRW)', fontsize=14, fontweight='bold', labelpad=10)
    ax.set_xlabel('Month', fontsize=14, fontweight='bold', labelpad=10)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(m) for m in all_months], fontsize=11)
    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.2, alpha=0.7)
    
    # Grid
    ax.grid(True, alpha=0.2, axis='y', linestyle='--')
    ax.set_axisbelow(True)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Format y-axis with commas
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'₩{int(x):,}'))
    
    # Add some padding to y-axis limits
    y_max = max(abs(net_income.min()), abs(net_income.max())) * 1.15
    ax.set_ylim(-y_max, y_max)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#0b5394', label='Net Income'),
                       Patch(facecolor='#990000', label='Net Loss')]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(f'{VISUALS_DIR}/monthly_net_income.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Monthly net income chart saved")


def plot_remarks_analysis(df, is_negative=True):
    """Generate horizontal bar chart for spending/deposits by remarks."""
    if is_negative:
        plot_df = df[df['Transaction_Amount'] < 0].copy()
        plot_df['Value'] = abs(plot_df['Transaction_Amount'])
        title = 'Withdrawals by Remarks'
        color = '#990000'
        filename = 'spending_by_remarks_negative.png'
        xlabel = 'Amount Spent (KRW)'
        label_type = "withdrawal"
    else:
        plot_df = df[df['Transaction_Amount'] >= 0].copy()
        plot_df['Value'] = plot_df['Transaction_Amount']
        title = 'Deposits by Remarks'
        color = '#0b5394'
        filename = 'spending_by_remarks_positive.png'
        xlabel = 'Amount Deposited (KRW)'
        label_type = "deposit"
    
    print(f"📊 Generating {label_type} remarks chart...")
    
    series = plot_df.groupby('Remarks')['Value'].sum().sort_values()
    labels = [str(i)[:50] + '...' if len(str(i)) > 50 else str(i) for i in series.index]
    
    num_items = len(series)
    dynamic_height = max(6, num_items * 0.4)
    
    fig, ax = plt.subplots(figsize=(14, dynamic_height))
    bars = ax.barh(range(num_items), series.values, color=color, alpha=0.8, edgecolor='white')
    
    ax.set_title(title, fontsize=20, fontweight='bold', pad=25)
    ax.set_xlabel(xlabel, fontsize=14, fontweight='bold')
    ax.set_yticks(range(num_items))
    ax.set_yticklabels(labels, fontsize=11)
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)
    
    max_val = series.max() if not series.empty else 1
    for i, v in enumerate(series.values):
        ax.text(v + (max_val * 0.01), i, f'{int(v):,}',
               va='center', fontweight='bold', fontsize=10, color='#333333')
    
    ax.grid(True, alpha=0.2, axis='x', linestyle='--')
    ax.set_xlim(0, max_val * 1.15)
    ax.set_ylim(-0.6, num_items - 0.4)
    
    plt.tight_layout()
    plt.savefig(f'{VISUALS_DIR}/{filename}', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ {label_type.capitalize()} remarks chart saved")

def create_hourly_histogram():
    """Create bar chart histogram of transaction frequency by hour of day."""
    print("📊 Creating hourly transaction histogram...")

    # Read the data
    df = pd.read_csv(CSV_OUTPUT)

    # Combine Date and Time columns, then parse
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df['Hour'] = df['DateTime'].dt.hour

    # Count transactions per hour
    hourly_counts = df['Hour'].value_counts().sort_index()

    # Create histogram
    plt.figure(figsize=(14, 8))
    plt.bar(hourly_counts.index, hourly_counts.values, color='#351c75', alpha=0.7)

    plt.title('Transaction Frequency by Hour of Day', fontsize=16, fontweight='bold')
    plt.xlabel('Hour of Day (24-hour format)', fontsize=14)
    plt.ylabel('Number of Transactions', fontsize=14)

    # Set x-axis to show all 24 hours
    plt.xticks(range(0, 24))
    plt.xlim(-0.5, 23.5)

    # Add value labels on bars
    for i, v in hourly_counts.items():
        plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{VISUALS_DIR}/hourly_transaction_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Hourly histogram saved!")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 60)
    print("TRANSACTION ANALYSIS - STARTING")
    print("=" * 60)
    
    # Step 1: Load and clean data
    load_and_clean_data()
    
    # Step 2: Prepare dataframe for analysis
    df = prepare_dataframe()
    
    # Step 3: Calculate KPIs
    kpis = calculate_kpis(df)
    
    # Step 4: Ensure visuals directory exists
    ensure_visuals_directory()
    
    # Step 5: Generate all visualizations
    draw_kpi_dashboard(kpis)
    plot_cash_flow_pie_chart(df)
    plot_monthly_income_expenses(df)
    plot_monthly_net_income(df)
    plot_transaction_types(df)
    plot_remarks_analysis(df, is_negative=True)
    plot_remarks_analysis(df, is_negative=False)
    create_hourly_histogram()
    
    print("\n" + "=" * 60)
    print("✅ ANALYSIS COMPLETE - All visualizations generated!")
    print("=" * 60)


if __name__ == "__main__":
    main()