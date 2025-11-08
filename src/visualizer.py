"""
Visualization Module
Creates charts and visual representations of market data and strategy analysis
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (14, 10)


class StrategyVisualizer:
    """Creates visualizations for trading strategy analysis"""

    def __init__(self, output_dir='output'):
        """
        Initialize visualizer

        Args:
            output_dir (str): Directory to save charts
        """
        self.output_dir = output_dir

    def plot_price_history(self, data, save_path=None):
        """
        Plot S&P 500 price history

        Args:
            data (pd.DataFrame): Historical price data
            save_path (str): Path to save the plot

        Returns:
            str: Path to saved plot
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Price chart
        ax1.plot(data.index, data['Close'], linewidth=1.5, color='#2E86AB')
        ax1.fill_between(data.index, data['Low'], data['High'], alpha=0.2, color='#2E86AB')
        ax1.set_title('S&P 500 Price History', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Volume chart
        colors = ['green' if data['Close'].iloc[i] > data['Open'].iloc[i] else 'red'
                  for i in range(len(data))]
        ax2.bar(data.index, data['Volume'], color=colors, alpha=0.5, width=0.8)
        ax2.set_title('Trading Volume', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()

        if save_path is None:
            save_path = f"{self.output_dir}/price_history.png"

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Price history chart saved to {save_path}")
        plt.close()

        return save_path

    def plot_volatility_analysis(self, data, volatility_analyzer, save_path=None):
        """
        Plot volatility analysis

        Args:
            data (pd.DataFrame): Historical price data
            volatility_analyzer: VolatilityAnalyzer instance
            save_path (str): Path to save the plot

        Returns:
            str: Path to saved plot
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))

        # Calculate volatilities
        rolling_vol_10 = volatility_analyzer.calculate_rolling_volatility(window=10)
        rolling_vol_30 = volatility_analyzer.calculate_rolling_volatility(window=30)
        rolling_vol_60 = volatility_analyzer.calculate_rolling_volatility(window=60)

        # Plot 1: Price with volatility bands
        current_price = data['Close'].iloc[-1]
        ax1.plot(data.index, data['Close'], linewidth=1.5, color='#2E86AB', label='S&P 500 Price')
        ax1.set_title('S&P 500 Price Movement', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Plot 2: Rolling volatility
        ax2.plot(rolling_vol_10.index, rolling_vol_10 * 100, linewidth=1.5,
                label='10-day Volatility', alpha=0.7, color='#A23B72')
        ax2.plot(rolling_vol_30.index, rolling_vol_30 * 100, linewidth=1.5,
                label='30-day Volatility', alpha=0.7, color='#F18F01')
        ax2.plot(rolling_vol_60.index, rolling_vol_60 * 100, linewidth=1.5,
                label='60-day Volatility', alpha=0.7, color='#C73E1D')
        ax2.set_title('Historical Volatility (Annualized)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Volatility (%)', fontsize=12)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Plot 3: Daily returns distribution
        daily_returns = data['Close'].pct_change().dropna() * 100
        ax3.hist(daily_returns, bins=50, alpha=0.7, color='#2E86AB', edgecolor='black')
        ax3.axvline(daily_returns.mean(), color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {daily_returns.mean():.2f}%')
        ax3.axvline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
        ax3.set_title('Daily Returns Distribution', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Daily Return (%)', fontsize=12)
        ax3.set_ylabel('Frequency', fontsize=12)
        ax3.legend(loc='upper right')
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path is None:
            save_path = f"{self.output_dir}/volatility_analysis.png"

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Volatility analysis chart saved to {save_path}")
        plt.close()

        return save_path

    def plot_iron_condor_payoff(self, strategy, save_path=None):
        """
        Plot Iron Condor payoff diagram

        Args:
            strategy: IronCondorStrategy instance
            save_path (str): Path to save the plot

        Returns:
            str: Path to saved plot
        """
        strikes = strategy.strikes
        profit_loss = strategy.calculate_profit_loss_zones()

        # Create price range for payoff diagram
        price_range = np.linspace(
            strikes['long_put'] - 100,
            strikes['long_call'] + 100,
            200
        )

        # Calculate payoff for each price
        payoffs = []
        for price in price_range:
            if price <= strikes['long_put']:
                # Max loss on put side
                payoff = -profit_loss['max_loss']
            elif price < strikes['short_put']:
                # Loss zone between long and short put
                payoff = (price - strikes['short_put']) + profit_loss['estimated_credit']
            elif price <= strikes['short_call']:
                # Profit zone
                payoff = profit_loss['estimated_credit']
            elif price < strikes['long_call']:
                # Loss zone between short and long call
                payoff = (strikes['short_call'] - price) + profit_loss['estimated_credit']
            else:
                # Max loss on call side
                payoff = -profit_loss['max_loss']

            payoffs.append(payoff)

        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot payoff line
        ax.plot(price_range, payoffs, linewidth=2.5, color='#2E86AB', label='Iron Condor Payoff')
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.axvline(x=strikes['current_price'], color='green', linestyle='--',
                  linewidth=2, label=f'Current Price: ${strikes["current_price"]:.2f}')

        # Mark strike prices
        ax.axvline(x=strikes['long_put'], color='red', linestyle=':',
                  linewidth=1.5, alpha=0.7, label=f'Long Put: ${strikes["long_put"]:.0f}')
        ax.axvline(x=strikes['short_put'], color='orange', linestyle=':',
                  linewidth=1.5, alpha=0.7, label=f'Short Put: ${strikes["short_put"]:.0f}')
        ax.axvline(x=strikes['short_call'], color='orange', linestyle=':',
                  linewidth=1.5, alpha=0.7, label=f'Short Call: ${strikes["short_call"]:.0f}')
        ax.axvline(x=strikes['long_call'], color='red', linestyle=':',
                  linewidth=1.5, alpha=0.7, label=f'Long Call: ${strikes["long_call"]:.0f}')

        # Mark breakeven points
        ax.axvline(x=profit_loss['breakeven_lower'], color='purple', linestyle='--',
                  linewidth=2, alpha=0.7, label=f'Lower BE: ${profit_loss["breakeven_lower"]:.2f}')
        ax.axvline(x=profit_loss['breakeven_upper'], color='purple', linestyle='--',
                  linewidth=2, alpha=0.7, label=f'Upper BE: ${profit_loss["breakeven_upper"]:.2f}')

        # Shade profit and loss zones
        profit_zone_mask = (price_range >= profit_loss['breakeven_lower']) & \
                          (price_range <= profit_loss['breakeven_upper'])
        ax.fill_between(price_range, 0, payoffs, where=profit_zone_mask,
                       alpha=0.2, color='green', label='Profit Zone')
        ax.fill_between(price_range, 0, payoffs, where=~profit_zone_mask,
                       alpha=0.2, color='red', label='Loss Zone')

        ax.set_title('Iron Condor Payoff Diagram', fontsize=16, fontweight='bold')
        ax.set_xlabel('S&P 500 Price at Expiration ($)', fontsize=12)
        ax.set_ylabel('Profit/Loss ($)', fontsize=12)
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)

        # Add text box with key metrics
        textstr = f'Max Profit: ${profit_loss["max_profit"]:.2f}\n'
        textstr += f'Max Loss: ${profit_loss["max_loss"]:.2f}\n'
        textstr += f'Return on Risk: {profit_loss["return_on_risk"]:.1f}%'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', bbox=props)

        plt.tight_layout()

        if save_path is None:
            save_path = f"{self.output_dir}/iron_condor_payoff.png"

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Iron Condor payoff diagram saved to {save_path}")
        plt.close()

        return save_path

    def create_dashboard(self, data, volatility_analyzer, strategy):
        """
        Create a comprehensive dashboard with all visualizations

        Args:
            data (pd.DataFrame): Historical price data
            volatility_analyzer: VolatilityAnalyzer instance
            strategy: IronCondorStrategy instance

        Returns:
            list: Paths to all saved charts
        """
        charts = []

        charts.append(self.plot_price_history(data))
        charts.append(self.plot_volatility_analysis(data, volatility_analyzer))
        charts.append(self.plot_iron_condor_payoff(strategy))

        logger.info(f"Created {len(charts)} visualization charts")
        return charts
