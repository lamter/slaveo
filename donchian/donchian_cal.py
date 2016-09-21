# coding: utf-8

import talib as tl
import pandas as pd
import numpy as np


def get_buy_donchian_channel(h_db, trend="high", is_long_trend=True, ma=None):
    """
    计算唐奇系统安买入点
    :param h_db:
    :param trend: "high" OR "low" 多头买入点和空头买入点
    :param is_long_trend:
    :param ma_short:
    :param ma_long:
    :return:
    """

    # 系统2的短周期均线和长周期均线
    mashort, malong = ma or (20, 60)

    h = h_db.copy()
    size = h.shape[0]
    buy_break_days = 20

    # # 计算 TR 和 ATR
    # h["ATR"] = tl.ATR(np.asarray(h[["high", "low", "close"]]))

    break_trend = "%s%s" % (trend, buy_break_days)  # high20 之类的

    # 计算20日高点
    if trend == "high":
        h = tl.MAX(h)

    # 计算50日均线和300日均线
    h["mashort"] = pd.rolling_mean(h["close"], mashort)
    h["malong"] = pd.rolling_mean(h["close"], malong)

    # 生成前一日收盘价
    h["pre_close"] = h.close.shift(1)

    # 生成买入点，pre_close < break_high < high
    buy = [False for _ in range(size)]
    costs = np.array([0 for _ in range(size)], dtype=np.float64)
    for i in range(buy_break_days, size):
        # 系统2
        if is_long_trend:
            if trend == 'high' and h["ma50"][i - 1] < h["ma300"][i - 1]:
                continue
            if trend == 'low' and h["ma50"][i - 1] > h["ma300"][i - 1]:
                continue
        # TODO 之后这里可以加个噪音滤波参数
        if trend == "high":
            is_buy = h.pre_close[i] < h[break_trend][i] < h[trend][i]
        elif trend == "low":
            is_buy = h.pre_close[i] > h[break_trend][i] > h[trend][i]
        else:
            raise ValueError("trend should be high OR low, not %s" % trend)
        if is_buy:
            # 买入点
            buy[i] = True
            # 买入价格
            break_pos = h[break_trend][i]
            if trend == "high":
                # 按照 low < open < 来计算
                if h.open[i] >= break_pos:
                    cost = h.open[i]
                else:
                    cost = break_pos
            else:  # trend == "low"
                if h.open[i] < break_pos:
                    cost = h.open[i]
                else:
                    cost = break_pos
            costs[i] = cost
    h["cost"] = costs
    h["buy"] = buy
    return h
