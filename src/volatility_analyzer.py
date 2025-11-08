"""
Volatility Analysis Module
Analyzes historical volatility and provides volatility metrics
"""

import numpy as np
import pandas as pd
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class VolatilityAnalyzer:
    """Analyzes volatility for options trading strategies"""

    def __init__(self, data):
        """
        Initialize the volatility analyzer

        Args:
            data (pd.DataFrame): Historical price data
        """
        self.data = data
        self.daily_returns = None

    def calculate_historical_volatility(self, window=30):
        """
        Calculate historical volatility (annualized)

        Args:
            window (int): Rolling window in days

        Returns:
            float: Annualized historical volatility
        """
        if 'Daily_Return' not in self.data.columns:
            self.data['Daily_Return'] = self.data['Close'].pct_change()

        self.daily_returns = self.data['Daily_Return'].dropna()

        # Annualized volatility (252 trading days)
        volatility = self.daily_returns.std() * np.sqrt(252)

        logger.info(f"Historical Volatility (annualized): {volatility:.2%}")
        return volatility

    def calculate_rolling_volatility(self, window=30):
        """
        Calculate rolling volatility

        Args:
            window (int): Rolling window size

        Returns:
            pd.Series: Rolling volatility
        """
        if 'Daily_Return' not in self.data.columns:
            self.data['Daily_Return'] = self.data['Close'].pct_change()

        rolling_vol = self.data['Daily_Return'].rolling(window=window).std() * np.sqrt(252)
        return rolling_vol

    def calculate_volatility_percentile(self, current_vol, lookback=252):
        """
        Calculate what percentile current volatility is at

        Args:
            current_vol (float): Current volatility
            lookback (int): Days to look back

        Returns:
            float: Percentile (0-100)
        """
        rolling_vol = self.calculate_rolling_volatility()
        recent_vol = rolling_vol.tail(lookback).dropna()

        percentile = stats.percentileofscore(recent_vol, current_vol)
        return percentile

    def get_volatility_metrics(self):
        """
        Get comprehensive volatility metrics

        Returns:
            dict: Volatility metrics
        """
        current_vol = self.calculate_historical_volatility(window=30)
        rolling_vol_10 = self.calculate_rolling_volatility(window=10).iloc[-1]
        rolling_vol_30 = self.calculate_rolling_volatility(window=30).iloc[-1]
        rolling_vol_60 = self.calculate_rolling_volatility(window=60).iloc[-1]

        metrics = {
            'current_volatility': current_vol,
            'volatility_10d': rolling_vol_10,
            'volatility_30d': rolling_vol_30,
            'volatility_60d': rolling_vol_60,
            'volatility_percentile': self.calculate_volatility_percentile(current_vol),
            'volatility_regime': self._classify_volatility_regime(current_vol)
        }

        return metrics

    def _classify_volatility_regime(self, volatility):
        """
        Classify volatility regime

        Args:
            volatility (float): Current volatility

        Returns:
            str: Volatility regime classification
        """
        if volatility < 0.15:
            return "LOW"
        elif volatility < 0.25:
            return "MODERATE"
        elif volatility < 0.35:
            return "ELEVATED"
        else:
            return "HIGH"

    def calculate_expected_move(self, current_price, days_to_expiration, volatility):
        """
        Calculate expected price move for options expiration

        Args:
            current_price (float): Current stock price
            days_to_expiration (int): Days until options expiration
            volatility (float): Implied or historical volatility

        Returns:
            dict: Expected move up and down
        """
        # Expected move formula: Price * Volatility * sqrt(DTE/365)
        expected_move = current_price * volatility * np.sqrt(days_to_expiration / 365)

        return {
            'expected_move': expected_move,
            'upper_range': current_price + expected_move,
            'lower_range': current_price - expected_move,
            'percentage': (expected_move / current_price) * 100
        }
