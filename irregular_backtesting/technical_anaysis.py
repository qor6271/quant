import numpy as np
import pandas as pd


class moving_average():
    def __init__(self, param, criterion = 'simple', period=130):
        # param = [ma_amount_of_change_values, up or down]
        # criterion = 'simple', or 'exponential'
        self.param = param
        self.criterion = criterion
        self.period = period
        self.first = False

    def default_setting(self, price_df):
        if self.first == False:
            self.first = True
            if self.criterion == 'simple':
                self.ma = price_df['close'].rolling(window=self.period).mean()
            elif self.criterion == 'exponential':
                self.ma = price_df['close'].ewm(span=self.period).mean()
            
    def condition(self, date):
        if self.param[1] == 'up':
            return self.ma.pct_change()[date] > self.param[0]
        elif self.param[1] == 'down':
            return self.ma.pct_change()[date] < self.param[0]


class stochastic():
    def __init__(self, param, criterion = 'K', period=14):
        # param = [stochastic_values, up or down] ,  stochastic_values: 0~100
        # criterion = 'K' (fast) or 'D' (slow)
        self.param = param
        self.criterion = criterion
        self.period = period
        self.first = False

    def default_setting(self, price_df):
        if self.first == False:
            self.first = True
            ndays_high = price_df['high'].rolling(window=self.period, min_periods=1).max()
            ndays_low = price_df['low'].rolling(window=self.period, min_periods=1).min()
            fast_k = (price_df['close'] - ndays_low) / (ndays_high - ndays_low) * 100
            if self.criterion == 'K':
                self.sto = fast_k
            elif self.criterion == 'D':
                self.sto = fast_k.rolling(window=3).mean()
    
    def condition(self, date):
        if self.param[1] == 'up':
            return self.sto[date] > self.param[0]
        elif self.param[1] == 'down':
            return self.sto[date] < self.param[0]


class intraday_intensity():
    def __init__(self, param, period=21):
        # param = [IIP_values, up or down] ,  IIP_values: -1~1
        self.param = param
        self.first = False
        self.period = period

    def default_setting(self, price_df):
        if self.first == False:
            self.first = True
            II = (2 * price_df['close'] - price_df['high'] - price_df['low']) \
                / (price_df['high'] - price_df['low']) * price_df['volume']
            self.IIP = II.rolling(window=self.period).sum() / price_df['volume'].rolling(window=self.period).sum() * 100
    
    def condition(self, date):
        if self.param[1] == 'up':
            return self.IIP[date] > self.param[0]
        elif self.param[1] == 'down':
            return self.IIP[date] < self.param[0]


class money_flow_index():
    def __init__(self, param, period=10):
        # param = [MFI_values, up or down] ,  MFI_values: 0~100
        self.param = param
        self.first = False
        self.period = period

    def default_setting(self, price_df):
        if self.first == False:
            self.first = True
            TP = (price_df['high'] + price_df['low'] + price_df['close']) / 3
            PMF = pd.DataFrame(index=price_df.index, columns=['stock'])
            NMF = pd.DataFrame(index=price_df.index, columns=['stock'])
            for i in range(len(price_df) - 1):
                if TP.values[i] < TP.values[i+1]:
                    PMF['stock'].values[i+1] = TP.values[i+1] * price_df['volume'].values[i+1]
                    NMF['stock'].values[i+1] = 0
                else:
                    NMF['stock'].values[i+1] = TP.values[i+1] * price_df['volume'].values[i+1]
                    PMF['stock'].values[i+1] = 0
            MFR = PMF['stock'].rolling(window=self.period).sum() / NMF['stock'].rolling(window=self.period).sum()
            self.MFI = 100 - 100 / (1 + MFR)
    
    def condition(self, date):
        if self.param[1] == 'up':
            return self.MFI[date] > self.param[0]
        elif self.param[1] == 'down':
            return self.MFI[date] < self.param[0]        


class bollinger_percent():
    def __init__(self, param, period=20):
        # param = [PB_values, up or down] ,  PB_values: 0~100
        self.param = param
        self.first = False
        self.period = period

    def default_setting(self, price_df):
        if self.first == False:
            self.first = True
            MA20 = price_df['close'].rolling(window=self.period).mean()
            stddev = price_df['close'].rolling(window=self.period).std()
            upper = MA20 + stddev * 2
            lower = MA20 - stddev * 2
            self.PB = (price_df['close'] - lower) / (upper - lower) * 100
            
    def condition(self, date):
        if self.param[1] == 'up':
            return self.PB[date] > self.param[0]
        elif self.param[1] == 'down':
            return self.PB[date] < self.param[0]


class no_deal():
    def __init__(self):
        self.first = False

    def default_setting(self, price_df):
        if self.first == False:
            self.first = True
    
    def condition(self, date):
        return False
