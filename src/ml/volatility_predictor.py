"""
GARCH-based volatility forecasting model
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Try to import arch library for GARCH models
try:
    from arch import arch_model
    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False
    logger.warning("arch library not available. Volatility forecasting will use simplified model.")


class VolatilityPredictor:
    """
    GARCH-based model for forecasting volatility
    """

    def __init__(self, forecast_horizon=5):
        """
        Initialize volatility predictor

        Args:
            forecast_horizon (int): Number of days to forecast ahead
        """
        self.forecast_horizon = forecast_horizon
        self.model = None
        self.model_fit = None
        self.is_trained = False

    def prepare_data(self, data):
        """
        Prepare data for GARCH model

        Args:
            data (pd.DataFrame): Historical price data

        Returns:
            pd.Series: Daily returns
        """
        # Calculate daily returns
        returns = data['Close'].pct_change().dropna() * 100  # Convert to percentage
        return returns

    def train(self, data, p=1, q=1):
        """
        Train GARCH model

        Args:
            data (pd.DataFrame): Historical price data
            p (int): GARCH p parameter
            q (int): GARCH q parameter

        Returns:
            dict: Model summary
        """
        if not ARCH_AVAILABLE:
            logger.warning("arch library not available. Using simple volatility estimation.")
            self.is_trained = True
            return {'method': 'simple', 'success': True}

        logger.info("Preparing returns data for GARCH model...")
        returns = self.prepare_data(data)

        logger.info(f"Training GARCH({p},{q}) model...")
        self.model = arch_model(returns, vol='Garch', p=p, q=q)
        self.model_fit = self.model.fit(disp='off')
        self.is_trained = True

        logger.info("GARCH model training completed")

        return {
            'aic': float(self.model_fit.aic),
            'bic': float(self.model_fit.bic),
            'log_likelihood': float(self.model_fit.loglikelihood),
            'method': 'GARCH'
        }

    def predict(self, data):
        """
        Forecast future volatility

        Args:
            data (pd.DataFrame): Historical price data

        Returns:
            dict: Volatility forecast
        """
        if not self.is_trained:
            logger.warning("Model not trained. Using simple volatility estimation.")
            return self._simple_volatility(data)

        if not ARCH_AVAILABLE:
            return self._simple_volatility(data)

        # Make forecast
        forecast = self.model_fit.forecast(horizon=self.forecast_horizon)

        # Extract variance forecast and convert to volatility (annualized)
        variance_forecast = forecast.variance.values[-1, :]
        volatility_forecast = np.sqrt(variance_forecast) * np.sqrt(252) / 100  # Annualized

        # Current volatility
        returns = self.prepare_data(data)
        current_volatility = returns.std() * np.sqrt(252) / 100  # Annualized

        # Average forecast volatility
        avg_forecast_volatility = np.mean(volatility_forecast)

        # Volatility change
        vol_change = avg_forecast_volatility - current_volatility
        vol_change_percent = (vol_change / current_volatility) * 100

        # Classify volatility regime
        if avg_forecast_volatility < 0.15:
            regime = 'LOW'
            regime_confidence = 0.8
        elif avg_forecast_volatility < 0.25:
            regime = 'MODERATE'
            regime_confidence = 0.7
        elif avg_forecast_volatility < 0.35:
            regime = 'ELEVATED'
            regime_confidence = 0.7
        else:
            regime = 'HIGH'
            regime_confidence = 0.8

        return {
            'current_volatility': float(current_volatility),
            'forecasted_volatility': float(avg_forecast_volatility),
            'volatility_change': float(vol_change),
            'volatility_change_percent': float(vol_change_percent),
            'volatility_regime': regime,
            'regime_confidence': regime_confidence,
            'forecast_horizon': self.forecast_horizon,
            'daily_forecasts': [float(v) for v in volatility_forecast]
        }

    def _simple_volatility(self, data):
        """
        Simple volatility estimation (fallback)

        Args:
            data (pd.DataFrame): Historical price data

        Returns:
            dict: Volatility estimate
        """
        # Calculate historical volatility
        returns = data['Close'].pct_change().dropna()

        # Current volatility (30-day)
        current_vol = returns.tail(30).std() * np.sqrt(252)

        # Recent volatility trend (10-day vs 30-day)
        recent_vol = returns.tail(10).std() * np.sqrt(252)

        # Forecast based on recent trend
        vol_momentum = recent_vol - current_vol
        forecasted_vol = current_vol + (vol_momentum * 0.3)  # Dampen the forecast

        vol_change = forecasted_vol - current_vol
        vol_change_percent = (vol_change / current_vol) * 100

        # Classify regime
        if forecasted_vol < 0.15:
            regime = 'LOW'
            regime_confidence = 0.6
        elif forecasted_vol < 0.25:
            regime = 'MODERATE'
            regime_confidence = 0.6
        elif forecasted_vol < 0.35:
            regime = 'ELEVATED'
            regime_confidence = 0.6
        else:
            regime = 'HIGH'
            regime_confidence = 0.6

        return {
            'current_volatility': float(current_vol),
            'forecasted_volatility': float(forecasted_vol),
            'volatility_change': float(vol_change),
            'volatility_change_percent': float(vol_change_percent),
            'volatility_regime': regime,
            'regime_confidence': regime_confidence,
            'forecast_horizon': self.forecast_horizon,
            'method': 'simple'
        }

    def get_optimal_dte(self, forecasted_volatility):
        """
        Suggest optimal days to expiration based on volatility

        Args:
            forecasted_volatility (float): Forecasted volatility

        Returns:
            dict: DTE recommendation
        """
        if forecasted_volatility < 0.15:
            # Low volatility - go longer for more premium
            dte = 60
            rationale = "Low volatility - longer DTE for better premium collection"
        elif forecasted_volatility < 0.25:
            # Moderate volatility - standard 45 DTE
            dte = 45
            rationale = "Moderate volatility - standard 45 DTE for balanced theta/risk"
        elif forecasted_volatility < 0.35:
            # Elevated volatility - shorter DTE for safety
            dte = 30
            rationale = "Elevated volatility - shorter DTE to reduce risk"
        else:
            # High volatility - very short DTE or avoid
            dte = 21
            rationale = "High volatility - short DTE or consider avoiding"

        return {
            'recommended_dte': dte,
            'rationale': rationale,
            'volatility_level': forecasted_volatility
        }
