import numpy as np
import pandas as pd

class single_Backtest():
    def __init__(self, price_df, stock, buy_estimators, sell_estimators, seed_money = 10000000, trading_timing = 'closing_price', stop_loss=-1, breakout_buy = False):
        # trading_timing = 'closing_price'
        # stop_loss : 고점대비 수익률 얼마일때 손절할지
        # breakout_buy : 전일 고점 돌파할 경우 매수

        self.price_df = price_df.copy()
        self.stock = stock
        self.buy_estimators = buy_estimators
        self.sell_estimators = sell_estimators
        self.seed_money = seed_money
        self.trading_timing = trading_timing
        self.stop_loss = stop_loss
        self.breakout_buy = breakout_buy
        
    def default_setting(self):
        first_col = []
        second_col = []
        for col in self.price_df.columns:
            first_col.append(col[1])
            second_col.append(col[0])
        self.price_df.columns = [first_col,second_col]
        self.price_single = self.price_df[self.stock]

    def make_balance(self, yesterday, today, form):
        if form == 'buy':
            self.stock_number = self.balance['cash'][yesterday] // self.price_single[self.trading_timing][today]
            self.balance['stock'][today] = self.price_single[self.trading_timing][today] * self.stock_number
            self.balance['cash'][today] = self.balance['cash'][yesterday] - self.balance['stock'][today]
            self.high_price = self.price_single['high_price'][today]
            
        elif form == 'sell':
            temp_cash = self.price_single[self.trading_timing][today] * self.stock_number
            self.stock_number = 0
            self.balance['stock'][today] = 0
            self.balance['cash'][today] = self.balance['cash'][yesterday] + temp_cash
        
        elif form == 'keep':
            if self.stock_number == 0:
                self.balance['stock'][today] = 0
            else:    
                self.balance['stock'][today] = self.price_single[self.trading_timing][today] * self.stock_number
                self.high_price = max(self.high_price, self.price_single['high_price'][today])
            self.balance['cash'][today] = self.balance['cash'][yesterday]

        self.balance['total'][today] = self.balance['cash'][today] + self.balance['stock'][today]

    def fit(self, start, end):
        self.default_setting()
        for buy in self.buy_estimators:
            buy.default_setting(self.price_single)
        for sell in self.sell_estimators:
            sell.default_setting(self.price_single)

        self.balance = pd.DataFrame(columns = ['cash','stock','total'], index = self.price_single.loc[start:end].index)
        self.balance.iloc[0] = [self.seed_money,0,self.seed_money]
        self.stock_number = 0
        self.high_price = 1
        for idx, today in enumerate(self.balance.index[1:], start=1):
            yesterday = self.balance.index[idx-1]
            if self.breakout_buy == True:
                buy_condition = self.price_single['high_price'][yesterday] < self.price_single['high_price'][today]
            elif self.breakout_buy == False:
                buy_condition = 1
            sell_condition = 1
            for buy in self.buy_estimators:
                if buy_condition == 0:
                    break
                buy_condition *= buy.condition(yesterday)
            for sell in self.sell_estimators:
                if sell_condition == 0:
                    break
                sell_condition *= sell.condition(yesterday)
            if buy_condition and self.stock_number == 0:
                self.make_balance(yesterday, today, 'buy')
            elif (sell_condition or (self.price_single['low_price'][yesterday]/self.high_price - 1 < self.stop_loss)) and self.stock_number != 0:
                self.make_balance(yesterday, today, 'sell')
            else:
                self.make_balance(yesterday, today, 'keep')