import numpy as np
import pandas as pd

class single_Backtest():
    def __init__(self, price_df, stock, buy_estimators, sell_estimators, seed_money = 10000000, trading_timing = 'close', stop_loss=-1, break_high = False, break_variability=0, coin = False, fee=0):
        # trading_timing = 'close'
        # stop_loss : 고점대비 수익률 얼마일때 손절할지
        # break_high : 전일 고점 돌파할 경우 매수
        # coin : 정수 아닌 갯수로 살 수 있음
        #fee : 수수료
        
        self.price_df = price_df.copy()
        self.stock = stock
        self.buy_estimators = buy_estimators
        self.sell_estimators = sell_estimators
        self.seed_money = seed_money
        self.trading_timing = trading_timing
        self.stop_loss = stop_loss
        self.break_high = break_high
        self.break_variability =break_variability
        self.coin = coin
        self.fee = fee
        
    def default_setting(self):
        first_col = []
        second_col = []
        for col in self.price_df.columns:
            first_col.append(col[1])
            second_col.append(col[0])
        self.price_df.columns = [first_col,second_col]
        self.price_single = self.price_df[self.stock]

    def make_balance(self, yesterday, today, form, stock_price):
        if form == 'buy':
            if self.coin == True:
                self.stock_number = self.balance['cash'][yesterday] / stock_price
            else:
                self.stock_number = self.balance['cash'][yesterday] // stock_price
            self.balance['stock'][today] = stock_price * self.stock_number * (1 - self.fee)
            self.balance['cash'][today] = self.balance['cash'][yesterday] - self.balance['stock'][today]
            self.high = self.price_single['high'][today]
            
        elif form == 'sell':
            temp_cash = stock_price * self.stock_number * (1 - self.fee)
            self.stock_number = 0
            self.balance['stock'][today] = 0
            self.balance['cash'][today] = self.balance['cash'][yesterday] + temp_cash
        
        elif form == 'keep':
            if self.stock_number == 0:
                self.balance['stock'][today] = 0
            else:
                self.balance['stock'][today] = stock_price * self.stock_number
                self.high = max(self.high, self.price_single['high'][today])
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
        self.high = 1
        self.buy_signal = []
        self.sell_signal = []
        for idx, today in enumerate(self.balance.index[1:], start=1):
            yesterday = self.balance.index[idx-1]
            if self.trading_timing == 'close':
                sell_date = today
            elif self.trading_timing == 'open':
                sell_date = yesterday
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

            if self.break_high == True:
                buy_condition_plus = self.price_single['high'][yesterday] < self.price_single['high'][today]
            elif self.break_variability != 0:
                buy_condition_plus = self.break_variability * (self.price_single['high'][yesterday] - self.price_single['low'][yesterday]) < (self.price_single['high'][today] - self.price_single['open'][today])
            else:
                buy_condition_plus = True
            
            if buy_condition and buy_condition_plus:
                self.buy_signal.append(today)
            if sell_condition:
                self.sell_signal.append(today)
            
            if buy_condition and self.stock_number == 0 and buy_condition_plus:
                if self.break_high == True:
                    self.make_balance(yesterday, today, 'buy', self.price_single['high'][yesterday])
                elif self.break_variability != 0:
                    self.make_balance(yesterday, today, 'buy', self.price_single['open'][today] + self.
                    break_variability * (self.price_single['high'][yesterday] - self.price_single['low'][yesterday]))
                else:
                    self.make_balance(yesterday, today, 'buy', self.price_single[self.trading_timing][today])
            elif (sell_condition or (self.price_single['low'][sell_date]/self.high - 1 < self.stop_loss)) and self.stock_number != 0:
                if self.price_single['low'][sell_date]/self.high - 1 < self.stop_loss:
                    self.make_balance(yesterday, today, 'sell', self.high * 0.9)
                else:
                    self.make_balance(yesterday, today, 'sell', self.price_single[self.trading_timing][today])
            else:
                self.make_balance(yesterday, today, 'keep', self.price_single['close'][today])

        #rate_of_return

        self.balance['rate_of_return'] = self.balance['total'] / self.balance['total'].iloc[0] - 1

        #MDD
        for i, index in enumerate(self.balance.index):
            if i == 0:
                max_price = self.balance.loc[index,'total']
                MDD_list = [0]
            else:
                max_price = max(max_price, self.balance.loc[index,'total'])
                MDD_list.append(max((max_price - self.balance.loc[index,'total'])/max_price, MDD_list[-1]))
        self.balance['MDD'] = MDD_list

