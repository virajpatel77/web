# S&P 500 Iron Condor Trading Bot

An advanced Python-based trading bot that analyzes the S&P 500 index and provides optimal strike price recommendations for implementing Iron Condor options strategies.

## 🎯 Features

- **Real-time S&P 500 Data**: Fetches up-to-date historical price data
- **Volatility Analysis**: Comprehensive volatility metrics and regime classification
- **Iron Condor Strategy**: Calculates optimal 4-leg strike prices
- **Strike Price Recommendations**: Data-driven recommendations for all legs
- **Visual Charts**: Beautiful visualizations of market data and strategy
- **Detailed Reports**: HTML, text, and CSV reports for analysis
- **Risk Analysis**: Probability of profit, breakeven points, and risk/reward ratios

## 📊 What is an Iron Condor?

An Iron Condor is a neutral options strategy consisting of four legs:
1. **Buy OTM Put** (lower strike) - Protection
2. **Sell OTM Put** (higher strike) - Income
3. **Sell OTM Call** (lower strike) - Income
4. **Buy OTM Call** (higher strike) - Protection

This creates a credit spread with defined risk and profit potential, ideal for range-bound markets.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone or download this repository:
```bash
cd /home/user/web
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Bot

Simply run the main script:
```bash
python main.py
```

The bot will:
1. Fetch 2 years of S&P 500 historical data
2. Analyze market volatility
3. Calculate optimal Iron Condor strike prices
4. Generate visual charts
5. Create detailed reports (HTML, text, CSV)

## 📁 Project Structure

```
web/
├── main.py                      # Main executable
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── src/                         # Source modules
│   ├── __init__.py
│   ├── data_fetcher.py          # S&P 500 data retrieval
│   ├── volatility_analyzer.py   # Volatility analysis
│   ├── iron_condor_strategy.py  # Strategy calculator
│   ├── visualizer.py            # Chart generation
│   └── report_generator.py      # Report creation
└── output/                      # Generated reports (created at runtime)
    ├── price_history.png
    ├── volatility_analysis.png
    ├── iron_condor_payoff.png
    ├── iron_condor_report.html
    ├── iron_condor_report.txt
    └── strategy_data.csv
```

## 📈 Output Files

After running the bot, you'll find the following files in the `output/` directory:

### Visual Charts
- **price_history.png**: S&P 500 price and volume charts
- **volatility_analysis.png**: Historical volatility analysis with multiple timeframes
- **iron_condor_payoff.png**: Profit/loss diagram showing breakeven points and risk zones

### Reports
- **iron_condor_report.html**: Interactive HTML report with all metrics and embedded charts
- **iron_condor_report.txt**: Detailed text report for easy reading
- **strategy_data.csv**: Historical price data
- **strategy_summary.csv**: Strategy metrics in CSV format

## 🎓 Understanding the Output

### Strike Prices
The bot provides 4 strike prices for the Iron Condor:
```
1. Long Put:    $5,700  (Buy for protection)
2. Short Put:   $5,750  (Sell for credit)
3. Short Call:  $5,950  (Sell for credit)
4. Long Call:   $5,000  (Buy for protection)
```

### Key Metrics

- **Max Profit**: Maximum profit if price stays between short strikes
- **Max Loss**: Maximum loss if price moves beyond long strikes
- **Return on Risk**: Profit potential as percentage of risk
- **Probability of Profit (PoP)**: Statistical probability of making money
- **Breakeven Points**: Upper and lower price points where profit = 0

### Volatility Regimes

- **LOW**: Volatility < 15% - smaller credits, safer environment
- **MODERATE**: 15-25% - ideal for Iron Condors
- **ELEVATED**: 25-35% - higher credits, increased risk
- **HIGH**: > 35% - risky, consider wider strikes

## 🔧 Customization

You can customize the bot behavior by modifying parameters in `main.py`:

```python
# Change lookback period
data = fetcher.fetch_historical_data(period="1y", interval="1d")

# Change days to expiration
strategy = IronCondorStrategy(
    current_price=current_price,
    volatility=volatility,
    days_to_expiration=30  # Default is 45
)

# Change risk profile
strikes = strategy.get_strike_recommendations(risk_profile='conservative')
# Options: 'conservative', 'moderate', 'aggressive'
```

## 📊 Strategy Parameters

The bot uses these default parameters (optimized for balanced trading):

- **Days to Expiration**: 45 days (optimal time decay)
- **Short Strike Delta**: ~0.16 (approximately 84% probability OTM)
- **Wing Width**: $50 (spread between long and short strikes)
- **Expected Move**: 1 standard deviation from current price

## ⚠️ Risk Management Guidelines

1. **Position Sizing**: Never risk more than 2-5% of account on a single trade
2. **Profit Target**: Take profit at 50% of max profit
3. **Stop Loss**: Cut losses at 200% of credit received
4. **Rolling**: Consider rolling if 21 days remain and position is challenged
5. **Monitoring**: Check position daily for breaches of short strikes

## 🔍 How It Works

### 1. Data Collection
- Fetches 2 years of S&P 500 historical data using yfinance
- Calculates daily returns and price statistics

### 2. Volatility Analysis
- Computes historical volatility (annualized)
- Calculates rolling volatility (10, 30, 60-day windows)
- Determines volatility regime and percentile

### 3. Strike Selection
- Uses standard deviation to determine expected move
- Places short strikes at ~1 standard deviation (16 delta)
- Adds protective long strikes for defined risk

### 4. Probability Calculation
- Uses normal distribution to estimate probability of profit
- Calculates standard deviations to breakeven points
- Provides confidence intervals

### 5. Visualization
- Creates comprehensive charts showing price history, volatility, and payoff diagram
- Generates interactive HTML reports with all metrics

## 📚 Educational Resources

To learn more about Iron Condor strategies:
- Options trading basics and Greeks
- Time decay (theta) and how it benefits sellers
- Volatility's impact on options pricing
- Rolling strategies for challenged positions
- Position management and adjustment techniques

## ⚖️ Disclaimer

**THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY**

- Not financial advice
- Options trading involves significant risk
- Past performance does not guarantee future results
- You can lose more than your initial investment
- Consult with a financial advisor before trading
- The authors are not responsible for any trading losses

## 🛠️ Troubleshooting

### "No module named 'yfinance'"
```bash
pip install -r requirements.txt
```

### "Failed to fetch data"
- Check your internet connection
- Yahoo Finance may be temporarily unavailable
- Try again in a few minutes

### Charts not displaying
- Ensure matplotlib is installed correctly
- Check that the output directory is writable

## 📝 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and enhance this bot for your own learning and research.

## 📧 Support

For issues or questions:
- Check the troubleshooting section
- Review the code comments
- Test with different parameters

---

**Remember**: Trading options involves risk. Always use proper risk management and never trade with money you can't afford to lose.

**Happy Trading! 📈**
