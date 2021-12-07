import pandas as pd
import numpy as np

class ratio_adjustment():
    def __init__(self, stocks, ratio):
        self.stocks = stocks
        self.ratio = ratio
    
    def fit(self, test_class):
        return [self.stocks, self.ratio]


def rate_of_return(start, end, price_df, code):
    code_price = price_df['closing_price'][code][start:end]
    return code_price / code_price[0] - 1
    