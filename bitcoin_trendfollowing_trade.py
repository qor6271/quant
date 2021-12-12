import pandas as pd
import numpy as np
import time
import pyupbit
import datetime
import requests

access_key = 'upbit_access'
secret_key = 'upbit_secret'
myToken = "slack-token"


def get_ohlcv(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
    df.drop(index=df.index[-1], columns='value', inplace=True)
    return df

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)
 
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


# 로그인
upbit = pyupbit.Upbit(access_key, secret_key)
print("autotrade start")
post_message(myToken, '#coin', '자동매매 시작')

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < start_time + datetime.timedelta(seconds=10):
            krw = get_balance('KRW')
            if krw > 5000:
                df = get_ohlcv('KRW-BTC')
                buy_bp = bollinger_percent(param=[80,'up'], period = 15)
                buy_mfi = money_flow_index(param = [80,'up'], period = 10)
                buy_bp.default_setting(df)
                buy_mfi.default_setting(df)
                if buy_bp.condition(date=start_time - datetime.timedelta(days=1)) and buy_mfi.condition(date=start_time - datetime.timedelta(days=1)):
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    high_price = pyupbit.get_current_price('KRW-BTC')
                    post_message(myToken, '#coin', '매수 완료')
                    time.sleep(1)
                    krw_new = get_balance("KRW")
                    btc_new = get_balance('BTC')
                    post_message(myToken, '#coin', f'현재 잔고 KRW : {krw_new}, BTC : {btc_new}')
            time.sleep(10)
        
        btc = get_balance('BTC')
        if btc > 0.00008:
            new_price = pyupbit.get_current_price('KRW-BTC')
            high_price = max(high_price, new_price)
            if high_price * 0.8 > new_price:
                upbit.sell_market_order("KRW-BTC", btc)
                post_message(myToken, '#coin', '매도 완료')
                time.sleep(1)
                krw_new = get_balance("KRW")
                btc_new = get_balance('BTC')
                post_message(myToken, '#coin', f'현재 잔고 KRW : {krw_new}, BTC : {btc_new}')
        time.sleep(1)
    except Exception as e:
        post_message(myToken, f'#coin','error\n에러내용: {e}')
        time.sleep(1)