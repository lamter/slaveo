# coding: utf-8

import logging
import os
import datetime as dt
from collections import OrderedDict

import pandas as pd
import tushare as ts
import numpy as np

from mymath import *


class BaseScout:
    """
    基础策略实例
    1. 有监控标的本身,如股票,期货等,直接交易其标的自身
    2. 有监控指数,则要交易其对应的证券

    初始化
    >>> setting = {"path": "scout_data", "open_indexes": "ma"}  # 配置参数
    >>> scout = BaseScout(**setting)    # 生成实例
    >>> scout.add_underlying("000025")    # 添加白名单
    >>> scout.update_quotation(price)   # 循环更新行情
    >>> scout.get_buy_order(asset_balance) # 更新行情
    >>> scout.code, amount, exc_value(asset_balance) # 记录购买

    """

    # 最低开仓手数
    MIN_OPEN_HAND = 3
    # 最大开仓金额比例
    MAX_OPEN_RATE = p2f("50%")

    # 指标类型
    INDEXES_TYPE_MA = 'ma'
    INDEXES_TYPE_FPR = 'fpr'  # 浮盈回撤

    def __init__(self, get_now, debug=False, log_handler=None, path=None, open_indexes=None, open_rate=p2f("2%"),
                 open_close_indexes=None,
                 open_close_rate=p2f("-5%")):
        """
        :param path:
        :param open_indexes:
        :return:
        """
        # 数据检查, 测试时使用, 生产环境时关闭,以加快速度
        self.debug = debug

        # 需要给定时间戳的获取方式
        self.get_now = get_now

        # 日志句柄
        self.log = log_handler or logging.getLogger()

        # 策略文件存储位置, 需要绝对路径
        self.path = path or os.path.join(os.getcwd(), "scout_data")

        # 开仓指标
        self.open_indexes = open_indexes or self.INDEXES_TYPE_MA

        # 开仓比例
        self.open_rate = open_rate

        # 首仓的清仓指标
        self.open_close_indexes = open_close_indexes or self.INDEXES_TYPE_FPR

        # 首仓的清仓回撤比例
        self.open_close_rate = open_close_rate

        self.codes_columns = OrderedDict([
            # "index",  # 要监控价格的标的,比如股票,或者指数
            ("code", None),  # 对应的标的,股票的话就是自身,指数的话就是对应的基金
            ("open_ma", None),  # 采用均线作为开仓指标
            ("close", None),  # 昨日收盘均线
            ("open_position", False),  # True 处于开仓状态
            ("times", 0),  # 加仓次数
            ("exc_times", 0),  # 预期加仓次数
            ("amount", 0),  # 持仓数量
            ("balance", 0),  # 累积投入的资金
            ("exc_value", 0),  # 预期本次加仓金额
            ("av_price", 0),  # 开仓均价
            ("close_fp", 0),  # 清仓浮盈, 可以为负数,浮盈小于这这个数值就清仓
            ("hand_unit", 100),  # 一手的数量
        ])
        self.codes = pd.DataFrame(columns=self.codes_columns, dtype="int")

        # 行情
        self.quotation_columns = ["name", "ask1_volume", "ask1", "bid1", "bid1_volume"]
        self.quotation = pd.DataFrame(columns=self.quotation_columns)

    def get_now(self):
        """
        需要重设时间戳的获取方式
        :return: datetime.datetime()
        """
        raise ValueError("This function need redefine!")

    def add_underlying(self, codes):
        """
        添加标的证券,即白名单
        可以在任何时候添加新的白名单
        :param codes: 数组["000001", "000002"] OR "000001, 000002"
        :return:
        """

        if isinstance(codes, str):
            codes = [c.strip() for c in codes.split(',')]

        # 股票标的
        data = self.codes_columns.copy()
        data.update({
            "code": codes,
        })
        self.codes = self.codes.append(
            pd.DataFrame(
                data,
                index=codes,
            ),
        )

        # 数据类型
        self.codes.times = self.codes.times.astype(np.int16)
        self.codes.exc_times = self.codes.exc_times.astype(np.int16)
        self.codes.amount = self.codes.amount.astype(np.int32)

        # 重设开仓指标
        self.reset_open_indexes()

    def update_quotation(self, price):
        """
        获取行情
        :param price: 实时行情
        :return:
        """
        # 刷新行情
        self.refresh_quotation(price)

        # 达到开仓条件的
        self.touch_open_indexes()

        # 计算开仓价格
        self.cal_open_position()

    def refresh_quotation(self, price):
        """
        :param price: pd.DataFrame() 传进来之前需要根据处理好 self.quotation_columns 处理好 columns
        :return:
        """

        assert isinstance(self.quotation, pd.DataFrame)

        if self.debug:
            assert isinstance(price, pd.DataFrame)
            if list(price.columns.values) != list(self.quotation.columns.values):
                raise ValueError("columns of quotation err!")

        self.quotation = price.copy()

    def reset_open_indexes(self):
        """
        重设开仓指标
        可以在任何时候重设,一般需要在开盘前重设一次
        :return:
        """
        yesterday = self.get_now() - dt.timedelta(days=1)
        yes_str = yesterday.strftime("%Y-%m-%d")
        # 从 tushare 中获取历史数据
        his = ts.get_hists(list(self.codes.index), start=yes_str, end=yes_str, pause=1)
        his = his[["code", "ma5", "close"]].set_index("code")

        if self.open_indexes == self.INDEXES_TYPE_MA:
            # 根据均线设置开仓指标
            self.codes.open_ma = his["ma5"]
            self.codes.close = his["close"]
        else:
            raise ValueError("未知的开仓指标类型 %s " % self.open_indexes)

    def touch_open_indexes(self):
        """
        选出达到开仓条件的标的
        :return:
        """
        quo = self.quotation

        assert isinstance(quo, pd.DataFrame)

        if self.open_indexes == self.INDEXES_TYPE_MA:
            # 合并数据
            ma = pd.merge(self.codes[["open_ma", "close"]], quo[["bid1"]], left_index=True, right_index=True)
            # 昨日收盘价 < 均线,且 买一价 > 均线
            ma["open_position"] = ma.bid1 > ma.open_ma
            self.codes.open_position = ma.open_position
            if self.debug:
                open_num = ma.open_position.value_counts()[True]
                self.log.debug("%s 个标的达到开仓条件 " % open_num)

    def cal_open_position(self):
        """
        计算新开仓
        :return:
        """
        # 没有任何仓位的,才执行开仓逻辑
        open_pos = self.codes[(self.codes.times == 0) & (self.codes.open_position == True)]

        for code in open_pos.index:
            self.codes.loc[code, "exc_times"] = 1

    def get_buy_order(self, asset_balance):
        """
        需要买入的标的
        :param assert_balance: 总资产
        :return:
        """
        codes = self.codes[self.codes.times != self.codes.exc_times]

        codes["change"] = codes.exc_times - codes.times

        # 后买
        buy_codes = codes[codes.change >= 1]

        # 接入行情
        buy_codes = pd.merge(buy_codes, self.quotation, left_index=True, right_index=True)

        # 先买仓位大的, 获得一个优先级列表
        # 先获得高仓位的
        buy_priority_index = buy_codes[buy_codes.exc_times > 1]

        if buy_priority_index.shape[0] > 0:
            # TODO 先获得高仓位的
            pass
        else:
            # 只有新开仓的,按总市值的一定比例开仓,比如2%, 并且最低3(self.MIN_OPEN_HAND)手
            exc_value = asset_balance * self.open_rate
            exc_amount = exc_value / buy_codes.bid1
            exc_hand = exc_amount / buy_codes.hand_unit
            exc_hand = exc_hand.apply(lambda x: max(x, self.MIN_OPEN_HAND))
            exc_amount = exc_hand * buy_codes.hand_unit
            buy_codes.exc_value = exc_amount * buy_codes.bid1
            # 最大开仓规模不超过 50% 总资产
            buy_codes = buy_codes[buy_codes.exc_value <= self.MAX_OPEN_RATE * asset_balance]

        return buy_codes

    def record_buy(self, code, amount, exc_value):
        """
        记录已买
        :param code:
        :param amount:
        :param exc_value:
        :return:
        """
        loc = self.codes.loc

        # 无论买量多少,都记为买的次数 + 1
        loc[code, "times"] += 1

        # 记录买量
        loc[code, "amount"] += amount

        # 记录投入资金
        loc[code, "balance"] += exc_value

        # 更新成本价
        loc[code, "av_price"] = loc[code, "balance"] / loc[code, "amount"]

        # 设置清仓浮盈
        if loc[code, "times"] == 1:
            # 首仓止损浮盈
            if self.open_close_indexes == self.INDEXES_TYPE_FPR:
                loc[code, "close_fp"] = - loc[code, "balance"] * self.open_close_rate

    def get_sell_order(self):
        """
        需要卖出的标的
        :param assert_balance: 总资产
        :return:
        """
        codes = self.codes[self.codes.times != self.codes.exc_times]

        codes["change"] = codes.exc_times - codes.times

        sell_codes = codes[codes.change < 0]

        # 接入行情
        sell_codes = pd.merge(sell_codes, self.quotation, left_index=True, right_index=True)

        # 先卖仓位大的, 获得一个优先级列表
        sell_priority_index = sell_codes[sell_codes.exc_times < -1].times.argsort()[::-1]

        # 排序
        sell_codes.take(sell_priority_index)

        return sell_codes

    def record_sell(self, code, amount, exc_value):
        """

        :param code:
        :param amount:
        :param exc_value:
        :return:
        """
        loc = self.codes.loc

        # 无论买量多少,都记为 0
        loc[code, "times"] = loc[code, "exc_times"]

        # 记录买量
        loc[code, "amount"] = max(0, loc[code, "amount"] - amount)

        # 记录投入资金
        loc[code, "balance"] = max(0, loc[code, "balance"] - exc_value)

        # 更新成本价
        if loc[code, "amount"] == 0:
            loc[code, "av_price"] = loc[code, "balance"] / loc[code, "amount"]

        # 设置清仓浮盈
        loc[code, "close_fp"] = self.codes_columns["close_fp"]
