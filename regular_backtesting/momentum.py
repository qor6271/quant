import pandas as pd
import numpy as np


class dual_momentum():
    def __init__(self, min_rate_of_return = 0.02, time_period = 12, stocks = ['A143850','A195930','A101280','A069500']):
        #stocks = S&P500 etf, 유로스탁스 etf, topix etf, kospi200 etf
        self.stocks = stocks
        self.min_rate_of_return = min_rate_of_return
        self.time_period = time_period

    def fit(self, test_class):
        present = test_class.section_start
        if int(present) % 100 <= self.time_period:
            past_six_month = str(int(present) - 88 - self.time_period)
        else:
            past_six_month = str(int(present) - self.time_period)
        if int(present) % 100 <= 1:
            past_one_month = str(int(present) - 89)
        else:
            past_one_month = str(int(present) - 1)
        past_price = test_class.price_df['close'][self.stocks][past_six_month:].iloc[0]
        present_price = test_class.price_df['close'][self.stocks][past_one_month:].iloc[0]

        if max((present_price - past_price) / past_price) > self.min_rate_of_return:
            return [[((present_price - past_price) / past_price).idxmax()], [1]]
        else:
            return [[],[]]


class relative_momentum():
    def __init__(self, stocks, time_period = 12, fip_on = False, momentum_number = 50, fip_number = 20, last_month_in = True):
        self.stocks = stocks
        self.time_period = time_period
        self.fip_on = fip_on
        self.momentum_number = momentum_number
        self.fip_number = fip_number
        self.last_month_in = last_month_in

    def actual_investment(self, start, end, price_df):
        actual_closing_price = price_df['close'][self.stocks][start:end]
        actual_rate_of_return = (actual_closing_price.iloc[-1] - actual_closing_price.iloc[0]) / actual_closing_price.iloc[0]
        actual_momentum_stock = actual_rate_of_return.sort_values(ascending=False).dropna().iloc[:self.momentum_number].index
        if self.fip_on == True:
            actual_market_price = price_df['open'][self.stocks][start:end]
            actual_date_rate = np.sign(actual_closing_price - actual_market_price)
            actual_fip = - np.sign(actual_closing_price.iloc[-1] - actual_closing_price.iloc[0]) * actual_date_rate.sum()
            actual_momentum_stock = actual_fip.loc[actual_momentum_stock].sort_values().iloc[:self.fip_number].index
        self.actual_investment_stocks = actual_momentum_stock

    def fit(self, test_class):
        if test_class.first == True:
            if int(test_class.section_start) % 100 <= self.time_period:
                past_six_month = str(int(test_class.section_start) - 88 - self.time_period)
            else:
                past_six_month = str(int(test_class.section_start) - self.time_period)
            
            self.past_date_section = test_class.date_division(past_six_month, test_class.section_start, 1)
        else:
            temp_date_section = test_class.date_division(self.past_date_section[-1], test_class.section_start, 1)
            rebal_month = len(temp_date_section)-1
            self.past_date_section = self.past_date_section[rebal_month:-1]
            self.past_date_section.extend(temp_date_section)

        if self.last_month_in == True:
            temp_index = -1
        else:
            temp_index = -2
            
        self.closing_price = test_class.price_df['close'][self.stocks][self.past_date_section[0]:self.past_date_section[temp_index]]
        self.rate_of_return_past = (self.closing_price.iloc[-1] - self.closing_price.iloc[0]) / self.closing_price.iloc[0]
        momentum_stock = self.rate_of_return_past.sort_values(ascending=False).dropna().iloc[:self.momentum_number].index

        if self.fip_on == True:
            self.market_price = test_class.price_df['open'][self.stocks][self.past_date_section[0]:self.past_date_section[temp_index]]
            self.date_rate = np.sign(self.closing_price - self.market_price)
            self.fip = - np.sign(self.closing_price.iloc[-1] - self.closing_price.iloc[0]) * self.date_rate.sum()
            momentum_stock = self.fip.loc[momentum_stock].sort_values().iloc[:self.fip_number].index

        rate = np.full(len(momentum_stock),1/len(momentum_stock))
        return [list(momentum_stock),rate]


class relative_momentum_test():
    def __init__(self, stocks, time_period = 12, section_cut = 5, rank = 1, last_month_in = True):
        self.stocks = stocks
        self.time_period = time_period
        self.section_cut = section_cut
        self.rank = rank
        self.last_month_in = last_month_in

    def fit(self, test_class):
        if test_class.first == True:
            if int(test_class.section_start) % 100 <= self.time_period:
                past_six_month = str(int(test_class.section_start) - 88 - self.time_period)
            else:
                past_six_month = str(int(test_class.section_start) - self.time_period)
            
            self.past_date_section = test_class.date_division(past_six_month, test_class.section_start, 1)
        else:
            temp_date_section = test_class.date_division(self.past_date_section[-1], test_class.section_start, 1)
            rebal_month = len(temp_date_section)-1
            self.past_date_section = self.past_date_section[rebal_month:-1]
            self.past_date_section.extend(temp_date_section)

        if self.last_month_in == True:
            temp_index = -1
        else:
            temp_index = -2
        

        self.closing_price = test_class.price_df['close'][self.stocks][self.past_date_section[0]:self.past_date_section[temp_index]]
        self.rate_of_return_past = (self.closing_price.iloc[-1] - self.closing_price.iloc[0]) / self.closing_price.iloc[0]
        self.rate_of_return_past.dropna(inplace=True)
        self.qcut = pd.qcut(self.rate_of_return_past, self.section_cut, labels=[self.section_cut - i for i in range(self.section_cut)])
        momentum_stock = self.qcut[self.qcut==self.rank].index

        rate = np.full(len(momentum_stock),1/len(momentum_stock))
        return [list(momentum_stock),rate]
