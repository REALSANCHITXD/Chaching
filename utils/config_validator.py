import yaml
import jsonschema

def validate_config(cfg):
    """
    Validates the user configuration against the defined JSON schema.
    """
    with open('config_schema.yaml', 'r', encoding='utf-8') as f:
        schema = yaml.safe_load(f)
    jsonschema.validate(cfg, schema)

def generate_template_config(path):
    """
    Generates a default template configuration file if one is missing.
    """
    template = {
        'mode': 'paper',
        'interval': 60,
        'enable_us_stocks': True,
        'enable_crypto': True,
        'crypto_assets': ['BTCUSDT', 'ETHUSDT'],
        'us_stock_assets': ['AAPL', 'TSLA'],
        'binance': {'api_key': 'YOUR_BINANCE_KEY', 'secret_key': 'YOUR_BINANCE_SECRET'},
        'alpaca': {'api_key': 'YOUR_ALPACA_KEY', 'secret_key': 'YOUR_ALPACA_SECRET'},
        'cache': {'memory_ttl': 30, 'redis_url': 'redis://localhost:6379', 'disk_path': 'cache/'},
        'psychology': {'max_trades_per_day': 15, 'cooldown_after_loss': 3},
        'risk_management': {'max_risk_per_trade': 0.02, 'stop_loss_pct': 0.01, 'take_profit_pct': 0.02},
        'logging': {'level': 'INFO', 'file': 'bot.log'},
    }
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(template, f, sort_keys=False)
