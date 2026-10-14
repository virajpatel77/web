#!/usr/bin/env python3
"""
Start the S&P 500 Iron Condor Trading Bot Web Server
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("S&P 500 IRON CONDOR TRADING BOT - WEB SERVER")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Starting Flask server with SocketIO...")
    logger.info("Dashboard will be available at: http://localhost:5000")
    logger.info("")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("=" * 70)

    # Create and run app
    app = create_app()
    app.socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
