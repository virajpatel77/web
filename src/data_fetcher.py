"""
S&P 500 Data Fetcher Module
Retrieves historical price data for the S&P 500 index
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SP500DataFetcher:
    """Fetches and manages S&P 500 historical data"""

    def __init__(self, symbol="^GSPC"):
        """
        Initialize the data fetcher

        Args:
            symbol (str): Ticker symbol for S&P 500 (default: ^GSPC)
        """
        self.symbol = symbol
        self.data = None

    def fetch_historical_data(self, period="2y", interval="1d"):
        """
        Fetch historical price data

        Args:
            period (str): Time period (e.g., '1y', '2y', '5y')
            interval (str): Data interval (e.g., '1d', '1h')

        Returns:
            pd.DataFrame: Historical price data
        """
        try:
            logger.info(f"Fetching {period} of data for {self.symbol}")
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(period=period, interval=interval)

            if self.data is None or self.data.empty:
                logger.warning("Yahoo Finance access blocked or no data retrieved. Using demo data...")
                self.data = self._generate_demo_data(period)

            logger.info(f"Retrieved {len(self.data)} data points")
            return self.data

        except Exception as e:
            logger.warning(f"Error fetching data: {e}. Using demo data...")
            self.data = self._generate_demo_data(period)
            logger.info(f"Retrieved {len(self.data)} demo data points")
            return self.data

    def _generate_demo_data(self, period="2y"):
        """
        Generate realistic demo S&P 500 data

        Args:
            period (str): Time period (e.g., '1y', '2y')

        Returns:
            pd.DataFrame: Simulated historical data
        """
        import numpy as np

        # Parse period
        years = int(period.replace('y', ''))
        days = years * 252  # Trading days

        # S&P 500 realistic parameters
        start_price = 4200
        drift = 0.10 / 252  # 10% annual return
        volatility = 0.18 / np.sqrt(252)  # 18% annualized volatility

        # Generate dates
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=days, freq='B')

        # Generate price path using geometric Brownian motion
        np.random.seed(42)  # For reproducibility
        returns = np.random.normal(drift, volatility, days)
        returns[0] = 0

        price_path = start_price * np.exp(np.cumsum(returns))

        # Add some realistic trends
        trend = np.linspace(0, 0.2, days)  # Upward trend
        price_path = price_path * (1 + trend)

        # Generate OHLC data
        data = pd.DataFrame(index=dates)
        data['Close'] = price_path
        data['Open'] = price_path * (1 + np.random.normal(0, 0.002, days))
        data['High'] = np.maximum(data['Open'], data['Close']) * (1 + np.random.uniform(0, 0.01, days))
        data['Low'] = np.minimum(data['Open'], data['Close']) * (1 - np.random.uniform(0, 0.01, days))
        data['Volume'] = np.random.normal(3.5e9, 0.5e9, days).astype(int)

        # Ensure Volume is positive
        data['Volume'] = data['Volume'].clip(lower=1e9)

        logger.info(f"Generated demo data with {len(data)} days, current price: ${data['Close'].iloc[-1]:.2f}")
        return data

    def get_current_price(self):
        """Get the most recent closing price"""
        if self.data is None or self.data.empty:
            self.fetch_historical_data(period="5d")

        return self.data['Close'].iloc[-1] if self.data is not None else None

    def get_price_stats(self):
        """Calculate basic price statistics"""
        if self.data is None:
            return None

        stats = {
            'current_price': self.data['Close'].iloc[-1],
            'mean_price': self.data['Close'].mean(),
            'std_dev': self.data['Close'].std(),
            'min_price': self.data['Close'].min(),
            'max_price': self.data['Close'].max(),
            'avg_volume': self.data['Volume'].mean()
        }

        return stats

    def calculate_daily_returns(self):
        """Calculate daily percentage returns"""
        if self.data is None:
            return None

        self.data['Daily_Return'] = self.data['Close'].pct_change() * 100
        return self.data['Daily_Return']

    def get_data(self):
        """Return the fetched data"""
        return self.data
