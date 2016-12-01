# coding: utf-8
"""
各种计算 e_ratio(优势比率) 的函数
"""
import numpy as np
import math
import pandas as pd
import talib as tl

def mfe_mae(h, days=200, period=5):
    """
    ln(1+mfe) + ln(1-mae)
    :return:
    """

    # 根据 buy 的买入信号，计算 1 ~ 200 天的 MAE 和 MFE

    days_list = list(range(0, 200, period))
    h = h.copy()

    h["ATR"] = tl.ATR(*np.asarray(h[["high", "low", "close"]].T))

    e_ratios = []
    # 信号数量
    size = h.shape[0]
    counts = h.buy.value_counts()
    buy_times = counts[True]

    # 索引
    buy_index = np.where(h.buy == True)[0]

    # 计算 E1 ~ E200, E1 就是买入当天
    for e_days in days_list:
        # 计算未来 e_days=5 天的 MFE 和 MAE
        mfe = [0 for _ in range(size)]
        mae = [0 for _ in range(size)]
        for d in buy_index:
            # MFE d : d + edays 日内，最大有利变化
            if d == size-1:
                # 最后一项忽略掉
                buy_times = buy_times - 1
                break
            cost = h.cost[d]
            atr = h.ATR[d]

            # 这里要做跌涨幅同质化， 跌50%才是跟涨200%同质，而不是跟150%同质

            high = h.high[d:d + e_days + 1].max()
            mfe[d] = math.log(high/cost) # 老杜法
#             mfe[d] = high/cost/atr # 海龟法

            low = h.low[d:d + e_days + 1].min()
            mae[d] = math.log(low/cost) # 老杜法
#             mae[d] = low/cost/atr # 海龟法

        # 对 MFE 和 MAE 求和，求平均
        e = (sum(mfe) + sum(mae)) / buy_times # 老杜法
#         e = (sum(mfe) / buy_times) / (sum(mae) / buy_times) # 海龟法

        e_ratios.append(e)

    # 生成 DataFrame
    return pd.DataFrame({"E-ratio":e_ratios}, index=days_list), h

