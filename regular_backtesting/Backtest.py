import pandas as pd
import numpy as np

class regular_Backtest():
    
    def __init__(self, price_df, estimator, seed_money = 10000000):
        self.price_df = price_df
        self.seed_money = seed_money
        self.estimator = estimator

    def date_division(self, start, end, rebal_month):
        date_section = []
        start = int(start)
        end = int(end)
        date = start
        while 1:
            date_section.append(str(date))
            date += rebal_month
            if date % 100 >= 13:
                date += 88
            if date >= end:
                date_section.append(str(date))
                break
        return date_section
                    
    def fit(self, start, end, rebal_month = None):
        self.first = True
        if rebal_month == None:
            self.section_start = start
            stocks_ratio = self.estimator.fit(self)
            self.make_balance(stocks_ratio, start, end, self.seed_money)
        else:
            date_section = self.date_division(start, end, rebal_month)
            for i in range(len(date_section) - 1):
                self.section_start = date_section[i]
                stocks_ratio = self.estimator.fit(self)
                if self.first == True:
                    self.make_balance(stocks_ratio, date_section[i], date_section[i+1], self.seed_money)
                else:
                    input_money = self.balance['total'][-1]
                    self.make_balance(stocks_ratio, date_section[i], date_section[i+1], input_money)
        
        
        #MDD
        for i, index in enumerate(self.balance.index):
            if i == 0:
                max_price = self.balance.loc[index,'total']
                MDD_list = [0]
            else:
                max_price = max(max_price, self.balance.loc[index,'total'])
                MDD_list.append(max((max_price - self.balance.loc[index,'total'])/max_price, MDD_list[-1]))
        self.balance['MDD'] = MDD_list

        self.balance.sort_index(axis=1, inplace=True)

        #CAGR
        month_section = self.date_division(start, end, 1)
        CAGR_dic = {}
        for month in range(6, len(month_section)-1):
            year = month/12
            last_money = self.balance.loc[month_section[month]:,'total'].iloc[0]
            CAGR_dic[month_section[month]] = ((last_money/self.seed_money)**(1/year) - 1) * 100
        self.CAGR = pd.Series(CAGR_dic)

        return self

    def make_balance(self, stocks_ratio, start, end, input_money, price_basis = 'close'):
        market_price = self.price_df[price_basis][stocks_ratio[0]][start:end]
        money_property = list(map(lambda x: x * input_money, stocks_ratio[1]))
        stock_amount = money_property // market_price.iloc[0]
        temp_balance = market_price * stock_amount
        temp_balance['stock'] = temp_balance.sum(axis=1)
        temp_balance['cash'] = input_money - temp_balance['stock'][0]
        temp_balance['total'] = temp_balance['stock'] + temp_balance['cash']
        temp_balance['rate_of_return'] = temp_balance['total'] / self.seed_money - 1
        if self.first == True:
            self.balance = temp_balance
            self.first =False
        else:
            self.balance = pd.concat([self.balance, temp_balance])
        return self