from flask import Flask, render_template, jsonify, request
from datetime import datetime, timezone

import numpy as np

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# In‑memory state
positions = []
price_history = []
last_session = {}
equity_history = [100000.0]
peak_equity = 100000.0
max_drawdown = 0.0
sharpe_ratio = 0.0

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/api/positions')
def api_positions():
    return jsonify(positions)

@app.route('/api/pnl')
def api_pnl():
    total_pnl = sum(p.get('unrealized_pnl', 0) for p in positions)
    return jsonify({
        'pnl': total_pnl,
        'sharpe': round(sharpe_ratio, 2),
        'drawdown': round(max_drawdown, 2)
    })

@app.route('/api/prices')
def api_prices():
    # Return the last 30 price snapshots
    return jsonify(price_history[-30:])

@app.route('/api/session')
def api_session():
    return jsonify(last_session)

@app.route('/api/update', methods=['POST'])
def api_update():
    global positions, price_history, last_session
    global equity_history, peak_equity, max_drawdown, sharpe_ratio
    
    data = request.json

    # Debug log
    print("Update received:", data, flush=True)

    # Update positions
    positions = data.get('positions', [])

    # Compute unrealized PnL per position
    prices = data.get('price', {})
    for pos in positions:
        symbol = pos['symbol']
        entry = pos.get('entry_price', 0)
        qty   = pos.get('qty', 0)
        side  = pos.get('side', 'buy')
        current = prices.get(symbol, entry)
        if side == 'buy':
            pos['unrealized_pnl'] = round((current - entry)*qty, 2)
        else:
            pos['unrealized_pnl'] = round((entry - current)*qty, 2)

    # Calculate Real Portfolio Metrics
    total_pnl = sum(pos.get('unrealized_pnl', 0) for pos in positions)
    current_equity = 100000.0 + total_pnl
    equity_history.append(current_equity)
    
    if current_equity > peak_equity:
        peak_equity = current_equity
        
    current_drawdown = (current_equity - peak_equity) / peak_equity * 100
    if current_drawdown < max_drawdown:
        max_drawdown = current_drawdown
        
    if len(equity_history) > 2:
        returns = np.diff(equity_history) / equity_history[:-1]
        std_dev = np.std(returns)
        if std_dev != 0:
            sharpe_ratio = (np.mean(returns) / std_dev) * np.sqrt(252*390*60) # Simplified annualized
        else:
            sharpe_ratio = 0.0

    # Append a timestamped price snapshot
    snapshot = prices.copy()
    snapshot['timestamp'] = datetime.now(timezone.utc).isoformat()
    price_history.append(snapshot)

    last_session = data.get('session', {}) or {}

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
