import logging
from alpaca_trade_api import REST

logger = logging.getLogger(__name__)

class AlpacaClient:
    def __init__(self, config):
        """
        Initialize the Alpaca API client for US stock trading and data.
        """
        api_key = config.get('api_key')
        secret_key = config.get('secret_key')
        
        try:
            self.client = REST(api_key, secret_key, paper=True)
        except TypeError:
            # Fallback for older alpaca-trade-api versions
            self.client = REST(api_key, secret_key)

    def get_prices(self, symbols):
        """
        Fetch the latest prices for a list of US stock symbols.
        """
        prices = {}
        try:
            # Legacy SDK path
            if hasattr(self.client, "get_barset"):
                bars = self.client.get_barset(symbols, "minute", limit=1)
                for symbol in symbols:
                    bar = bars.get(symbol)
                    if bar:
                        prices[symbol] = float(bar[0].c)
                return prices

            # Newer SDK path
            latest = self.client.get_latest_bar(symbols)
            for symbol in symbols:
                bar = latest.get(symbol) if isinstance(latest, dict) else None
                if bar and getattr(bar, "c", None) is not None:
                    prices[symbol] = float(bar.c)
                    
        except Exception as e:
            logger.error(f"Alpaca API error while fetching prices: {e}")
            
        return prices
