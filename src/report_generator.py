"""
Report Generator Module
Generates detailed HTML and text reports for strategy analysis
"""

import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive strategy analysis reports"""

    def __init__(self, output_dir='output'):
        """
        Initialize report generator

        Args:
            output_dir (str): Directory to save reports
        """
        self.output_dir = output_dir

    def generate_text_report(self, summary, vol_metrics, save_path=None):
        """
        Generate a detailed text report

        Args:
            summary (dict): Strategy summary
            vol_metrics (dict): Volatility metrics
            save_path (str): Path to save the report

        Returns:
            str: Path to saved report
        """
        report = []
        report.append("=" * 80)
        report.append("S&P 500 IRON CONDOR TRADING BOT - ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {summary['analysis_date']}")
        report.append(f"\n{'-' * 80}\n")

        # Market Overview
        report.append("MARKET OVERVIEW")
        report.append("-" * 80)
        report.append(f"Current S&P 500 Price: ${summary['underlying_price']:.2f}")
        report.append(f"Days to Expiration: {summary['days_to_expiration']}")
        report.append(f"Expected Move: ${summary['strikes']['expected_move']:.2f} "
                     f"({summary['strikes']['expected_move_pct']:.2f}%)")
        report.append(f"\n{'-' * 80}\n")

        # Volatility Analysis
        report.append("VOLATILITY ANALYSIS")
        report.append("-" * 80)
        report.append(f"Current Volatility: {vol_metrics['current_volatility']:.2%}")
        report.append(f"10-Day Volatility: {vol_metrics['volatility_10d']:.2%}")
        report.append(f"30-Day Volatility: {vol_metrics['volatility_30d']:.2%}")
        report.append(f"60-Day Volatility: {vol_metrics['volatility_60d']:.2%}")
        report.append(f"Volatility Percentile: {vol_metrics['volatility_percentile']:.1f}%")
        report.append(f"Volatility Regime: {vol_metrics['volatility_regime']}")
        report.append(f"\n{'-' * 80}\n")

        # Iron Condor Strategy
        report.append("IRON CONDOR STRATEGY")
        report.append("-" * 80)
        report.append("\nSTRIKE PRICES (All 4 Legs):")
        report.append(f"  1. Long Put (Buy):   ${summary['strikes']['long_put']:.0f}")
        report.append(f"  2. Short Put (Sell):  ${summary['strikes']['short_put']:.0f}")
        report.append(f"  3. Short Call (Sell): ${summary['strikes']['short_call']:.0f}")
        report.append(f"  4. Long Call (Buy):  ${summary['strikes']['long_call']:.0f}")

        report.append(f"\nPut Spread Width: "
                     f"${summary['strikes']['short_put'] - summary['strikes']['long_put']:.0f}")
        report.append(f"Call Spread Width: "
                     f"${summary['strikes']['long_call'] - summary['strikes']['short_call']:.0f}")
        report.append(f"\n{'-' * 80}\n")

        # Profit & Loss Analysis
        report.append("PROFIT & LOSS ANALYSIS")
        report.append("-" * 80)
        report.append(f"Estimated Credit Received: ${summary['profit_loss']['estimated_credit']:.2f}")
        report.append(f"Maximum Profit: ${summary['profit_loss']['max_profit']:.2f}")
        report.append(f"Maximum Loss: ${summary['profit_loss']['max_loss']:.2f}")
        report.append(f"Return on Risk: {summary['profit_loss']['return_on_risk']:.2f}%")
        report.append(f"Risk/Reward Ratio: {summary['profit_loss']['risk_reward_ratio']:.2f}")
        report.append(f"\n{'-' * 80}\n")

        # Breakeven Analysis
        report.append("BREAKEVEN ANALYSIS")
        report.append("-" * 80)
        report.append(f"Lower Breakeven: ${summary['profit_loss']['breakeven_lower']:.2f}")
        report.append(f"Upper Breakeven: ${summary['profit_loss']['breakeven_upper']:.2f}")
        report.append(f"Breakeven Range: ${summary['profit_loss']['profit_zone_width']:.2f} "
                     f"({summary['profit_loss']['profit_zone_pct']:.2f}%)")
        report.append(f"\n{'-' * 80}\n")

        # Probability Analysis
        report.append("PROBABILITY ANALYSIS")
        report.append("-" * 80)
        report.append(f"Probability of Profit: {summary['probability']['probability_of_profit']:.2f}%")
        report.append(f"Confidence Level: {summary['probability']['confidence_level']:.2%}")
        report.append(f"Lower Breakeven (Std Dev): {summary['probability']['lower_breakeven_std_dev']:.2f}")
        report.append(f"Upper Breakeven (Std Dev): {summary['probability']['upper_breakeven_std_dev']:.2f}")
        report.append(f"\n{'-' * 80}\n")

        # Trading Recommendations
        report.append("TRADING RECOMMENDATIONS")
        report.append("-" * 80)
        report.append("\nENTRY STRATEGY:")
        report.append("  • Enter when volatility is in the moderate to elevated range")
        report.append("  • Aim for 30-45 days to expiration for optimal time decay")
        report.append("  • Target credit of 25-35% of the spread width")
        report.append("\nMANAGEMENT RULES:")
        report.append("  • Take profit at 50% of max profit")
        report.append("  • Cut losses at 200% of credit received")
        report.append("  • Consider rolling if 21 days remain and position is challenged")
        report.append("\nRISK MANAGEMENT:")
        report.append("  • Never risk more than 2-5% of account on a single trade")
        report.append("  • Monitor position daily for any breach of short strikes")
        report.append("  • Have an exit plan before entering the trade")
        report.append(f"\n{'-' * 80}\n")

        # Market Conditions
        report.append("CURRENT MARKET CONDITIONS")
        report.append("-" * 80)
        if vol_metrics['volatility_regime'] == 'LOW':
            report.append("⚠ Low volatility environment - smaller credits expected")
            report.append("  Consider waiting for higher volatility or using tighter strikes")
        elif vol_metrics['volatility_regime'] == 'MODERATE':
            report.append("✓ Moderate volatility - Good environment for Iron Condors")
            report.append("  Balanced risk/reward with reasonable credit potential")
        elif vol_metrics['volatility_regime'] == 'ELEVATED':
            report.append("✓ Elevated volatility - Excellent for Iron Condors")
            report.append("  Higher credits available, but increased risk of price movement")
        else:  # HIGH
            report.append("⚠ High volatility - Risky environment")
            report.append("  Consider wider strikes or waiting for volatility to decrease")

        report.append(f"\n{'=' * 80}\n")
        report.append("DISCLAIMER: This analysis is for educational purposes only.")
        report.append("Not financial advice. Trade at your own risk.")
        report.append("=" * 80)

        # Save report
        report_text = "\n".join(report)

        if save_path is None:
            save_path = f"{self.output_dir}/iron_condor_report.txt"

        with open(save_path, 'w') as f:
            f.write(report_text)

        logger.info(f"Text report saved to {save_path}")
        return save_path

    def generate_html_report(self, summary, vol_metrics, chart_paths, save_path=None):
        """
        Generate an HTML report with embedded charts

        Args:
            summary (dict): Strategy summary
            vol_metrics (dict): Volatility metrics
            chart_paths (list): Paths to chart images
            save_path (str): Path to save the report

        Returns:
            str: Path to saved report
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>S&P 500 Iron Condor Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2E86AB;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #333;
            background-color: #f0f0f0;
            padding: 10px;
            margin-top: 30px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background-color: #f9f9f9;
            border-left: 4px solid #2E86AB;
            padding: 15px;
            border-radius: 4px;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }}
        .metric-value {{
            font-size: 1.3em;
            color: #2E86AB;
            margin-top: 5px;
        }}
        .strike-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .strike-table th, .strike-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .strike-table th {{
            background-color: #2E86AB;
            color: white;
        }}
        .strike-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .chart {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .alert {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .alert-info {{
            background-color: #d1ecf1;
            border-left: 4px solid #0c5460;
            color: #0c5460;
        }}
        .alert-success {{
            background-color: #d4edda;
            border-left: 4px solid #155724;
            color: #155724;
        }}
        .alert-warning {{
            background-color: #fff3cd;
            border-left: 4px solid #856404;
            color: #856404;
        }}
        .timestamp {{
            color: #999;
            font-size: 0.9em;
            text-align: right;
        }}
        ul {{
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>S&P 500 Iron Condor Trading Bot Analysis</h1>
        <p class="timestamp">Generated: {summary['analysis_date']}</p>

        <h2>Market Overview</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Current S&P 500 Price</div>
                <div class="metric-value">${summary['underlying_price']:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Days to Expiration</div>
                <div class="metric-value">{summary['days_to_expiration']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Expected Move</div>
                <div class="metric-value">${summary['strikes']['expected_move']:.2f} ({summary['strikes']['expected_move_pct']:.2f}%)</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Volatility</div>
                <div class="metric-value">{summary['volatility']:.2%}</div>
            </div>
        </div>

        <h2>Volatility Analysis</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Current Volatility</div>
                <div class="metric-value">{vol_metrics['current_volatility']:.2%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">30-Day Volatility</div>
                <div class="metric-value">{vol_metrics['volatility_30d']:.2%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Volatility Percentile</div>
                <div class="metric-value">{vol_metrics['volatility_percentile']:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Volatility Regime</div>
                <div class="metric-value">{vol_metrics['volatility_regime']}</div>
            </div>
        </div>

        <h2>Iron Condor Strike Prices</h2>
        <table class="strike-table">
            <thead>
                <tr>
                    <th>Leg</th>
                    <th>Action</th>
                    <th>Type</th>
                    <th>Strike Price</th>
                    <th>Distance from Current</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>BUY</td>
                    <td>Put</td>
                    <td>${summary['strikes']['long_put']:.0f}</td>
                    <td>${summary['underlying_price'] - summary['strikes']['long_put']:.2f} ({((summary['underlying_price'] - summary['strikes']['long_put'])/summary['underlying_price']*100):.2f}%)</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>SELL</td>
                    <td>Put</td>
                    <td>${summary['strikes']['short_put']:.0f}</td>
                    <td>${summary['underlying_price'] - summary['strikes']['short_put']:.2f} ({((summary['underlying_price'] - summary['strikes']['short_put'])/summary['underlying_price']*100):.2f}%)</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>SELL</td>
                    <td>Call</td>
                    <td>${summary['strikes']['short_call']:.0f}</td>
                    <td>${summary['strikes']['short_call'] - summary['underlying_price']:.2f} ({((summary['strikes']['short_call'] - summary['underlying_price'])/summary['underlying_price']*100):.2f}%)</td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>BUY</td>
                    <td>Call</td>
                    <td>${summary['strikes']['long_call']:.0f}</td>
                    <td>${summary['strikes']['long_call'] - summary['underlying_price']:.2f} ({((summary['strikes']['long_call'] - summary['underlying_price'])/summary['underlying_price']*100):.2f}%)</td>
                </tr>
            </tbody>
        </table>

        <h2>Profit & Loss Analysis</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Max Profit</div>
                <div class="metric-value">${summary['profit_loss']['max_profit']:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Max Loss</div>
                <div class="metric-value">${summary['profit_loss']['max_loss']:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Return on Risk</div>
                <div class="metric-value">{summary['profit_loss']['return_on_risk']:.2f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Probability of Profit</div>
                <div class="metric-value">{summary['probability']['probability_of_profit']:.2f}%</div>
            </div>
        </div>

        <h2>Breakeven Points</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Lower Breakeven</div>
                <div class="metric-value">${summary['profit_loss']['breakeven_lower']:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Upper Breakeven</div>
                <div class="metric-value">${summary['profit_loss']['breakeven_upper']:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Breakeven Range</div>
                <div class="metric-value">${summary['profit_loss']['profit_zone_width']:.2f} ({summary['profit_loss']['profit_zone_pct']:.2f}%)</div>
            </div>
        </div>

        <h2>Visual Analysis</h2>
        """

        # Add charts
        for chart_path in chart_paths:
            chart_name = chart_path.split('/')[-1].replace('.png', '').replace('_', ' ').title()
            html += f"""
        <div class="chart">
            <h3>{chart_name}</h3>
            <img src="{chart_path}" alt="{chart_name}">
        </div>
            """

        # Add recommendations
        vol_regime = vol_metrics['volatility_regime']
        if vol_regime == 'LOW':
            alert_class = 'alert-warning'
            recommendation = "⚠ Low volatility environment - smaller credits expected. Consider waiting for higher volatility."
        elif vol_regime in ['MODERATE', 'ELEVATED']:
            alert_class = 'alert-success'
            recommendation = "✓ Good environment for Iron Condors. Proceed with standard position sizing."
        else:
            alert_class = 'alert-warning'
            recommendation = "⚠ High volatility - Increased risk. Consider wider strikes or reduced position size."

        html += f"""
        <h2>Trading Recommendations</h2>
        <div class="alert {alert_class}">
            <strong>Current Market Conditions:</strong> {recommendation}
        </div>

        <div class="alert alert-info">
            <strong>Entry Strategy:</strong>
            <ul>
                <li>Enter when volatility is in the moderate to elevated range</li>
                <li>Aim for 30-45 days to expiration for optimal time decay</li>
                <li>Target credit of 25-35% of the spread width</li>
            </ul>
        </div>

        <div class="alert alert-info">
            <strong>Management Rules:</strong>
            <ul>
                <li>Take profit at 50% of max profit</li>
                <li>Cut losses at 200% of credit received</li>
                <li>Consider rolling if 21 days remain and position is challenged</li>
            </ul>
        </div>

        <div class="alert alert-info">
            <strong>Risk Management:</strong>
            <ul>
                <li>Never risk more than 2-5% of account on a single trade</li>
                <li>Monitor position daily for any breach of short strikes</li>
                <li>Have an exit plan before entering the trade</li>
            </ul>
        </div>

        <p style="text-align: center; color: #999; margin-top: 40px; padding: 20px; border-top: 1px solid #ddd;">
            <strong>DISCLAIMER:</strong> This analysis is for educational purposes only. Not financial advice. Trade at your own risk.
        </p>
    </div>
</body>
</html>
        """

        if save_path is None:
            save_path = f"{self.output_dir}/iron_condor_report.html"

        with open(save_path, 'w') as f:
            f.write(html)

        logger.info(f"HTML report saved to {save_path}")
        return save_path

    def generate_csv_data(self, data, summary, save_path=None):
        """
        Generate CSV file with strategy data

        Args:
            data (pd.DataFrame): Historical price data
            summary (dict): Strategy summary
            save_path (str): Path to save the CSV

        Returns:
            str: Path to saved CSV
        """
        if save_path is None:
            save_path = f"{self.output_dir}/strategy_data.csv"

        # Save price data
        data.to_csv(save_path)
        logger.info(f"CSV data saved to {save_path}")

        # Save strategy summary
        summary_path = f"{self.output_dir}/strategy_summary.csv"
        summary_df = pd.DataFrame([{
            'Analysis Date': summary['analysis_date'],
            'Current Price': summary['underlying_price'],
            'DTE': summary['days_to_expiration'],
            'Volatility': summary['volatility'],
            'Long Put': summary['strikes']['long_put'],
            'Short Put': summary['strikes']['short_put'],
            'Short Call': summary['strikes']['short_call'],
            'Long Call': summary['strikes']['long_call'],
            'Max Profit': summary['profit_loss']['max_profit'],
            'Max Loss': summary['profit_loss']['max_loss'],
            'PoP': summary['probability']['probability_of_profit']
        }])
        summary_df.to_csv(summary_path, index=False)

        return save_path
