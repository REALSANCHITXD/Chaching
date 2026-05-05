import asyncio

class AsyncFetcher:
    async def fetch_prices(self, binance, alpaca, config):
        """
        Fetches prices concurrently from configured exchanges.
        """
        tasks = []
        
        if config.get('enable_crypto'):
            crypto_assets = config.get('crypto_assets', [])
            if crypto_assets:
                tasks.append(asyncio.to_thread(binance.get_prices, crypto_assets))
                
        if config.get('enable_us_stocks'):
            us_stocks = config.get('us_stock_assets', [])
            if us_stocks:
                tasks.append(asyncio.to_thread(alpaca.get_prices, us_stocks))
                
        # Gather all price data concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for result in results:
            if isinstance(result, dict):
                prices.update(result)
            elif isinstance(result, Exception):
                # We could log the exception here if we had the logger
                pass
                
        return prices
