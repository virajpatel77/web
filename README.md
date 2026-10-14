# S&P 500 Iron Condor Trading Bot 🤖

An advanced AI-powered Python trading bot that analyzes the S&P 500 index and provides optimal strike price recommendations for implementing Iron Condor options strategies.

## ✨ Features

### Core Features
- **Real-time S&P 500 Data**: Live price streaming with WebSocket support
- **Volatility Analysis**: Comprehensive volatility metrics and regime classification
- **Iron Condor Strategy**: Calculates optimal 4-leg strike prices
- **Strike Price Recommendations**: Data-driven recommendations for all legs
- **Visual Charts**: Beautiful visualizations of market data and strategy
- **Detailed Reports**: HTML, text, and CSV reports for analysis
- **Risk Analysis**: Probability of profit, breakeven points, and risk/reward ratios

### 🆕 Advanced Features
- **🤖 Machine Learning Predictions**:
  - LSTM neural networks for price movement forecasting
  - GARCH models for volatility forecasting
  - AI-powered entry/exit recommendations
  - Confidence-based strike price adjustments

- **📡 Real-time Data Streaming**:
  - Live S&P 500 price updates
  - WebSocket support for instant notifications
  - Fallback to polling for reliability
  - Demo mode for testing

- **💼 Position Tracking**:
  - Track multiple open Iron Condor positions
  - Real-time P&L calculations
  - Trade history logging
  - Portfolio performance metrics
  - Win/loss statistics

- **🌐 Interactive Web Dashboard**:
  - Modern, responsive UI
  - Real-time charts and updates
  - Position management interface
  - ML prediction visualization
  - One-click strategy analysis

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
- 2GB RAM minimum (4GB recommended for ML training)

### Installation

1. Clone or download this repository:
```bash
cd /path/to/web
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Install the multitasking stub (workaround for build issues):
```bash
cat > /tmp/multitasking.py << 'EOF'
"""Stub multitasking module"""
def task(func): return func
def wait_for_tasks(): pass
def createPool(name="default", processes=None): pass
__version__ = "0.0.11"
EOF

# Copy to your Python site-packages
cp /tmp/multitasking.py $(python -c "import site; print(site.getsitepackages()[0])")/multitasking.py
```

**Note**: The bot will automatically use demo data if Yahoo Finance is unavailable

### Running the Bot

#### Option 1: Command-Line Mode
Run the traditional analysis script:
```bash
python main.py
```

This will:
1. Fetch 2 years of S&P 500 historical data
2. Analyze market volatility
3. Calculate optimal Iron Condor strike prices
4. Generate visual charts
5. Create detailed reports (HTML, text, CSV)

#### Option 2: Web Dashboard Mode (Recommended)
Start the web server for the interactive dashboard:
```bash
python run_server.py
```

Then open your browser to:
```
http://localhost:5000
```

Features:
- Real-time price monitoring
- Interactive strategy analysis
- ML predictions and recommendations
- Position tracking and management
- Live charts and visualizations

## 📁 Project Structure

```
web/
├── main.py                      # CLI trading bot
├── run_server.py                # Web server launcher
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── src/                         # Source modules
│   ├── data_fetcher.py          # S&P 500 data retrieval
│   ├── volatility_analyzer.py   # Volatility analysis
│   ├── iron_condor_strategy.py  # Strategy calculator
│   ├── visualizer.py            # Chart generation
│   ├── report_generator.py      # Report creation
│   ├── ml/                      # Machine Learning
│   │   ├── price_predictor.py   # LSTM price prediction
│   │   ├── volatility_predictor.py # GARCH volatility forecasting
│   │   └── ml_engine.py         # ML orchestration
│   ├── streaming/               # Real-time data
│   │   └── price_stream.py      # Live price streaming
│   ├── db/                      # Database & persistence
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # Position & trade models
│   │   └── position_manager.py  # Position tracking
│   └── api/                     # Web API
│       └── app.py               # Flask REST API
├── web/                         # Frontend
│   ├── templates/
│   │   └── dashboard.html       # Dashboard UI
│   └── static/
│       └── dashboard.js         # Dashboard JavaScript
├── models/                      # Trained ML models
└── output/                      # Generated reports
    ├── price_history.png
    ├── volatility_analysis.png
    ├── iron_condor_payoff.png
    ├── iron_condor_report.html
    ├── iron_condor_report.txt
    └── strategy_data.csv
```

## 🎯 Usage Guide

### Web Dashboard

1. **Start the Server**:
   ```bash
   python run_server.py
   ```

2. **Access Dashboard**: Open `http://localhost:5000` in your browser

3. **Train ML Models** (first time):
   - Click "🧠 Train ML Models" button
   - Wait 2-5 minutes for training to complete
   - Models are saved and reused automatically

4. **Analyze Strategy**:
   - Click "🔍 Analyze Strategy"
   - View optimal strike prices, P&L metrics, and ML predictions
   - Get AI-powered recommendations (ENTER, WAIT, AVOID)

5. **Start Live Data**:
   - Click "▶️ Start Live Data"
   - Watch real-time price updates
   - Monitor live P&L on open positions

6. **Manage Positions**:
   - Create positions from analysis results
   - Track multiple open positions
   - Close positions manually or based on ML signals

### API Endpoints

The server exposes a REST API at `http://localhost:5000/api/`:

#### Market Data
- `GET /api/market/current` - Current market data and volatility
- `GET /api/health` - System health check

#### Strategy Analysis
- `POST /api/strategy/analyze` - Analyze Iron Condor strategy
  ```json
  {
    "days_to_expiration": 45
  }
  ```

