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

            if self.data.empty:
                logger.error("No data retrieved")
                return None

            logger.info(f"Retrieved {len(self.data)} data points")
            return self.data

        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None

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
