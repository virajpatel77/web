"""
ML Engine that combines price and volatility predictions
to provide trading recommendations
"""

import logging
from typing import Dict
import pandas as pd
from .price_predictor import PricePredictor
from .volatility_predictor import VolatilityPredictor

logger = logging.getLogger(__name__)


class MLEngine:
    """
    Main ML engine combining multiple prediction models
    """

    def __init__(self):
        """Initialize ML engine with predictors"""
        self.price_predictor = PricePredictor(lookback=60, forecast_days=5)
        self.volatility_predictor = VolatilityPredictor(forecast_horizon=5)
        self.is_trained = False

    def train(self, historical_data: pd.DataFrame):
        """
        Train all ML models

        Args:
            historical_data (pd.DataFrame): Historical price data

        Returns:
            dict: Training results
        """
        logger.info("Training ML models...")

        # Train price predictor
        logger.info("Training price prediction model...")
        price_training = self.price_predictor.train(historical_data, epochs=50)

        # Train volatility predictor
        logger.info("Training volatility forecasting model...")
        vol_training = self.volatility_predictor.train(historical_data)

        self.is_trained = True
        logger.info("ML engine training completed")

        return {
            'price_model': price_training,
            'volatility_model': vol_training,
            'success': True
        }

    def predict(self, recent_data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive prediction

        Args:
            recent_data (pd.DataFrame): Recent price data

        Returns:
            dict: Complete prediction with recommendations
        """
        logger.info("Generating ML predictions...")

        # Get price prediction
        price_prediction = self.price_predictor.predict(recent_data)

        # Get volatility forecast
        vol_forecast = self.volatility_predictor.predict(recent_data)

        # Generate trading recommendation
        recommendation = self._generate_recommendation(
            price_prediction,
            vol_forecast
        )

        return {
            'price_prediction': price_prediction,
            'volatility_forecast': vol_forecast,
            'recommendation': recommendation,
            'model_version': '1.0.0'
        }

    def _generate_recommendation(self, price_pred: Dict, vol_forecast: Dict) -> Dict:
        """
        Generate trading recommendation based on predictions

        Args:
            price_pred (dict): Price prediction results
            vol_forecast (dict): Volatility forecast results

        Returns:
            dict: Trading recommendation
        """
        # Extract key metrics
        price_direction = price_pred['direction']
        price_confidence = price_pred['confidence']
        vol_regime = vol_forecast['volatility_regime']
        vol_change = vol_forecast['volatility_change_percent']

        # Initialize recommendation
        action = 'HOLD'
        confidence = 0.5
        rationale = []
        risk_level = 'MODERATE'

        # Determine action based on predictions
        if vol_regime in ['MODERATE', 'ELEVATED'] and abs(vol_change) < 20:
            # Good conditions for Iron Condor
            if price_direction == 'neutral':
                action = 'ENTER'
                confidence = min(price_confidence + 0.2, 0.9)
                rationale.append(f"Neutral price prediction with {vol_regime.lower()} volatility")
                rationale.append("Ideal conditions for Iron Condor strategy")
                risk_level = 'LOW' if vol_regime == 'MODERATE' else 'MODERATE'

            elif price_confidence < 0.6:
                # Low confidence in direction = possible range-bound
                action = 'ENTER'
                confidence = 0.7
                rationale.append("Low directional conviction suggests range-bound market")
                rationale.append(f"{vol_regime} volatility supports premium selling")
                risk_level = 'MODERATE'

            else:
                action = 'WAIT'
                confidence = 0.6
                rationale.append(f"Strong {price_direction} prediction may break range")
                rationale.append("Consider waiting for price to settle")
                risk_level = 'MODERATE'

        elif vol_regime == 'LOW':
            action = 'WAIT'
            confidence = 0.5
            rationale.append("Low volatility environment - limited premium available")
            rationale.append("Consider waiting for volatility expansion")
            risk_level = 'LOW'

        elif vol_regime == 'HIGH' or abs(vol_change) > 30:
            action = 'AVOID'
            confidence = 0.8
            rationale.append("High or rapidly changing volatility")
            rationale.append("Elevated risk of price breaking through strikes")
            risk_level = 'HIGH'

        else:
            action = 'WAIT'
            confidence = 0.5
            rationale.append("Mixed signals from price and volatility models")
            rationale.append("Wait for clearer market conditions")
            risk_level = 'MODERATE'

        # Get optimal DTE recommendation
        dte_recommendation = self.volatility_predictor.get_optimal_dte(
            vol_forecast['forecasted_volatility']
        )

        return {
            'action': action,
            'confidence': confidence,
            'rationale': rationale,
            'risk_level': risk_level,
            'optimal_dte': dte_recommendation['recommended_dte'],
            'dte_rationale': dte_recommendation['rationale'],
            'price_direction': price_direction,
            'price_confidence': price_confidence,
            'volatility_regime': vol_regime
        }

    def get_optimal_strikes(self, current_price: float, volatility: float,
                           price_prediction: Dict) -> Dict:
        """
        Calculate optimal strike prices based on ML predictions

        Args:
            current_price (float): Current underlying price
            volatility (float): Current volatility
            price_prediction (dict): Price prediction results

        Returns:
            dict: Optimal strike prices
        """
        # Adjust strike width based on price prediction confidence
        price_confidence = price_prediction['confidence']
        predicted_change = abs(price_prediction['price_change_percent'])

        # Wider strikes if high confidence in direction
        if price_confidence > 0.7 and predicted_change > 2:
            strike_multiplier = 1.3  # Wider strikes for more safety
        else:
            strike_multiplier = 1.0  # Standard strikes

        # Calculate expected move
        expected_move = current_price * volatility * np.sqrt(45 / 365) * strike_multiplier

        # Calculate strikes
        short_put_strike = current_price - expected_move
        short_call_strike = current_price + expected_move

        # Adjust based on price direction
        if price_prediction['direction'] == 'up' and price_confidence > 0.6:
            # Skew higher to account for upward bias
            short_call_strike *= 1.1
        elif price_prediction['direction'] == 'down' and price_confidence > 0.6:
            # Skew lower to account for downward bias
            short_put_strike *= 0.9

        # Wing width (protection strikes)
        wing_width = expected_move * 0.3  # 30% of expected move

        return {
            'long_put': round(short_put_strike - wing_width, -1),
            'short_put': round(short_put_strike, -1),
            'short_call': round(short_call_strike, -1),
            'long_call': round(short_call_strike + wing_width, -1),
            'expected_move': expected_move,
            'confidence_adjusted': price_confidence > 0.7
        }

    def load_models(self):
        """Load pre-trained models"""
        logger.info("Loading pre-trained models...")

        success = self.price_predictor.load_model()
        if success:
            self.is_trained = True
            logger.info("Models loaded successfully")
        else:
            logger.warning("Could not load models. Will need to train first.")

        return success


# Add numpy import if not available
try:
    import numpy as np
except ImportError:
    import math as np
