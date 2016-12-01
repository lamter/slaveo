# coding: utf-8

import pandas as pd


class NewBar:
    """
    计算单位周期K线计算大周期K线
    """

    def __init__(self, bar1, t):
        self.bar1 = bar1  # 原始数据1分钟K线
        self.t = t  # 要计算t分钟K线

        # 映射
        self.ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'position': "last",
        }

    def new(self):
        # 使用 datetime ,即actionDay 作为时间序列
        if self.bar1.index.name != 'datetime':
            self.bar1 = self.bar1.set_index("datetime")

        return self.bar1.resample(
            "%sT" % self.t,
            how=self.ohlc_dict,
            closed="left",
            label="left"
        ).dropna().reset_index()


class NewMinuteBar(NewBar):
    """
    由1分钟K线计算N分钟K线
    日K线计算见 NewDayBar
    """


class NewDayBar(NewBar):
    def new(self):
        # 使用 date,即 tradingDay 作为时间序列
        if self.bar1.index.name != 'date':
            self.bar1["date"] = pd.to_datetime(self.bar1["date"])
            self.bar1 = self.bar1.set_index("date")

        return self.bar1.resample(
            "%sT" % self.t,
            how=self.ohlc_dict,
            closed="left",
            label="left"
        ).dropna().reset_index()
