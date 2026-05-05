def calculate_position_size(price, volatility_modifier=0.0, account_equity=100000):
    """
    Calculates the position size based on price and account equity.
    """
    base_risk = account_equity * 0.02
    
    risk_factor = base_risk * (1 - min(0.5, volatility_modifier))
    
    return risk_factor / price
