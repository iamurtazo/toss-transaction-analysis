# 💰 Toss Transaction Dashboard

A comprehensive, interactive financial analysis dashboard built with Streamlit.

## 🚀 Quick Start

### 1. Run the Dashboard

```bash
cd /Users/murtazo/SelfImprovementProjects/toss_analysis
source venv/bin/activate
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### 2. Navigate the Dashboard

The dashboard has 5 main sections:

#### 📊 **Executive Summary**
- Quick financial health overview
- Key metrics: Income, Expenses, Savings, Savings Rate
- AI-generated insights
- Monthly trend visualization
- Complete monthly breakdown table

#### 💰 **Income Analysis**
- Total income overview
- Top income sources (top 15)
- Income stability analysis
- Income concentration metrics
- Monthly income breakdown selector

#### 💸 **Spending Analysis**
- Total spending overview  
- Daily burn rate calculator
- Top spending categories (top 15)
- Most visited merchants
- Weekend vs weekday spending
- Monthly spending breakdown selector

#### ⏱️ **Patterns & Behavior**
- Spending by day of week
- Transaction activity by hour
- Transaction type breakdown
- Cashback & rewards summary
- Peak activity hours

#### 📋 **Raw Data**
- Filterable transaction table
- Search by remarks
- Filter by transaction type
- Amount range slider
- Export to CSV

## ✨ Key Features

### Smart Insights 🤖
The dashboard automatically generates insights:
- Savings performance evaluation
- Top spending/income identification
- Activity level analysis
- Balance trend tracking
- Spending pattern detection

### Interactive Filters 🔍
- Date range selector (All Time, Last Month, Last 3 Months, Custom)
- Transaction type filters
- Search functionality
- Amount range sliders

### Beautiful Visualizations 📊
- Color-coded charts (green for income, red for expenses)
- Value labels on all bars
- Interactive month selectors
- Responsive layouts
- Korean text support

## 📱 Features

✅ **Consolidated Analysis** - All 29 PNG charts now in one interactive dashboard
✅ **Real-time Filtering** - No need to regenerate charts
✅ **Smart Insights** - Automatic interpretation of your data
✅ **Mobile Responsive** - Works on any device
✅ **Easy Navigation** - Sidebar navigation between sections
✅ **Export Functionality** - Download filtered data anytime

## 🎨 What Makes This Better Than Static PNG Files?

| Static PNGs | Interactive Dashboard |
|-------------|----------------------|
| 29 separate files | 1 unified interface |
| No interactivity | Month selectors, filters |
| No insights | AI-generated insights |
| Hard to compare | Easy period comparison |
| No search | Full search & filter |
| Static data | Dynamic updates |

## 💡 Tips for Using the Dashboard

1. **Start with Executive Summary** - Get the big picture first
2. **Use Date Filters** - Focus on specific periods in the sidebar
3. **Drill Down** - Use month selectors to see detailed breakdowns
4. **Export Data** - Download filtered data from Raw Data page
5. **Check Insights** - Read the AI-generated insights for quick takeaways

## 🔄 Updating Data

When you have new transactions:

1. Update `transactions.csv` with new data
2. Refresh the dashboard (it will auto-reload)
3. Or restart: `streamlit run dashboard.py`

## 🎯 Future Enhancements (Optional)

Want to add more features? Consider:
- Budget tracking & alerts
- Expense categorization (Food, Transport, etc.)
- Forecasting future spending
- Goal setting & progress tracking
- Email reports
- Multi-account support

## 🐛 Troubleshooting

**Dashboard won't start?**
```bash
pip install streamlit pandas matplotlib numpy
```

**Korean text not showing?**
- The dashboard uses AppleGothic font (macOS default)
- Charts will still work, just Korean text might appear as boxes

**Data not loading?**
- Ensure `transactions.csv` is in the same directory
- Check CSV format matches expected columns

## 📊 Data Requirements

The dashboard expects `transactions.csv` with these columns:
- `Date` - Transaction date
- `Time` - Transaction time  
- `Remarks` - Merchant/source name
- `Transaction_Type` - Type (Deposit, Withdrawal, etc.)
- `Transaction_Amount` - Amount (positive for income, negative for expenses)
- `Balance` - Account balance after transaction

## 🎉 You're Done!

Your comprehensive transaction dashboard is ready to use. Enjoy exploring your financial data! 💰

---

**Questions or issues?** The dashboard is self-contained and easy to modify. All code is in `dashboard.py`.



