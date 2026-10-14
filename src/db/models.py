"""
Database models for position tracking and trade history
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Position(Base):
    """Track open Iron Condor positions"""
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Position details
    strategy = Column(String(50), default='iron_condor')  # iron_condor, iron_butterfly, etc.
    status = Column(String(20), default='open')  # open, closed, expired

    # Entry details
    entry_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime)
    days_to_expiration = Column(Integer)
    underlying_price_at_entry = Column(Float)

    # Strike prices
    long_put_strike = Column(Float)
    short_put_strike = Column(Float)
    short_call_strike = Column(Float)
    long_call_strike = Column(Float)

    # Premium and costs
    credit_received = Column(Float)
    max_profit = Column(Float)
    max_loss = Column(Float)

    # Risk metrics
    return_on_risk = Column(Float)
    probability_of_profit = Column(Float)
    breakeven_lower = Column(Float)
    breakeven_upper = Column(Float)

    # Current status
    current_underlying_price = Column(Float)
    current_pnl = Column(Float, default=0.0)
    current_pnl_percent = Column(Float, default=0.0)

    # Exit details (when closed)
    exit_date = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)
    exit_reason = Column(String(100), nullable=True)
    realized_pnl = Column(Float, nullable=True)

    # ML predictions at entry
    ml_prediction_score = Column(Float, nullable=True)
    volatility_forecast = Column(Float, nullable=True)

    # Additional metadata
    notes = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    trade_history = relationship("TradeHistory", back_populates="position", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert position to dictionary"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'strategy': self.strategy,
            'status': self.status,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'days_to_expiration': self.days_to_expiration,
            'underlying_price_at_entry': self.underlying_price_at_entry,
            'strikes': {
                'long_put': self.long_put_strike,
                'short_put': self.short_put_strike,
                'short_call': self.short_call_strike,
                'long_call': self.long_call_strike
            },
            'premium': {
                'credit_received': self.credit_received,
                'max_profit': self.max_profit,
                'max_loss': self.max_loss
            },
            'risk_metrics': {
                'return_on_risk': self.return_on_risk,
                'probability_of_profit': self.probability_of_profit,
                'breakeven_lower': self.breakeven_lower,
                'breakeven_upper': self.breakeven_upper
            },
            'current': {
                'underlying_price': self.current_underlying_price,
                'pnl': self.current_pnl,
                'pnl_percent': self.current_pnl_percent
            },
            'ml_predictions': {
                'prediction_score': self.ml_prediction_score,
                'volatility_forecast': self.volatility_forecast
            },
            'notes': self.notes
        }


class TradeHistory(Base):
    """Track trade updates and P&L changes"""
    __tablename__ = 'trade_history'

    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey('positions.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Snapshot data
    underlying_price = Column(Float)
    pnl = Column(Float)
    pnl_percent = Column(Float)

    # Event type
    event_type = Column(String(50))  # update, entry, exit, adjustment
    notes = Column(String(200), nullable=True)

    # Relationships
    position = relationship("Position", back_populates="trade_history")

    def to_dict(self):
        """Convert history to dictionary"""
        return {
            'id': self.id,
            'position_id': self.position_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'underlying_price': self.underlying_price,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'event_type': self.event_type,
            'notes': self.notes
        }


class MLPrediction(Base):
    """Store ML model predictions"""
    __tablename__ = 'ml_predictions'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Prediction details
    model_name = Column(String(100))
    model_version = Column(String(50))
    prediction_type = Column(String(50))  # price, volatility, signal

    # Input features
    current_price = Column(Float)
    volatility = Column(Float)
    days_ahead = Column(Integer)

    # Predictions
    predicted_price = Column(Float, nullable=True)
    predicted_volatility = Column(Float, nullable=True)
    predicted_direction = Column(String(10), nullable=True)  # up, down, neutral
    confidence = Column(Float)

    # Recommendation
    recommendation = Column(String(20))  # enter, exit, hold, avoid
    optimal_strikes = Column(JSON, nullable=True)

    # Actual outcome (for model evaluation)
    actual_price = Column(Float, nullable=True)
    actual_volatility = Column(Float, nullable=True)
    prediction_accuracy = Column(Float, nullable=True)

    # Metadata
    features_used = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'prediction_type': self.prediction_type,
            'current_price': self.current_price,
            'volatility': self.volatility,
            'predicted_price': self.predicted_price,
            'predicted_volatility': self.predicted_volatility,
            'predicted_direction': self.predicted_direction,
            'confidence': self.confidence,
            'recommendation': self.recommendation,
            'optimal_strikes': self.optimal_strikes
        }
