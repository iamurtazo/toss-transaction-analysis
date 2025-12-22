# Transaction Analysis Dashboard

A comprehensive, interactive Streamlit dashboard for visualizing and analyzing financial transaction data.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run dashboard.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`

## 📊 Features

### Data Upload
- Drag and drop your `latest_transactions.xlsx` file
- Automatic data processing and cleaning
- Support for Korean transaction data with English translation

### Time Period Filters
- **Default View**: Current year and current month
- **Year Selection**: Choose specific year or view all years
- **Month Selection**: Filter by specific month (1-12 months per year)
- Real-time filtering updates all visualizations

### 8 Comprehensive Visualizations

1. **Key Performance Indicators (KPIs)**
   - Total Income, Total Expenses, Net Flow, Savings Rate
   - Color-coded metric cards with visual highlights

2. **Overall Cash Flow Pie Chart**
   - Income vs Expenses distribution
   - Percentage breakdown with visual proportions

3. **Monthly Income vs Expenses (Horizontal Bar Chart)**
   - Side-by-side comparison per month
   - Smart label positioning (inside/outside bars)
   - Blue (#0b5394) for income, Red (#990000) for expenses

4. **Monthly Net Income Trend**
   - Green bars for positive months, Red for negative
   - Identifies saving vs overspending patterns

5. **Transaction Types Breakdown**
   - Volume of different transaction categories
   - Deposits, Withdrawals, Card Payments, Cashback, etc.

6. **Top Spending Categories**
   - Top 15 expense sources ranked by amount
   - Identify major cost centers

7. **Top Income Sources**
   - Top 15 income sources ranked by amount
   - Understand revenue streams

8. **Hourly Transaction Patterns (Scatter Plot)**
   - Purple color intensification
   - Bubble size represents transaction volume
   - Discover daily spending habits

## 🎨 Design Features

### Layout
- **Two-column design** inspired by Stack Overflow annual survey
- Left column: Descriptive insights and context
- Right column: Corresponding visualization
- Responsive and professional styling

### Color Scheme
- **Income**: #0b5394 (Blue)
- **Expenses**: #990000 (Dark Red)
- **Positive Net**: #2E8B57 (Green)
- **Negative Net**: #DC143C (Crimson)
- **Hourly Pattern**: Purple gradient (Purples colormap)

### User Experience
- Clean, modern interface
- Informative insight boxes for each visualization
- Real-time filtering without page reload
- Progress indicators and success messages
- Professional metric cards

## 🔧 Technical Details

### Data Processing
- All data processing uses functions from `transactions_analysis.py`
- Cached data loading for performance (`@st.cache_data`)
- Automatic date parsing and type conversion
- Korean to English translation for transaction types

### File Structure
```
toss_analysis/
├── dashboard.py              # Main Streamlit dashboard
├── transactions_analysis.py  # Data processing and analysis logic
├── requirements.txt          # Python dependencies
├── latest_transactions.xlsx  # Upload this file through the UI
└── visuals/                  # Generated visualizations (optional)
```

## 📝 Usage Tips

1. **Default Period**: Dashboard defaults to current year and month for relevant insights
2. **Historical Analysis**: Select "All" for year or month to see full history
3. **Comparison**: Use month filter to compare specific months across years
4. **Export**: Right-click any chart to save as image
5. **Mobile**: Dashboard is responsive and works on tablets/mobile devices

## 🎯 Key Metrics Explained

- **Total Income**: Sum of all positive transactions (deposits)
- **Total Expenses**: Sum of all negative transactions (withdrawals, payments)
- **Net Flow**: Income minus Expenses (your savings/deficit)
- **Savings Rate**: Percentage of income that's saved (Net Flow / Income × 100)

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Run with verbose output
streamlit run dashboard.py --logger.level=debug
```

### File upload fails
- Ensure file is `.xlsx` format (not `.xls`)
- Check that file has 8 header rows to skip
- Verify column names match expected Korean format

### Charts not displaying
- Check browser console for errors
- Try refreshing the page (Ctrl/Cmd + R)
- Clear Streamlit cache: Press 'C' in the terminal running the dashboard

## 🔮 Future Enhancements

- [ ] Download filtered data as CSV/Excel
- [ ] Custom date range selection (beyond monthly)
- [ ] Budget tracking and alerts
- [ ] Year-over-year comparison charts
- [ ] Category-based budget allocation
- [ ] Export dashboard as PDF report

## 📄 License

This dashboard is part of your personal financial analysis toolkit.

---

**Powered by**: Streamlit, Pandas, Matplotlib, NumPy  
**Data Source**: Toss Bank transaction exports


