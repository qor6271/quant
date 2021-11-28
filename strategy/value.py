import pandas as pd
import numpy as np

class Graham():
    def __init__(self, financial_df):
        self.financial_df = financial_df

    def fit(self, test_class):
        check_month = str(((int(test_class.section_start) - 100) // 100) * 100 + 12)
        temp_df = self.financial_df[self.financial_df[check_month]['ROA'] >= 5]
        temp2_df = temp_df[temp_df[check_month]['부채비율'] <= 50]
        stocks = list(temp2_df[check_month].sort_values(by=['PBR']).head(20).index)
        ratio = np.full(len(stocks), 1/len(stocks))
        return [stocks, ratio]