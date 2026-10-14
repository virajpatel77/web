"""
LSTM-based price prediction model for S&P 500
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import logging
import os
import joblib

logger = logging.getLogger(__name__)

# Try to import TensorFlow, but make it optional
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger.warning("TensorFlow not available. Price prediction will use simplified model.")


class PricePredictor:
    """
    LSTM-based model for predicting S&P 500 price movements
    """

    def __init__(self, lookback=60, forecast_days=5):
        """
        Initialize price predictor

        Args:
            lookback (int): Number of days to look back for prediction
            forecast_days (int): Number of days to forecast ahead
        """
        self.lookback = lookback
        self.forecast_days = forecast_days
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_trained = False
        self.model_path = 'models/price_predictor.h5'
        self.scaler_path = 'models/price_scaler.pkl'

    def prepare_data(self, data):
        """
        Prepare data for LSTM training

        Args:
            data (pd.DataFrame): Historical price data

        Returns:
            tuple: (X, y) training data
        """
        # Use Close price
        prices = data['Close'].values.reshape(-1, 1)

        # Scale data
        scaled_data = self.scaler.fit_transform(prices)

        X, y = [], []
        for i in range(self.lookback, len(scaled_data) - self.forecast_days):
            X.append(scaled_data[i - self.lookback:i, 0])
            y.append(scaled_data[i + self.forecast_days, 0])

        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        return X, y

    def build_model(self):
        """Build LSTM model"""
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not available. Cannot build LSTM model.")
            return None

        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(self.lookback, 1)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])

        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train(self, data, epochs=50, batch_size=32, validation_split=0.2):
        """
        Train the LSTM model

        Args:
            data (pd.DataFrame): Historical price data
            epochs (int): Number of training epochs
            batch_size (int): Batch size
            validation_split (float): Validation split ratio

        Returns:
            dict: Training history
        """
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not available. Using simplified prediction.")
            self.is_trained = True
            return {'loss': [0.01], 'val_loss': [0.01]}

        logger.info("Preparing training data...")
        X, y = self.prepare_data(data)

        logger.info(f"Training LSTM model with {len(X)} samples...")
        self.model = self.build_model()

        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )

        self.is_trained = True
        logger.info("Model training completed")

        # Save model
        self.save_model()

        return {
            'loss': history.history['loss'],
            'val_loss': history.history['val_loss']
        }

    def predict(self, recent_data):
        """
        Predict future price

        Args:
            recent_data (pd.DataFrame): Recent price data (at least lookback days)

        Returns:
            dict: Prediction results
        """
        if not self.is_trained:
            logger.warning("Model not trained. Using simple prediction.")
            return self._simple_prediction(recent_data)

        if not TF_AVAILABLE:
            return self._simple_prediction(recent_data)

        # Prepare input data
        prices = recent_data['Close'].values[-self.lookback:].reshape(-1, 1)
        scaled_prices = self.scaler.transform(prices)
        X = scaled_prices.reshape(1, self.lookback, 1)

        # Make prediction
        scaled_prediction = self.model.predict(X, verbose=0)
        predicted_price = self.scaler.inverse_transform(scaled_prediction)[0][0]

        current_price = recent_data['Close'].iloc[-1]
        price_change = predicted_price - current_price
        price_change_percent = (price_change / current_price) * 100

        # Determine direction and confidence
        if abs(price_change_percent) > 2:
            direction = 'up' if price_change > 0 else 'down'
            confidence = min(abs(price_change_percent) / 5, 0.9)  # Cap at 90%
        else:
            direction = 'neutral'
            confidence = 0.5

        return {
            'current_price': current_price,
            'predicted_price': predicted_price,
            'price_change': price_change,
            'price_change_percent': price_change_percent,
            'direction': direction,
            'confidence': confidence,
            'forecast_days': self.forecast_days
        }

    def _simple_prediction(self, recent_data):
        """
        Simple moving average based prediction (fallback)

        Args:
            recent_data (pd.DataFrame): Recent price data

        Returns:
            dict: Prediction results
        """
        # Use simple moving average trend
        prices = recent_data['Close'].values[-30:]
        current_price = prices[-1]

        # Calculate trend
        ma_short = np.mean(prices[-5:])
        ma_long = np.mean(prices[-20:])

        # Predict based on momentum
        momentum = (ma_short - ma_long) / ma_long
        predicted_change = current_price * momentum * 0.5  # Dampen the prediction

        predicted_price = current_price + predicted_change
        price_change_percent = (predicted_change / current_price) * 100

        if abs(price_change_percent) > 1:
            direction = 'up' if predicted_change > 0 else 'down'
            confidence = min(abs(price_change_percent) / 3, 0.7)
        else:
            direction = 'neutral'
            confidence = 0.5

        return {
            'current_price': current_price,
            'predicted_price': predicted_price,
            'price_change': predicted_change,
            'price_change_percent': price_change_percent,
            'direction': direction,
            'confidence': confidence,
            'forecast_days': self.forecast_days,
            'method': 'moving_average'
        }

    def save_model(self):
        """Save model and scaler to disk"""
        if not TF_AVAILABLE or self.model is None:
            return

        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)

        # Save model
        self.model.save(self.model_path)
        logger.info(f"Model saved to {self.model_path}")

        # Save scaler
        joblib.dump(self.scaler, self.scaler_path)
        logger.info(f"Scaler saved to {self.scaler_path}")

    def load_model(self):
        """Load model and scaler from disk"""
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not available. Cannot load model.")
            return False

        if not os.path.exists(self.model_path):
            logger.warning(f"Model file not found: {self.model_path}")
            return False

        try:
            self.model = keras.models.load_model(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            self.is_trained = True
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
