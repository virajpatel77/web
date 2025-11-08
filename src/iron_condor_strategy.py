"""
Iron Condor Options Strategy Module
Calculates optimal strike prices and analyzes Iron Condor strategies
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class IronCondorStrategy:
    """
    Iron Condor Strategy Calculator

    An Iron Condor consists of 4 legs:
    1. Buy OTM Put (lower strike)
    2. Sell OTM Put (higher strike than #1)
    3. Sell OTM Call (lower strike than #4)
    4. Buy OTM Call (higher strike)

    This creates a credit spread with defined risk and profit potential.
    """

    def __init__(self, current_price, volatility, days_to_expiration=45):
        """
        Initialize Iron Condor strategy

        Args:
            current_price (float): Current price of underlying
            volatility (float): Historical or implied volatility
            days_to_expiration (int): Days until expiration
        """
        self.current_price = current_price
        self.volatility = volatility
        self.dte = days_to_expiration
        self.strikes = None

    def calculate_optimal_strikes(self, put_delta=0.16, call_delta=0.16, wing_width=50):
        """
        Calculate optimal strike prices for Iron Condor

        Args:
            put_delta (float): Target delta for short put (default 0.16 ~ 84% probability OTM)
            call_delta (float): Target delta for short call (default 0.16 ~ 84% probability OTM)
            wing_width (float): Distance between long and short strikes

        Returns:
            dict: Strike prices for all 4 legs
        """
        # Calculate expected move
        expected_move = self.current_price * self.volatility * np.sqrt(self.dte / 365)

        # For ~16 delta (1 standard deviation), use ~84% probability
        # This is approximately 1 standard deviation
        std_dev_multiplier = 1.0

        # Calculate short strikes (the ones we sell)
        short_put_strike = self.current_price - (expected_move * std_dev_multiplier)
        short_call_strike = self.current_price + (expected_move * std_dev_multiplier)

        # Calculate long strikes (the ones we buy for protection)
        long_put_strike = short_put_strike - wing_width
        long_call_strike = short_call_strike + wing_width

        # Round to nearest $5 (or $10 for higher prices)
        rounding = 5 if self.current_price < 2000 else 10

        self.strikes = {
            'long_put': self._round_strike(long_put_strike, rounding),
            'short_put': self._round_strike(short_put_strike, rounding),
            'short_call': self._round_strike(short_call_strike, rounding),
            'long_call': self._round_strike(long_call_strike, rounding),
            'current_price': self.current_price,
            'expected_move': expected_move,
            'expected_move_pct': (expected_move / self.current_price) * 100
        }

        logger.info(f"Calculated Iron Condor strikes: {self.strikes}")
        return self.strikes

    def _round_strike(self, price, increment=5):
        """Round strike price to nearest increment"""
        return round(price / increment) * increment

    def calculate_profit_loss_zones(self):
        """
        Calculate profit and loss zones for the Iron Condor

        Returns:
            dict: P&L zones and breakeven points
        """
        if self.strikes is None:
            self.calculate_optimal_strikes()

        # Wing widths
        put_width = self.strikes['short_put'] - self.strikes['long_put']
        call_width = self.strikes['long_call'] - self.strikes['short_call']

        # Typical credit received (estimated at ~30% of wing width)
        # This is a simplified estimate - actual credit depends on market conditions
        estimated_credit_put = put_width * 0.30
        estimated_credit_call = call_width * 0.30
        total_credit = estimated_credit_put + estimated_credit_call

        # Maximum profit (credit received)
        max_profit = total_credit

        # Maximum loss (wing width - credit received)
        max_loss_put = put_width - total_credit
        max_loss_call = call_width - total_credit
        max_loss = max(max_loss_put, max_loss_call)

        # Breakeven points
        breakeven_lower = self.strikes['short_put'] - total_credit
        breakeven_upper = self.strikes['short_call'] + total_credit

        profit_zone = {
            'max_profit': max_profit,
            'max_loss': max_loss,
            'estimated_credit': total_credit,
            'breakeven_lower': breakeven_lower,
            'breakeven_upper': breakeven_upper,
            'profit_zone_width': breakeven_upper - breakeven_lower,
            'profit_zone_pct': ((breakeven_upper - breakeven_lower) / self.current_price) * 100,
            'risk_reward_ratio': max_loss / max_profit if max_profit > 0 else 0,
            'return_on_risk': (max_profit / max_loss) * 100 if max_loss > 0 else 0
        }

        return profit_zone

    def calculate_probability_of_profit(self):
        """
        Calculate probability of profit (PoP) for the Iron Condor

        Returns:
            dict: Probability metrics
        """
        if self.strikes is None:
            self.calculate_optimal_strikes()

        profit_loss = self.calculate_profit_loss_zones()

        # Standard deviation for the period
        std_dev = self.current_price * self.volatility * np.sqrt(self.dte / 365)

        # Calculate how many standard deviations away the breakeven points are
        lower_std_dev = (self.current_price - profit_loss['breakeven_lower']) / std_dev
        upper_std_dev = (profit_loss['breakeven_upper'] - self.current_price) / std_dev

        # Using normal distribution for probability
        # PoP is probability price stays between breakeven points
        from scipy.stats import norm
        prob_below_upper = norm.cdf(upper_std_dev)
        prob_above_lower = 1 - norm.cdf(-lower_std_dev)
        pop = prob_below_upper + prob_above_lower - 1

        return {
            'probability_of_profit': pop * 100,
            'lower_breakeven_std_dev': lower_std_dev,
            'upper_breakeven_std_dev': upper_std_dev,
            'confidence_level': pop
        }

    def generate_strategy_summary(self):
        """
        Generate a comprehensive strategy summary

        Returns:
            dict: Complete strategy analysis
        """
        if self.strikes is None:
            self.calculate_optimal_strikes()

        profit_loss = self.calculate_profit_loss_zones()
        probability = self.calculate_probability_of_profit()

        summary = {
            'strategy': 'Iron Condor',
            'underlying_price': self.current_price,
            'days_to_expiration': self.dte,
            'volatility': self.volatility,
            'strikes': self.strikes,
            'profit_loss': profit_loss,
            'probability': probability,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return summary

    def get_strike_recommendations(self, risk_profile='moderate'):
        """
        Get strike recommendations based on risk profile

        Args:
            risk_profile (str): 'conservative', 'moderate', or 'aggressive'

        Returns:
            dict: Recommended strikes
        """
        if risk_profile == 'conservative':
            # Wider strikes, higher probability of profit
            return self.calculate_optimal_strikes(put_delta=0.10, call_delta=0.10, wing_width=50)
        elif risk_profile == 'aggressive':
            # Tighter strikes, higher credit but lower probability
            return self.calculate_optimal_strikes(put_delta=0.25, call_delta=0.25, wing_width=25)
        else:  # moderate
            # Balanced approach
            return self.calculate_optimal_strikes(put_delta=0.16, call_delta=0.16, wing_width=50)
