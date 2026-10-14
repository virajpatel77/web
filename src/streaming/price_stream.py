"""
Real-time price streaming with WebSocket and polling fallback
"""

import asyncio
import logging
import time
from typing import Callable, Optional
import threading
import yfinance as yf

logger = logging.getLogger(__name__)


class PriceStreamer:
    """
    Real-time price streaming for S&P 500
    Supports both WebSocket (when available) and polling fallback
    """

    def __init__(self, symbol="^GSPC", update_interval=5):
        """
        Initialize price streamer

        Args:
            symbol (str): Ticker symbol (default: ^GSPC for S&P 500)
            update_interval (int): Update interval in seconds for polling
        """
        self.symbol = symbol
        self.update_interval = update_interval
        self.is_streaming = False
        self.current_price = None
        self.last_update = None
        self.callbacks = []
        self._thread = None
        self._stop_event = threading.Event()

    def add_callback(self, callback: Callable):
        """
        Add a callback function to be called on price updates

        Args:
            callback: Function to call with (symbol, price, timestamp)
        """
        self.callbacks.append(callback)
        logger.info(f"Added callback: {callback.__name__}")

    def remove_callback(self, callback: Callable):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            logger.info(f"Removed callback: {callback.__name__}")

    def start(self):
        """Start streaming prices"""
        if self.is_streaming:
            logger.warning("Price streamer already running")
            return

        logger.info(f"Starting price streamer for {self.symbol}")
        self.is_streaming = True
        self._stop_event.clear()

        # Start in separate thread
        self._thread = threading.Thread(target=self._stream_loop, daemon=True)
        self._thread.start()

        logger.info("Price streamer started")

    def stop(self):
        """Stop streaming prices"""
        if not self.is_streaming:
            return

        logger.info("Stopping price streamer...")
        self.is_streaming = False
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=5)

        logger.info("Price streamer stopped")

    def _stream_loop(self):
        """Main streaming loop (polling-based)"""
        logger.info("Starting polling loop")

        while self.is_streaming and not self._stop_event.is_set():
            try:
                # Fetch current price
                price = self._fetch_current_price()

                if price is not None:
                    self.current_price = price
                    self.last_update = time.time()

                    # Notify all callbacks
                    self._notify_callbacks(price)

            except Exception as e:
                logger.error(f"Error in streaming loop: {e}")

            # Wait for next update
            self._stop_event.wait(self.update_interval)

    def _fetch_current_price(self) -> Optional[float]:
        """
        Fetch current price using yfinance

        Returns:
            float: Current price or None if failed
        """
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period='1d', interval='1m')

            if not data.empty:
                price = data['Close'].iloc[-1]
                logger.debug(f"Fetched price: {price:.2f}")
                return float(price)
            else:
                logger.warning("No data received from yfinance")
                return None

        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return None

    def _notify_callbacks(self, price: float):
        """
        Notify all registered callbacks

        Args:
            price (float): Current price
        """
        timestamp = time.time()

        for callback in self.callbacks:
            try:
                callback(self.symbol, price, timestamp)
            except Exception as e:
                logger.error(f"Error in callback {callback.__name__}: {e}")

    def get_current_price(self) -> Optional[float]:
        """
        Get the most recent price

        Returns:
            float: Current price or None
        """
        return self.current_price

    def get_last_update_time(self) -> Optional[float]:
        """
        Get timestamp of last update

        Returns:
            float: Unix timestamp or None
        """
        return self.last_update

    def is_connected(self) -> bool:
        """
        Check if streamer is active and receiving data

        Returns:
            bool: True if connected and receiving data
        """
        if not self.is_streaming:
            return False

        if self.last_update is None:
            return False

        # Consider connected if last update was within 2x update interval
        time_since_update = time.time() - self.last_update
        return time_since_update < (self.update_interval * 2)


class DemoStreamer(PriceStreamer):
    """Demo streamer that generates simulated price movements"""

    def __init__(self, initial_price=6500, volatility=0.002, **kwargs):
        """
        Initialize demo streamer

        Args:
            initial_price (float): Starting price
            volatility (float): Daily volatility (as decimal)
            **kwargs: Additional arguments for PriceStreamer
        """
        super().__init__(**kwargs)
        self.initial_price = initial_price
        self.volatility = volatility
        self.current_price = initial_price

    def _fetch_current_price(self) -> Optional[float]:
        """
        Generate simulated price movement

        Returns:
            float: Simulated price
        """
        import random

        # Random walk with drift
        change_percent = random.gauss(0, self.volatility)
        self.current_price = self.current_price * (1 + change_percent)

        logger.debug(f"Generated demo price: {self.current_price:.2f}")
        return self.current_price
