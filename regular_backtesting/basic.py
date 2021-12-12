import pandas as pd
import numpy as np

class ratio_adjustment():
    def __init__(self, stocks, ratio):
        self.stocks = stocks
        self.ratio = ratio
    
    def fit(self, test_class):
        return [self.stocks, self.ratio]


class basic_balance():
    def __init__(self, price_df, code):
        self.price_df = price_df
        self.code = code


    def fit(self, start, end):
        self.balance = self.price_df['close'][self.code][start:end]
        self.balance = self.balance.to_frame(name='total')
        self.balance['rate_of_return'] = self.balance['total'] / self.balance['total'][0] - 1

        for i, index in enumerate(self.balance.index):
            if i == 0:
                max_price = self.balance.loc[index,'total']
                MDD_list = [0]
            else:
                max_price = max(max_price, self.balance.loc[index,'total'])
                MDD_list.append(max((max_price - self.balance.loc[index,'total'])/max_price, MDD_list[-1]))
        self.balance['MDD'] = MDD_list
    
    