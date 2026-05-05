import pandas as pd

class IndicatorLogic:
    def __init__(self, max_points=250):
        self.max_points = max_points
        self.history = {}

    def compute_all(self, price_dict):
        features = {}
        for sym, price in price_dict.items():
            if price is None:
                features[sym] = dict.fromkeys(["rsi", "macd", "ema_fast", "ema_slow", "bb_upper", "bb_lower"])
                continue

            series = self.history.setdefault(sym, [])
            series.append(float(price))
            if len(series) > self.max_points:
                series.pop(0)

            close = pd.Series(series, dtype="float64")
            if len(close) < 2:
                features[sym] = dict.fromkeys(["rsi", "macd", "ema_fast", "ema_slow", "bb_upper", "bb_lower"])
                continue

            ema_fast = close.ewm(span=12, adjust=False).mean().iloc[-1]
            ema_slow = close.ewm(span=26, adjust=False).mean().iloc[-1]
            macd = ema_fast - ema_slow

            delta = close.diff()
            gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
            loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
            
            g_val = gain.iloc[-1]
            l_val = loss.iloc[-1]
            
            if l_val == 0:
                rsi_val = 50.0 if g_val == 0 else 100.0
            else:
                rs = g_val / l_val
                rsi_val = 100 - (100 / (1 + rs))

            rolling_mean = close.rolling(window=20).mean().iloc[-1]
            rolling_std = close.rolling(window=20).std().iloc[-1]
            bb_upper = rolling_mean + (2 * rolling_std) if pd.notna(rolling_mean) and pd.notna(rolling_std) else None
            bb_lower = rolling_mean - (2 * rolling_std) if pd.notna(rolling_mean) and pd.notna(rolling_std) else None

            features[sym] = {
                "rsi": float(rsi_val) if pd.notna(rsi_val) else None,
                "macd": float(macd) if pd.notna(macd) else None,
                "ema_fast": float(ema_fast) if pd.notna(ema_fast) else None,
                "ema_slow": float(ema_slow) if pd.notna(ema_slow) else None,
                "bb_upper": float(bb_upper) if bb_upper is not None else None,
                "bb_lower": float(bb_lower) if bb_lower is not None else None,
            }
        return features
