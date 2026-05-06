import logging

import requests

logger = logging.getLogger(__name__)


def _map_symbol_to_yahoo(symbol: str) -> str:
    """
    Map common exchange symbols into Yahoo Finance tickers.
    - Crypto config uses e.g. BTCUSDT; Yahoo uses BTC-USD.
    - Stocks generally match (AAPL, TSLA) and Indian tickers often include .NS/.BO already.
    """
    s = (symbol or "").strip().upper()
    if s.endswith("USDT") and len(s) > 4:
        base = s[:-4]
        return f"{base}-USD"
    return symbol


class YahooClient:
    def get_prices(self, symbols):
        prices = {}
        for sym in symbols:
            ysym = _map_symbol_to_yahoo(sym)
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ysym}"
                resp = requests.get(
                    url,
                    params={"interval": "1m", "range": "1d"},
                    timeout=10,
                    headers={
                        # Yahoo can be picky; keep it simple.
                        "User-Agent": "Mozilla/5.0",
                        "Accept": "application/json,text/plain,*/*",
                    },
                )
                resp.raise_for_status()
                data = resp.json() or {}
                result = ((data.get("chart") or {}).get("result") or [None])[0] or {}

                meta = result.get("meta") or {}
                last = meta.get("regularMarketPrice")

                if last is None:
                    indicators = (result.get("indicators") or {}).get("quote") or []
                    quote0 = indicators[0] if indicators else {}
                    closes = quote0.get("close") if isinstance(quote0, dict) else None
                    if isinstance(closes, list):
                        for v in reversed(closes):
                            if v is not None:
                                last = v
                                break

                if last is not None:
                    prices[sym] = float(last)
            except Exception as e:
                logger.error(f"Yahoo Finance fetch error for {sym} ({ysym}): {e}")

        return prices

