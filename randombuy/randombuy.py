# coding: utf-8

import doctest

# 假设平均10天开仓一次

def get_random_buy(h_buy, period=10):
    """

    :param h_buy: pd.DataFrame(columns=["cost", "high", "low"])
    :param p:
    :return:
    """
    import pandas as pd
    import random
    h_buy = h_buy.copy()
    size = h_buy.shape[0]

    # 随机生成买入信号的 index, 平均开仓频率
    num = int(size / period)

    buy_index = random.sample(range(size), num)
    buy = [False for _ in range(size)]
    for i in buy_index:
        buy[i] = True

    # 过滤掉连续出现买入信号的情况
    for i in range(size - 1, 0, -1):
        if buy[i - 1] == True:
            buy[i] = False

    h_buy["buy"] = buy

    # 同时生成买入价
    h_buy["cost"] = (h_buy["high"] + h_buy["low"]) / 2

    return h_buy


if __name__ == "__main__":
    doctest.testmod()