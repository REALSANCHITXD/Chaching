class DecisionEngine:
    def __init__(self, risk_cfg):
        self.max_risk = risk_cfg.get('max_risk_per_trade', 0.02)
        self.sl_pct = risk_cfg.get('stop_loss_pct', 0.05)
        self.tp_pct = risk_cfg.get('take_profit_pct', 0.10)
        # If you want the bot to place more frequent paper trades, lower this.
        self.signal_threshold = float(risk_cfg.get('signal_threshold', 0.0))

    def generate_signals(self, features, sentiment, prices, open_positions=None, account_equity=10000, position_sizer=None):
        orders = []
        open_positions = open_positions or {}
        
        for symbol, metrics in features.items():
            price = prices.get(symbol)
            
            # Skip if we don't have valid price or RSI data
            if not price or metrics.get('rsi') is None:
                continue

            # Demo-safety: don't keep stacking positions endlessly.
            # If a position exists for this symbol, skip new entries.
            if symbol in open_positions:
                continue
                
            # Calculate component scores
            rsi_score = (50 - metrics['rsi']) / 50.0
            
            macd_val = metrics.get('macd')
            macd_score = (macd_val / price) if macd_val else 0.0
            
            sentiment_data = sentiment.get(symbol, {})
            sentiment_score = sentiment_data.get('score', 0.0)
            
            # Combine into a final normalized score
            total_score = rsi_score + macd_score + sentiment_score
            
            # Determine order size
            if position_sizer:
                qty = position_sizer(price, 0)
            else:
                qty = (self.max_risk * account_equity) / price
                
            # Determine direction based on score
            threshold = self.signal_threshold
            if total_score > threshold:
                side = 'buy'
            elif total_score < -threshold:
                side = 'sell'
            else:
                continue
                
            # Calculate Stop Loss and Take Profit
            if side == 'buy':
                stop_loss = price * (1 - self.sl_pct)
                take_profit = price * (1 + self.tp_pct)
            else:
                stop_loss = price * (1 + self.sl_pct)
                take_profit = price * (1 - self.tp_pct)
                
            orders.append({
                'symbol': symbol,
                'side': side,
                'qty': round(qty, 6),
                'price': price,
                'stop_loss': round(stop_loss, 6),
                'take_profit': round(take_profit, 6)
            })
            
        return orders
