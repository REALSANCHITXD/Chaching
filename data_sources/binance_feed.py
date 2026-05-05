import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException

logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self, config):
        """
        Initialize the Binance API client.
        """
        self.client = Client(config.get('api_key'), config.get('secret_key'))

    def get_prices(self, symbols):
        """
        Fetch current ticker prices for a list of cryptocurrency symbols.
        """
        prices = {}
        for symbol in symbols:
            try:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                prices[symbol] = float(ticker['price'])
            except BinanceAPIException as e:
                logger.error(f"Binance API error for {symbol}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching {symbol} from Binance: {e}")
                
        return prices
