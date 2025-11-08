#!/usr/bin/env python3
"""
S&P 500 Iron Condor Trading Bot
Main execution script
"""

import os
import sys
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import SP500DataFetcher
from volatility_analyzer import VolatilityAnalyzer
from iron_condor_strategy import IronCondorStrategy
from visualizer import StrategyVisualizer
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║          S&P 500 IRON CONDOR TRADING BOT                     ║
    ║          Advanced Options Strategy Analyzer                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main execution function"""
    try:
        print_banner()
        logger.info("Starting S&P 500 Iron Condor Trading Bot...")

        # Create output directory
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

        # Step 1: Fetch S&P 500 Data
        print("\n" + "="*70)
        print("STEP 1: Fetching S&P 500 Historical Data")
        print("="*70)
        fetcher = SP500DataFetcher(symbol="^GSPC")
        data = fetcher.fetch_historical_data(period="2y", interval="1d")

        if data is None:
            logger.error("Failed to fetch data. Exiting.")
            return

        current_price = fetcher.get_current_price()
        price_stats = fetcher.get_price_stats()

        print(f"\n✓ Successfully retrieved {len(data)} days of data")
        print(f"  Current S&P 500 Price: ${current_price:.2f}")
        print(f"  52-Week High: ${price_stats['max_price']:.2f}")
        print(f"  52-Week Low: ${price_stats['min_price']:.2f}")
        print(f"  Average Volume: {price_stats['avg_volume']:,.0f}")

        # Step 2: Analyze Volatility
        print("\n" + "="*70)
        print("STEP 2: Analyzing Market Volatility")
        print("="*70)
        vol_analyzer = VolatilityAnalyzer(data)
        vol_metrics = vol_analyzer.get_volatility_metrics()

        print(f"\n✓ Volatility Analysis Complete")
        print(f"  Current Volatility: {vol_metrics['current_volatility']:.2%}")
        print(f"  30-Day Volatility: {vol_metrics['volatility_30d']:.2%}")
        print(f"  Volatility Regime: {vol_metrics['volatility_regime']}")
        print(f"  Volatility Percentile: {vol_metrics['volatility_percentile']:.1f}%")

        # Step 3: Calculate Iron Condor Strategy
        print("\n" + "="*70)
        print("STEP 3: Calculating Iron Condor Strategy")
        print("="*70)

        # Use current volatility for strategy
        days_to_expiration = 45  # Standard 45 DTE
        strategy = IronCondorStrategy(
            current_price=current_price,
            volatility=vol_metrics['current_volatility'],
            days_to_expiration=days_to_expiration
        )

        # Calculate optimal strikes
        strikes = strategy.calculate_optimal_strikes()
        profit_loss = strategy.calculate_profit_loss_zones()
        probability = strategy.calculate_probability_of_profit()

        print(f"\n✓ Iron Condor Strategy Calculated")
        print(f"\n  STRIKE PRICES (All 4 Legs):")
        print(f"  ┌─────────────────────────────────────────────┐")
        print(f"  │ 1. Long Put (Buy):    ${strikes['long_put']:>7.0f}       │")
        print(f"  │ 2. Short Put (Sell):   ${strikes['short_put']:>7.0f}       │")
        print(f"  │ 3. Short Call (Sell):  ${strikes['short_call']:>7.0f}       │")
        print(f"  │ 4. Long Call (Buy):   ${strikes['long_call']:>7.0f}       │")
        print(f"  └─────────────────────────────────────────────┘")

        print(f"\n  PROFIT & LOSS:")
        print(f"  ┌─────────────────────────────────────────────┐")
        print(f"  │ Max Profit:           ${profit_loss['max_profit']:>7.2f}       │")
        print(f"  │ Max Loss:             ${profit_loss['max_loss']:>7.2f}       │")
        print(f"  │ Return on Risk:       {profit_loss['return_on_risk']:>6.2f}%       │")
        print(f"  │ Probability of Profit: {probability['probability_of_profit']:>5.2f}%       │")
        print(f"  └─────────────────────────────────────────────┘")

        print(f"\n  BREAKEVEN POINTS:")
        print(f"  ┌─────────────────────────────────────────────┐")
        print(f"  │ Lower Breakeven:      ${profit_loss['breakeven_lower']:>7.2f}       │")
        print(f"  │ Upper Breakeven:      ${profit_loss['breakeven_upper']:>7.2f}       │")
        print(f"  │ Profit Range:         ${profit_loss['profit_zone_width']:>7.2f}       │")
        print(f"  └─────────────────────────────────────────────┘")

        # Step 4: Generate Visualizations
        print("\n" + "="*70)
        print("STEP 4: Generating Visual Charts")
        print("="*70)
        visualizer = StrategyVisualizer(output_dir=output_dir)
        chart_paths = visualizer.create_dashboard(data, vol_analyzer, strategy)

        print(f"\n✓ Generated {len(chart_paths)} visualization charts:")
        for i, chart in enumerate(chart_paths, 1):
            print(f"  {i}. {chart}")

        # Step 5: Generate Reports
        print("\n" + "="*70)
        print("STEP 5: Generating Detailed Reports")
        print("="*70)
        report_gen = ReportGenerator(output_dir=output_dir)

        # Generate strategy summary
        summary = strategy.generate_strategy_summary()

        # Generate text report
        text_report = report_gen.generate_text_report(summary, vol_metrics)
        print(f"\n✓ Text Report: {text_report}")

        # Generate HTML report
        html_report = report_gen.generate_html_report(summary, vol_metrics, chart_paths)
        print(f"✓ HTML Report: {html_report}")

        # Generate CSV data
        csv_report = report_gen.generate_csv_data(data, summary)
        print(f"✓ CSV Data: {csv_report}")

        # Step 6: Display Market Recommendations
        print("\n" + "="*70)
        print("MARKET RECOMMENDATIONS")
        print("="*70)

        if vol_metrics['volatility_regime'] == 'LOW':
            print("\n⚠  LOW VOLATILITY ENVIRONMENT")
            print("   • Smaller credits expected")
            print("   • Consider waiting for higher volatility")
            print("   • Or use tighter strikes with lower risk")
        elif vol_metrics['volatility_regime'] == 'MODERATE':
            print("\n✓  MODERATE VOLATILITY - GOOD FOR IRON CONDORS")
            print("   • Balanced risk/reward environment")
            print("   • Reasonable credit potential")
            print("   • Proceed with standard position sizing")
        elif vol_metrics['volatility_regime'] == 'ELEVATED':
            print("\n✓  ELEVATED VOLATILITY - EXCELLENT FOR IRON CONDORS")
            print("   • Higher credits available")
            print("   • Good premium collection environment")
            print("   • Monitor for increased price movement")
        else:  # HIGH
            print("\n⚠  HIGH VOLATILITY - RISKY ENVIRONMENT")
            print("   • Significant price swings expected")
            print("   • Consider wider strikes")
            print("   • Reduce position size or wait for calm")

        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print(f"\n✓ All reports and charts saved to: {output_dir}/")
        print(f"✓ Open the HTML report for interactive analysis")
        print(f"\n  HTML Report: {html_report}")
        print("\n" + "="*70)
        print("\nDISCLAIMER: This analysis is for educational purposes only.")
        print("Not financial advice. Trade at your own risk.")
        print("="*70 + "\n")

        logger.info("Trading bot analysis completed successfully!")

    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
