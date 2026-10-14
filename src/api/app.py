"""
Flask application for trading bot API and dashboard
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_fetcher import SP500DataFetcher
from volatility_analyzer import VolatilityAnalyzer
from iron_condor_strategy import IronCondorStrategy
from ml.ml_engine import MLEngine
from streaming.price_stream import PriceStreamer, DemoStreamer
from db.database import init_db, get_session
from db.position_manager import PositionManager
from db.models import Position, MLPrediction

logger = logging.getLogger(__name__)

# Global instances
price_streamer = None
ml_engine = None
position_manager = None


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__,
                template_folder='../../web/templates',
                static_folder='../../web/static')

    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change in production
    CORS(app)

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Initialize database
    init_db()

    # Initialize global objects
    global ml_engine, position_manager, price_streamer
    ml_engine = MLEngine()
    position_manager = PositionManager()

    # Try to load trained ML models
    ml_engine.load_models()

    # ====================
    # REST API ENDPOINTS
    # ====================

    @app.route('/')
    def index():
        """Serve dashboard HTML"""
        return render_template('dashboard.html')

    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'ml_trained': ml_engine.is_trained,
            'streaming': price_streamer.is_streaming if price_streamer else False
        })

    @app.route('/api/market/current')
    def get_current_market():
        """Get current market data and analysis"""
        try:
            # Fetch recent data
            fetcher = SP500DataFetcher()
            data = fetcher.fetch_historical_data(period="2y")

            if data is None:
                return jsonify({'error': 'Failed to fetch market data'}), 500

            current_price = fetcher.get_current_price()
            price_stats = fetcher.get_price_stats()

            # Analyze volatility
            vol_analyzer = VolatilityAnalyzer(data)
            vol_metrics = vol_analyzer.get_volatility_metrics()

            return jsonify({
                'price': current_price,
                'stats': price_stats,
                'volatility': vol_metrics
            })

        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/strategy/analyze', methods=['POST'])
    def analyze_strategy():
        """Analyze Iron Condor strategy with ML predictions"""
        try:
            data = request.json
            days_to_expiration = data.get('days_to_expiration', 45)

            # Fetch market data
            fetcher = SP500DataFetcher()
            historical_data = fetcher.fetch_historical_data(period="2y")
            current_price = fetcher.get_current_price()

            # Volatility analysis
            vol_analyzer = VolatilityAnalyzer(historical_data)
            vol_metrics = vol_analyzer.get_volatility_metrics()

            # Get ML predictions
            ml_predictions = None
            if ml_engine.is_trained:
                try:
                    ml_predictions = ml_engine.predict(historical_data)
                except Exception as e:
                    logger.error(f"ML prediction error: {e}")

            # Calculate Iron Condor strategy
            strategy = IronCondorStrategy(
                current_price=current_price,
                volatility=vol_metrics['current_volatility'],
                days_to_expiration=days_to_expiration
            )

            strikes = strategy.calculate_optimal_strikes()
            profit_loss = strategy.calculate_profit_loss_zones()
            probability = strategy.calculate_probability_of_profit()

            # Generate summary
            summary = {
                'current_price': current_price,
                'days_to_expiration': days_to_expiration,
                'volatility': vol_metrics['current_volatility'],
                'strikes': strikes,
                'profit_loss': profit_loss,
                'probability': probability,
                'ml_predictions': ml_predictions,
                'volatility_metrics': vol_metrics
            }

            return jsonify(summary)

        except Exception as e:
            logger.error(f"Error analyzing strategy: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ml/predict', methods=['POST'])
    def get_ml_prediction():
        """Get ML predictions"""
        try:
            if not ml_engine.is_trained:
                return jsonify({
                    'error': 'ML models not trained',
                    'message': 'Please train models first'
                }), 400

            # Fetch recent data
            fetcher = SP500DataFetcher()
            data = fetcher.fetch_historical_data(period="1y")

            # Get predictions
            predictions = ml_engine.predict(data)

            return jsonify(predictions)

        except Exception as e:
            logger.error(f"Error getting ML prediction: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ml/train', methods=['POST'])
    def train_ml_models():
        """Train ML models"""
        try:
            # Fetch training data
            fetcher = SP500DataFetcher()
            data = fetcher.fetch_historical_data(period="5y")  # More data for training

            # Train models
            result = ml_engine.train(data)

            return jsonify({
                'message': 'ML models trained successfully',
                'result': result
            })

        except Exception as e:
            logger.error(f"Error training ML models: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/positions', methods=['GET'])
    def get_positions():
        """Get all positions"""
        try:
            positions = position_manager.get_all_positions(limit=100)
            return jsonify({
                'positions': [p.to_dict() for p in positions]
            })
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/positions/open', methods=['GET'])
    def get_open_positions():
        """Get open positions"""
        try:
            positions = position_manager.get_open_positions()
            return jsonify({
                'positions': [p.to_dict() for p in positions]
            })
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/positions', methods=['POST'])
    def create_position():
        """Create a new position"""
        try:
            data = request.json

            # Create position
            position = position_manager.create_position(
                strategy_data=data['strategy'],
                ml_prediction=data.get('ml_prediction')
            )

            return jsonify({
                'message': 'Position created successfully',
                'position': position.to_dict()
            })

        except Exception as e:
            logger.error(f"Error creating position: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/positions/<int:position_id>', methods=['GET'])
    def get_position(position_id):
        """Get a specific position"""
        try:
            position = position_manager.get_position(position_id)
            if not position:
                return jsonify({'error': 'Position not found'}), 404

            return jsonify({
                'position': position.to_dict(),
                'history': [h.to_dict() for h in position_manager.get_position_history(position_id)]
            })

        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/positions/<int:position_id>/close', methods=['POST'])
    def close_position(position_id):
        """Close a position"""
        try:
            data = request.json
            exit_price = data.get('exit_price')
            exit_reason = data.get('exit_reason', 'manual')

            if not exit_price:
                # Use current price
                fetcher = SP500DataFetcher()
                data = fetcher.fetch_historical_data(period="1d")
                exit_price = fetcher.get_current_price()

            position = position_manager.close_position(
                position_id,
                exit_price,
                exit_reason
            )

            return jsonify({
                'message': 'Position closed successfully',
                'position': position.to_dict()
            })

        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/portfolio/summary')
    def get_portfolio_summary():
        """Get portfolio summary"""
        try:
            summary = position_manager.get_portfolio_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/streaming/start', methods=['POST'])
    def start_streaming():
        """Start price streaming"""
        try:
            global price_streamer

            data = request.json or {}
            use_demo = data.get('demo', False)

            if price_streamer and price_streamer.is_streaming:
                return jsonify({'message': 'Streaming already active'})

            # Create streamer
            if use_demo:
                price_streamer = DemoStreamer(update_interval=2)
            else:
                price_streamer = PriceStreamer(update_interval=5)

            # Add callback to broadcast prices
            def broadcast_price(symbol, price, timestamp):
                socketio.emit('price_update', {
                    'symbol': symbol,
                    'price': price,
                    'timestamp': timestamp
                })

            price_streamer.add_callback(broadcast_price)
            price_streamer.start()

            return jsonify({'message': 'Streaming started successfully'})

        except Exception as e:
            logger.error(f"Error starting streaming: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/streaming/stop', methods=['POST'])
    def stop_streaming():
        """Stop price streaming"""
        try:
            global price_streamer

            if price_streamer:
                price_streamer.stop()
                return jsonify({'message': 'Streaming stopped'})
            else:
                return jsonify({'message': 'No active streaming'})

        except Exception as e:
            logger.error(f"Error stopping streaming: {e}")
            return jsonify({'error': str(e)}), 500

    # ====================
    # WEBSOCKET EVENTS
    # ====================

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info('Client connected')
        emit('connection_response', {'status': 'connected'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info('Client disconnected')

    @socketio.on('request_update')
    def handle_update_request():
        """Handle client request for update"""
        try:
            # Send current market data
            fetcher = SP500DataFetcher()
            data = fetcher.fetch_historical_data(period="1d")
            current_price = fetcher.get_current_price()

            emit('market_update', {
                'price': current_price,
                'timestamp': time.time()
            })

        except Exception as e:
            logger.error(f"Error handling update request: {e}")
            emit('error', {'message': str(e)})

    # Store socketio instance for external access
    app.socketio = socketio

    return app


if __name__ == '__main__':
    import time

    # Create app
    app = create_app()

    # Run server
    logger.info("Starting Flask server...")
    app.socketio.run(app, host='0.0.0.0', port=5000, debug=True)
