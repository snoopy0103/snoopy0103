import pandas as pd

class BaseClient():
    def __init__(self, trader, Strategies):
        self.trader = trader
        self.BuySellList_df = pd.DataFrame()
        self.Strategies = Strategies
        self.Stocks = pd.DataFrame()
    
    

