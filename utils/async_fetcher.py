import asyncio

class AsyncFetcher:
    async def fetch_prices(self, binance, alpaca, yahoo, config):
        """
        Fetches prices concurrently from configured exchanges.
        """
        tasks = []
        mode = config.get("mode", "paper")
        use_yahoo = bool((config.get("yahoo_finance") or {}).get("enabled", mode == "paper"))
        
        if config.get('enable_crypto'):
            crypto_assets = config.get('crypto_assets', [])
            if crypto_assets:
                # In paper mode (or when enabled), fetch Yahoo prices too as a fallback.
                if use_yahoo:
                    tasks.append(asyncio.to_thread(yahoo.get_prices, crypto_assets))
                tasks.append(asyncio.to_thread(binance.get_prices, crypto_assets))
                
        if config.get('enable_us_stocks'):
            us_stocks = config.get('us_stock_assets', [])
            if us_stocks:
                # Alpaca requires keys; Yahoo works in paper mode without broker creds.
                if use_yahoo:
                    tasks.append(asyncio.to_thread(yahoo.get_prices, us_stocks))
                tasks.append(asyncio.to_thread(alpaca.get_prices, us_stocks))

        if config.get("enable_in_stocks"):
            in_stocks = config.get("in_stock_assets", [])
            if in_stocks and use_yahoo:
                tasks.append(asyncio.to_thread(yahoo.get_prices, in_stocks))
                
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
