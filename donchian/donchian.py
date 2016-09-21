# coding: utf-8
import doctest
import talib as tl
import pandas as pd
import numpy as np


class DonchianChannel:
    """
    Donchian channel 系统
    """

    @classmethod
    def his_open_point(cls, h_db, trend="high", days=20, is_long_trend=True, ma=None):
        """
        计算 Donchian channel 历史的突破开仓点
        :param h_db:
        :param trend: "high" OR "low" 多头买入点和空头买入点
        :param days: 前 N 日的最高点
        :param is_long_trend:
        :param ma_short:
        :param ma_long:
        :return:
        """

        # 系统2的短周期均线和长周期均线
        mashort, malong = ma or (20, 60)

        h = h_db.copy()
        size = h.shape[0]

        # # 计算 TR 和 ATR
        # h["ATR"] = tl.ATR(np.asarray(h[["high", "low", "close"]]))

        # 计算20日高点
        if trend == "high":
            h["highest"] = tl.MAX(h.high.values)
        if trend == "low":
            h["lowest"] = tl.MIN(h.low.values)

        # 计算系统2的长短周期均线
        h["mashort"] = pd.rolling_mean(h["close"], mashort)
        h["malong"] = pd.rolling_mean(h["close"], malong)

        # 计算系统2的强弱, 50日均线在 300日均线上是强,否则是弱
        h["strong"] = h["mashort"] >= h["malong"]

        buy = [False for _ in range(size)]
        cost = [0 for _ in range(size)]
        # 计算买入点
        index = days
        while index < size:
            i, index = index, index + 1

            # 前days/2日没有开仓,才开仓
            if True in buy[i - int(days/2):i]:
                continue
            # 2. 系统2的判定, 系统1的判定
            if not cls._sys2(trend, h, i) and not cls._sys1(trend, h, i):
                continue

            # 3. 标记为买入
            buy[i] = True
            index += int(days/2)

            # 4. 计算买入价
            if trend == "high" and h["open"][i] > h["highest"][i-1]:
                # 直接跳开,高开
                c = h["open"][i]
            elif trend == "low" and h["open"][i] < h["lowest"][i-1]:
                # 直接跳开, 低开
                c = h["open"][i]
            else:
                # 盘中突破
                clm = "%sest" % trend
                c = h[clm][i-1]
            cost[i] = c

        h["buy"] = buy
        h["cost"] = cost

        return h

    @staticmethod
    def _sys1(trend, h, i):
        if trend == "high" and h["high"][i] > h["highest"][i-1]:
            # 今日高点高于前日的20日最高点
            return True
        elif trend == "low" and h["low"][i] < h["lowest"][i-1]:
            # 今日低点低于于前日的20日最低点
            return True
        else:
            # 系统1逆势中
            return False


    @staticmethod
    def _sys2(trend, h, i):
        """
        系统2的判定
        :return:
        """
        if trend == "high" and h["strong"][i]:
            # 系统2强势才做多
            return True
        elif trend == "low" and not h["strong"][i]:
            # 系统2弱势才做空
            return True
        else:
            # 与系统2逆势中,不操作
            return False