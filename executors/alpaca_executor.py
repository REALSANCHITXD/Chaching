from alpaca_trade_api import REST
class AlpacaExecutor:
    def __init__(self,cfg):
        try:
            self.client=REST(cfg['api_key'],cfg['secret_key'],paper=False)
        except TypeError:
            self.client=REST(cfg['api_key'],cfg['secret_key'])
    def execute(self,order):
        print(f"[ALPACA] {order}")
        # self.client.submit_order(**order)
