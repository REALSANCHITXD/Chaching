from binance.client import Client
class BinanceExecutor:
    def __init__(self,cfg):
        self.client=Client(cfg['api_key'],cfg['secret_key'])
    def execute(self,order):
        print(f"[BINANCE] {order}")
        # self.client.order_market(**order)