#### Machine Learning
- `POST /api/ml/train` - Train ML models (takes 2-5 minutes)
- `POST /api/ml/predict` - Get ML predictions

#### Position Management
- `GET /api/positions` - Get all positions
- `GET /api/positions/open` - Get open positions
- `POST /api/positions` - Create new position
- `GET /api/positions/<id>` - Get specific position
- `POST /api/positions/<id>/close` - Close position

#### Portfolio
- `GET /api/portfolio/summary` - Get portfolio metrics

#### Streaming
- `POST /api/streaming/start` - Start real-time price streaming
- `POST /api/streaming/stop` - Stop streaming

### WebSocket Events

Connect to Socket.IO for real-time updates:

```javascript
const socket = io('http://localhost:5000');

socket.on('price_update', (data) => {
  console.log('Price:', data.price);
  console.log('Timestamp:', data.timestamp);
});
```

## 🧠 Machine Learning Models

### Price Prediction Model
- **Architecture**: LSTM (Long Short-Term Memory) neural network
- **Input**: 60 days of historical prices
- **Output**: Price prediction 5 days ahead
- **Fallback**: Moving average-based prediction if TensorFlow unavailable

### Volatility Forecasting Model
- **Architecture**: GARCH (Generalized Autoregressive Conditional Heteroskedasticity)
- **Input**: Daily returns history
- **Output**: Volatility forecast 5 days ahead
- **Fallback**: Simple volatility estimation if arch library unavailable

### ML Recommendations
The bot provides AI-powered recommendations:
- **ENTER**: Good conditions for Iron Condor (neutral price, moderate volatility)
- **WAIT**: Mixed signals, wait for clarity
- **AVOID**: High risk conditions (high volatility, strong directional bias)
- **HOLD**: Maintain existing positions

## 📈 Strategy Parameters

The bot uses these default parameters (optimized for balanced trading):

- **Days to Expiration**: 45 days (optimal time decay)
- **Short Strike Delta**: ~0.16 (approximately 84% probability OTM)
- **Wing Width**: Dynamically calculated based on volatility
- **Expected Move**: Based on current volatility and ML forecasts

### Customization

Modify in `main.py` or via API:

```python
# Change risk profile
strikes = strategy.get_strike_recommendations(risk_profile='conservative')
# Options: 'conservative', 'moderate', 'aggressive'

# Adjust ML model parameters
price_predictor = PricePredictor(lookback=90, forecast_days=10)
vol_predictor = VolatilityPredictor(forecast_horizon=10)
```

## ⚠️ Risk Management Guidelines

1. **Position Sizing**: Never risk more than 2-5% of account on a single trade
2. **Profit Target**: Take profit at 50% of max profit
3. **Stop Loss**: Cut losses at 200% of credit received
4. **Rolling**: Consider rolling if 21 days remain and position is challenged
5. **Monitoring**: Check positions daily for breaches of short strikes
6. **ML Confidence**: Only act on ML recommendations with >70% confidence
7. **Volatility Regime**: Avoid trading in HIGH volatility environments

## 🔧 Troubleshooting

### "TensorFlow not available"
- ML models will use fallback methods (moving averages)
- Install TensorFlow for full ML features: `pip install tensorflow>=2.13.0`

### "Yahoo Finance access denied"
- Bot automatically switches to demo data
- Demo data uses realistic price simulations
- Check internet connection or wait and retry

### Port 5000 already in use
- Change port in `run_server.py`:
  ```python
  app.socketio.run(app, host='0.0.0.0', port=8000)
  ```

### Database errors
- Delete `trading_bot.db` to reset database
- Run `python -c "from src.db.database import init_db; init_db()"`

## 📊 Sample Output

### Command-Line Mode
```
✓ Successfully retrieved 504 days of data
  Current S&P 500 Price: $6506.64
  Volatility: 17.76%
  Volatility Regime: MODERATE

✓ Iron Condor Strategy Calculated
  STRIKE PRICES (All 4 Legs):
  1. Long Put:    $6050
  2. Short Put:   $6100
  3. Short Call:  $6910
  4. Long Call:   $6960

  Max Profit: $30.00
  Max Loss: $20.00
  Probability of Profit: 71.63%
```

### Web Dashboard
- Interactive charts with live updates
- Real-time P&L tracking
- ML prediction confidence bars
- Color-coded risk indicators
- One-click position management

## 📚 Educational Resources

To learn more about Iron Condor strategies:
- Options trading basics and Greeks
- Time decay (theta) and how it benefits sellers
- Volatility's impact on options pricing
- Rolling strategies for challenged positions
- Position management and adjustment techniques
- Machine learning in algorithmic trading

## ⚖️ Disclaimer

**THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY**

- Not financial advice
- Options trading involves significant risk
- Past performance does not guarantee future results
- ML predictions are not guaranteed to be accurate
- You can lose more than your initial investment
- Consult with a financial advisor before trading
- The authors are not responsible for any trading losses

## 🤝 Contributing

Feel free to fork, modify, and enhance this bot for your own learning and research.

### Future Enhancements
- Integration with broker APIs for live trading
- Backtesting engine with historical data
- Additional strategies (Iron Butterfly, Strangles, etc.)
- Portfolio optimization algorithms
- Risk visualization and heat maps
- Mobile app support

## 📝 License

This project is provided as-is for educational purposes.

## 📧 Support

For issues or questions:
- Check the troubleshooting section
- Review the code comments
- Test with different parameters

---

**Remember**: Trading options involves risk. Always use proper risk management and never trade with money you can't afford to lose.

**Happy Trading! 📈**

Made with ❤️ by Claude Sonnet 4.5
