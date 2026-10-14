"""
Position Manager for tracking and managing Iron Condor positions
"""

from datetime import datetime
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from .models import Position, TradeHistory, MLPrediction
from .database import get_session, close_session

logger = logging.getLogger(__name__)


class PositionManager:
    """Manage Iron Condor positions and P&L tracking"""

    def __init__(self):
        self.session: Optional[Session] = None

    def _get_session(self) -> Session:
        """Get or create database session"""
        if self.session is None:
            self.session = get_session()
        return self.session

    def create_position(self, strategy_data: Dict, ml_prediction: Optional[Dict] = None) -> Position:
        """
        Create a new position

        Args:
            strategy_data: Strategy details from IronCondorStrategy
            ml_prediction: Optional ML prediction data

        Returns:
            Position: Created position object
        """
        session = self._get_session()

        position = Position(
            strategy='iron_condor',
            status='open',
            entry_date=datetime.utcnow(),
            expiration_date=strategy_data.get('expiration_date'),
            days_to_expiration=strategy_data.get('days_to_expiration', 45),
            underlying_price_at_entry=strategy_data['current_price'],
            long_put_strike=strategy_data['strikes']['long_put'],
            short_put_strike=strategy_data['strikes']['short_put'],
            short_call_strike=strategy_data['strikes']['short_call'],
            long_call_strike=strategy_data['strikes']['long_call'],
            credit_received=strategy_data['profit_loss']['estimated_credit'],
            max_profit=strategy_data['profit_loss']['max_profit'],
            max_loss=strategy_data['profit_loss']['max_loss'],
            return_on_risk=strategy_data['profit_loss']['return_on_risk'],
            probability_of_profit=strategy_data['probability']['probability_of_profit'],
            breakeven_lower=strategy_data['profit_loss']['breakeven_lower'],
            breakeven_upper=strategy_data['profit_loss']['breakeven_upper'],
            current_underlying_price=strategy_data['current_price'],
            current_pnl=0.0,
            current_pnl_percent=0.0
        )

        # Add ML prediction if available
        if ml_prediction:
            position.ml_prediction_score = ml_prediction.get('confidence')
            position.volatility_forecast = ml_prediction.get('predicted_volatility')

        session.add(position)
        session.commit()

        # Create initial trade history entry
        self.add_trade_history(
            position.id,
            strategy_data['current_price'],
            0.0,
            0.0,
            'entry',
            'Position opened'
        )

        logger.info(f"Created position #{position.id}")
        return position

    def update_position_pnl(self, position_id: int, current_price: float) -> Position:
        """
        Update position P&L based on current price

        Args:
            position_id: Position ID
            current_price: Current underlying price

        Returns:
            Position: Updated position
        """
        session = self._get_session()
        position = session.query(Position).filter(Position.id == position_id).first()

        if not position:
            raise ValueError(f"Position {position_id} not found")

        if position.status != 'open':
            logger.warning(f"Position {position_id} is not open")
            return position

        # Calculate P&L
        # Iron Condor P&L = Credit Received - Current Value
        # Simplified: based on how far price moved from entry

        # Check if price is within profit zone
        if position.breakeven_lower <= current_price <= position.breakeven_upper:
            # In profit zone - P&L approaches max profit as time passes
            # Simplified: assume 50% of max profit if in middle of zone
            pnl = position.max_profit * 0.5
        elif current_price < position.breakeven_lower:
            # Below lower breakeven - losing on put side
            distance_from_breakeven = position.breakeven_lower - current_price
            pnl = -min(distance_from_breakeven, position.max_loss)
        elif current_price > position.breakeven_upper:
            # Above upper breakeven - losing on call side
            distance_from_breakeven = current_price - position.breakeven_upper
            pnl = -min(distance_from_breakeven, position.max_loss)
        else:
            pnl = 0.0

        # Update position
        position.current_underlying_price = current_price
        position.current_pnl = pnl
        position.current_pnl_percent = (pnl / position.max_loss) * 100 if position.max_loss > 0 else 0.0
        position.updated_at = datetime.utcnow()

        session.commit()

        # Add trade history
        self.add_trade_history(
            position_id,
            current_price,
            pnl,
            position.current_pnl_percent,
            'update',
            f'P&L update: ${pnl:.2f}'
        )

        return position

    def close_position(self, position_id: int, exit_price: float, exit_reason: str = 'manual') -> Position:
        """
        Close a position

        Args:
            position_id: Position ID
            exit_price: Exit price
            exit_reason: Reason for closing

        Returns:
            Position: Closed position
        """
        session = self._get_session()
        position = session.query(Position).filter(Position.id == position_id).first()

        if not position:
            raise ValueError(f"Position {position_id} not found")

        # Calculate final P&L
        self.update_position_pnl(position_id, exit_price)

        # Close position
        position.status = 'closed'
        position.exit_date = datetime.utcnow()
        position.exit_price = exit_price
        position.exit_reason = exit_reason
        position.realized_pnl = position.current_pnl

        session.commit()

        # Add trade history
        self.add_trade_history(
            position_id,
            exit_price,
            position.realized_pnl,
            position.current_pnl_percent,
            'exit',
            f'Position closed: {exit_reason}'
        )

        logger.info(f"Closed position #{position_id} with P&L: ${position.realized_pnl:.2f}")
        return position

    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        session = self._get_session()
        return session.query(Position).filter(Position.status == 'open').all()

    def get_all_positions(self, limit: int = 100) -> List[Position]:
        """Get all positions"""
        session = self._get_session()
        return session.query(Position).order_by(Position.created_at.desc()).limit(limit).all()

    def get_position(self, position_id: int) -> Optional[Position]:
        """Get a specific position"""
        session = self._get_session()
        return session.query(Position).filter(Position.id == position_id).first()

    def add_trade_history(self, position_id: int, price: float, pnl: float,
                          pnl_percent: float, event_type: str, notes: str = None):
        """Add a trade history entry"""
        session = self._get_session()

        history = TradeHistory(
            position_id=position_id,
            underlying_price=price,
            pnl=pnl,
            pnl_percent=pnl_percent,
            event_type=event_type,
            notes=notes
        )

        session.add(history)
        session.commit()

    def get_position_history(self, position_id: int) -> List[TradeHistory]:
        """Get trade history for a position"""
        session = self._get_session()
        return session.query(TradeHistory)\
            .filter(TradeHistory.position_id == position_id)\
            .order_by(TradeHistory.timestamp.asc())\
            .all()

    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary statistics"""
        session = self._get_session()

        open_positions = self.get_open_positions()
        all_positions = session.query(Position).all()
        closed_positions = [p for p in all_positions if p.status == 'closed']

        total_pnl = sum(p.current_pnl for p in open_positions)
        total_realized_pnl = sum(p.realized_pnl for p in closed_positions if p.realized_pnl)

        win_count = len([p for p in closed_positions if p.realized_pnl and p.realized_pnl > 0])
        loss_count = len([p for p in closed_positions if p.realized_pnl and p.realized_pnl < 0])
        win_rate = (win_count / len(closed_positions) * 100) if closed_positions else 0.0

        return {
            'open_positions': len(open_positions),
            'total_positions': len(all_positions),
            'closed_positions': len(closed_positions),
            'total_unrealized_pnl': total_pnl,
            'total_realized_pnl': total_realized_pnl,
            'total_pnl': total_pnl + total_realized_pnl,
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': win_rate
        }

    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()
            self.session = None
