class DecisionEngine:
    def __init__(self, risk_cfg):
        self.max_risk = risk_cfg.get('max_risk_per_trade', 0.02)
        self.sl_pct = risk_cfg.get('stop_loss_pct', 0.05)
        self.tp_pct = risk_cfg.get('take_profit_pct', 0.10)

    def generate_signals(self, features, sentiment, prices, account_equity=10000, position_sizer=None):
        orders = []
        
        for symbol, metrics in features.items():
            price = prices.get(symbol)
            
            # Skip if we don't have valid price or RSI data
            if not price or metrics.get('rsi') is None:
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
            # (Threshold lowered to 0.05 temporarily so you can see live test trades)
            if total_score > 0.05:
                side = 'buy'
            elif total_score < -0.05:
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
