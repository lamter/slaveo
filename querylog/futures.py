# coding: utf-8

"""
查询期货的日志
"""

import pandas as pd
import numpy as np
import pymongo


class VnpyCtaLog(object):
    """
    查询 vnpy 中的 CtaLog 的日志
    """

    def __init__(self, database, collection, host=None):
        """

        :param host: ("localhost", 27017)
        :param database:
        :param collection:
        :return:
        """
        host = host or ("localhost", 27017)
        self.ip, self.port = host

        # 建立链接
        self.client = pymongo.MongoClient(self.ip, self.port)
        self.log = self.client[database][collection]

        # 成交的数据

        self.deals = None

    def init_dealsdata(self, future="all", betime=None):
        """
        查询所有成交
        :param future:
        :param betime:
        :return:
        """

        condition = {}
        # 取出所有数据
        if future != "all":
            condition["future"] = future
        if betime:
            b, e = betime
            dt = {}
            condition["datetime"] = dt
            if b:
                dt["$gte"] = b
            if e:
                dt["$lte"] = e

        cursor = self.log.find(condition)

        count = pd.DataFrame([l for l in cursor])
        count = count[count.text == u"成交"].dropna(axis=1, how="all")

        self.deals = count

    def count_profit(self, future="all", betime=None, exclud=None):
        """
        查询指定的品种，或者全部品种
        count[count.profit < 5000] 过滤掉数值异常的部分
        :param futures:
        :return:
        """
        if self.deals is None:
            raise ValueError("run .init_dealsdata(future, betime) to get init data")

        count = self.deals.copy()

        # 多头利润
        # long = count[count.profit.apply(lambda p: not (np.isnan(p)))]

        long = count[count.type.str.contains("longOut")]
        short = count[count.type.str.contains("shortOut")]

        if exclud:
            low, high = exclud
            long = long[(low <= long.profit) & (long.profit <= high)]
            short = short[(low <= short.profit) & (short.profit <= high)]

        # long = count[count.text == u"成交"].dropna(axis=1, how="all")
        # long = long[long.profit.apply(lambda p: not (np.isnan(p)))]

        profit = pd.DataFrame({
            "long": long.groupby("future").profit.sum(),
            "short": short.groupby("future").profit.sum(),
        })
        profit = profit.fillna(0)
        profit["profit"] = profit.long + profit.short

        # 重置 future 字段
        profit.index.name = "future"
        profit = profit.reset_inddex()

        return profit.sort_values("profit", ascending=False)
