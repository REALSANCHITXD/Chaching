import os
import asyncio
import requests
import yaml
from datetime import datetime
from functools import partial

from data_sources.binance_feed import BinanceClient
from data_sources.alpaca_feed import AlpacaClient
from data_sources.sentiment_finbert import FinBERTSentiment

from strategies.indicator_logic import IndicatorLogic
from strategies.decision_engine import DecisionEngine

from executors.binance_executor import BinanceExecutor
from executors.alpaca_executor import AlpacaExecutor
from executors.paper_executor import PaperExecutor

from utils.logger import setup_logger
from utils.market_calendar import MarketCalendar
from utils.risk_manager import calculate_position_size
from utils.async_fetcher import AsyncFetcher
from utils.cache_manager import CacheManager
from utils.config_validator import validate_config, generate_template_config
from utils.shutdown_handler import GracefulShutdown
from utils.trade_limit import TradeLimiter


class TradingBot:
    def __init__(self, config_path="config.yaml"):
        # We need to initialize shutdown early just in case load_config fails or takes time
        self.shutdown = GracefulShutdown()
        self.config = self._load_config(config_path)
        self.logger = setup_logger(self.config)
        
        # Initialize utilities
        self.calendar = MarketCalendar()
        self.trade_limiter = TradeLimiter(self.config.get('psychology', {}))
        self.cache = CacheManager(self.config.get('cache', {}))
        self.fetcher = AsyncFetcher()
        
        # Initialize clients
        self.binance = BinanceClient(self.config.get('binance', {}))
        self.alpaca = AlpacaClient(self.config.get('alpaca', {}))
        self.sentiment_model = FinBERTSentiment()
        
        # Initialize strategies
        self.tai = IndicatorLogic()
        self.de_engine = DecisionEngine(self.config.get('risk_management', {}))
        
        # Initialize executor lazily based on mode
        self.executor = self._initialize_executor()
        
        # Using a dictionary for faster O(1) position lookups {symbol: position_data}
        self.positions = {}

    def _load_config(self, path):
        if not os.path.exists("config.template.yaml"):
            generate_template_config("config.template.yaml")
        
        try:
            with open(path, 'r') as file:
                cfg = yaml.safe_load(file)
            validate_config(cfg)
            return cfg
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {path} not found. Please create it or copy from config.template.yaml.")

    def _initialize_executor(self):
        mode = self.config.get('mode', 'paper')
        if mode == 'live_crypto':
            return BinanceExecutor(self.config.get('binance', {}))
        elif mode == 'live_stocks':
            return AlpacaExecutor(self.config.get('alpaca', {}))
        else:
            return PaperExecutor()

    def update_position(self, order):
        symbol = order['symbol']
        side = order['side']
        qty = order['qty']
        price = order['price']
        
        if symbol in self.positions and self.positions[symbol]['side'] == side:
            pos = self.positions[symbol]
            total_qty = pos['qty'] + qty
            # Calculate Volume Weighted Average Price (VWAP) cleanly
            new_entry_price = ((pos['entry_price'] * pos['qty']) + (price * qty)) / total_qty
            
            pos['entry_price'] = new_entry_price
            pos['qty'] = total_qty
            pos['timestamp'] = datetime.utcnow().isoformat()
        else:
            self.positions[symbol] = {
                'symbol': symbol,
                'side': side,
                'qty': qty,
                'entry_price': price,
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _post_dashboard_update(self, loop, payload):
        """Run blocking POST requests in an executor."""
        try:
            await loop.run_in_executor(
                None,
                partial(requests.post, 'http://localhost:5000/api/update', json=payload, timeout=5)
            )
        except Exception as e:
            self.logger.error(f"Dashboard update failed: {e}")

    async def main_loop(self):
        mode = self.config.get('mode', 'paper')
        self.logger.info(f"Starting bot in {mode} mode...")
        
        loop = asyncio.get_running_loop()
        interval = self.config.get('interval', 60)
        news_queries = self.config.get('news_queries', [])
        
        while not self.shutdown.triggered:
            if self.trade_limiter.exceeded():
                await asyncio.sleep(interval)
                continue

            # Async fetch + caching
            prices = await self.cache.get_or_fetch(
                "prices", 
                self.fetcher.fetch_prices, 
                self.binance, 
                self.alpaca, 
                self.config, 
                ttl=interval
            )

            features = self.tai.compute_all(prices)
            sentiment = await self.sentiment_model.analyze_per_asset(news_queries)

            orders = self.de_engine.generate_signals(
                features, 
                sentiment, 
                prices,
                position_sizer=calculate_position_size
            )

            for order in orders:
                if self.shutdown.triggered:
                    break
                self.executor.execute(order)
                self.update_position(order)

            current_positions = list(self.positions.values())

            # Non-blocking Dashboard update
            payload = {
                'positions': current_positions, 
                'price': prices, 
                'session': self.calendar.get_session()
            }
            # Fire and forget the dashboard update using loop.create_task
            loop.create_task(self._post_dashboard_update(loop, payload))

            await asyncio.sleep(interval)

        self._shutdown_sequence()

    def _shutdown_sequence(self):
        """Handle final tasks before the bot exits completely."""
        self.logger.info("Initiating shutdown sequence...")
        self.logger.info("Shutdown complete.")

    def run(self):
        """Entry point to run the bot."""
        loop = asyncio.get_event_loop()
        self.shutdown.register_signals(loop)
        try:
            loop.run_until_complete(self.main_loop())
        finally:
            loop.close()


if __name__ == '__main__':
    bot = TradingBot("config.yaml")
    bot.run()

