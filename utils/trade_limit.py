from datetime import date

class TradeLimiter:
    def __init__(self, config):
        self.max_trades = config.get('max_trades_per_day', 15)
        self.cooldown = config.get('cooldown_after_loss', 3)
        self.trades = []

    def exceeded(self):
        """
        Check if the maximum number of daily trades has been reached.
        """
        today = date.today()
        daily_trades = [t for t in self.trades if t.date() == today]
        return len(daily_trades) >= self.max_trades
