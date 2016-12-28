# coding: utf-8
from itertools import chain
import datetime
import doctest
import os
import json

import arrow
import calendar
import pandas as pd

pwd = os.path.split(__file__)[0]

# 交易日类型
TRADE_DAY_TYPE_FIRST = u"首交"  # 假期后第一个交易日
TRADE_DAY_TYPE_NORMAL = u"正常"  # 正常交易日
TRADE_DAY_TYPE_FRI = u"周五"  # 正常周五
TRADE_DAY_TYPE_SAT = u"周六"  # 正常周六
TRADE_DAY_TYPE_HOLIDAY = u"假期"  # 假期
TRADE_DAY_TYPE_LAST = u"末日"  # 长假前最后一个交易日
TRADE_DAY_TYPE_HOLIDAY_FIRST = u"首假"  # 长假第一天

# 假期时间表
# H = [
#     ["2016-01-01", "2016-01-03"],  # 元旦
#     ["2016-02-06", "2016-02-14"],  # 春节
#     ["2016-04-02", "2016-04-04"],  # 清明节
#     ["2016-04-30", "2016-05-02"],  # 劳动节
#     ["2016-06-09", "2016-06-12"],  # 端午节
#     ["2016-09-15", "2016-09-18"],  # 中秋节
#     ["2016-10-01", "2016-10-09"],  # 国庆节
# ]
# HOLIDAYS = list(map(
#     lambda ds: [pd.to_datetime(ds[0]).date(), pd.to_datetime(ds[1]).date()],
#     H
# ))



closed = 0
call_auction = 1  # 集合竞价
match = 2  # 撮合
continuous_auction = 3  # 连续竞价

t = datetime.time

# 中金所股指期货日盘
CFFEX_sid = (
    [t(9, 25), t(9, 29), call_auction],  # 集合竞价
    [t(9, 29), t(9, 30), match],  # 撮合
    [t(9, 30), t(11, 30), continuous_auction],  # 连续竞价
    [t(13, 0), t(15, 0), continuous_auction],  # 连续竞价
)

# 中金所国债期货日盘
CFFEX_ndd = (
    [t(9, 10), t(9, 14), call_auction],  # 集合竞价
    [t(9, 14), t(9, 15), match],  # 撮合
    [t(9, 15), t(11, 30), continuous_auction],  # 连续竞价
    [t(13, 0), t(15, 15), continuous_auction],  # 连续竞价
)

# 郑商所日盘
CZCE_d = (
    [t(8, 55), t(8, 59), call_auction],  # 集合竞价
    [t(8, 59), t(9, 0), match],  # 撮合
    [t(9, 0), t(10, 15), continuous_auction],  # 连续竞价
    [t(10, 30), t(11, 30), continuous_auction],  # 连续竞价
    [t(13, 30), t(15, 0), continuous_auction],  # 连续竞价
)

# 郑商所夜盘
CZCE_n = (
    [t(20, 55), t(20, 59), call_auction],  # 集合竞价
    [t(20, 59), t(21, 0), match],  # 撮合
    [t(21, 0), t(23, 30), continuous_auction],  # 连续竞价
)

# 大商所日盘
DCE_d = CZCE_d
# 大商所夜盘
DCE_n = CZCE_n

# 上期所日盘
SHFE_d = CZCE_d
# 上期所夜盘
SHFE_n1 = (
    [t(20, 55), t(20, 59), call_auction],  # 集合竞价
    [t(20, 59), t(21, 0), call_auction],  # 撮合
    [t(21, 0), t(2, 30), continuous_auction],  # 连续竞价
)
# 上期所深夜盘2
SHFE_n2 = (
    [t(20, 55), t(20, 59), call_auction],  # 集合竞价
    [t(20, 59), t(21, 0), call_auction],  # 撮合
    [t(21, 0), t(1, 0), continuous_auction],  # 连续竞价
)
# 上期所深夜盘3
SHFE_n3 = (
    [t(20, 55), t(20, 59), call_auction],  # 集合竞价
    [t(20, 59), t(21, 0), call_auction],  # 撮合
    [t(21, 0), t(23, 0), continuous_auction],  # 连续竞价
)

# 期货交易时间
futures_tradeing_time = {
    # 中金所
    "IC": CFFEX_sid,  # 中证500股指
    "IF": CFFEX_sid,  # 沪深300股指
    "IH": CFFEX_sid,  # 上证50股指
    "TF": CFFEX_ndd,  # 5年国债
    "T": CFFEX_ndd,  # 10年国债

    # 郑商所
    "CF": list(chain(CZCE_d, CZCE_n)),  # 棉花
    "ZC": list(chain(CZCE_d, CZCE_n)),  # 动力煤
    "SR": list(chain(CZCE_d, CZCE_n)),  # 白砂糖
    "RM": list(chain(CZCE_d, CZCE_n)),  # 菜籽粕
    "MA": list(chain(CZCE_d, CZCE_n)),  # 甲醇
    "TA": list(chain(CZCE_d, CZCE_n)),  # PTA化纤
    "FG": list(chain(CZCE_d, CZCE_n)),  # 玻璃
    "OI": list(chain(CZCE_d, CZCE_n)),  # 菜籽油
    "WH": CZCE_d,  # 强筋麦709
    "SM": CZCE_d,  # 锰硅709
    "SF": CZCE_d,  # 硅铁709
    "RS": CZCE_d,  # 油菜籽709
    "RI": CZCE_d,  # 早籼稻709
    "PM": CZCE_d,  # 普通小麦709
    "LR": CZCE_d,  # 晚籼稻709
    "JR": CZCE_d,  # 粳稻709

    # 大商所
    "j": list(chain(DCE_d, DCE_n)),  # 焦炭
    "i": list(chain(DCE_d, DCE_n)),  # 铁矿石
    "jm": list(chain(DCE_d, DCE_n)),  # 焦煤
    "a": list(chain(DCE_d, DCE_n)),  # 黄大豆1号
    "y": list(chain(DCE_d, DCE_n)),  # 豆油
    "m": list(chain(DCE_d, DCE_n)),  # 豆粕
    "b": list(chain(DCE_d, DCE_n)),  # 黄大豆2号
    "p": list(chain(DCE_d, DCE_n)),  # 棕榈油
    ###################
    "jd": DCE_d,  # 鲜鸡蛋1709
    "l": DCE_d,  # 聚乙烯1709
    "v": DCE_d,  # 聚氯乙烯1709
    "pp": DCE_d,  # 聚丙烯1709
    "fb": DCE_d,  # 纤维板1709
    "cs": DCE_d,  # 玉米淀粉1709
    "c": DCE_d,  # 黄玉米1709
    "bb": DCE_d,  # 胶合板1709

    # 上期所
    "ag": list(chain(SHFE_d, SHFE_n1)),  # 白银1709
    "au": list(chain(SHFE_d, SHFE_n1)),  # 黄金1710
    ##################
    "pb": list(chain(SHFE_d, SHFE_n2)),  # 铅1709
    "ni": list(chain(SHFE_d, SHFE_n2)),  # 镍1709
    "zn": list(chain(SHFE_d, SHFE_n2)),  # 锌1709
    "al": list(chain(SHFE_d, SHFE_n2)),  # 铝1709
    "sn": list(chain(SHFE_d, SHFE_n2)),  # 锡1709
    "cu": list(chain(SHFE_d, SHFE_n2)),  # 铜1709
    #########
    "ru": list(chain(SHFE_d, SHFE_n3)),  # 天然橡胶1709
    "rb": list(chain(SHFE_d, SHFE_n3)),  # 螺纹钢1709
    "hc": list(chain(SHFE_d, SHFE_n3)),  # 热轧板1709
    "bu": list(chain(SHFE_d, SHFE_n3)),  # 沥青1809
    ##############
    "wr": SHFE_d,  # 线材1709
    "fu": SHFE_d,  # 燃料油1709
}

# 日盘开始
DAY_LINE = datetime.time(3)
# 夜盘开始
NIGHT_LINE = datetime.time(20, 30)
# 午夜盘
MIDNIGHT_LINE = datetime.time(20, 30)


class FutureTradeCalendar(object):
    """
    期货的交易日生成
    """

    def __init__(self, begin=None, end=None):
        """
        self.calendar 格式如下
            type  weekday    next_td   tradeday day_trade night_trade  midnight_trade
date
2016-01-01     2        5 2016-01-04 2016-01-01      True        True           True
2016-01-02     3        6 2016-01-04 2016-01-04     False       False           True

        :param begin:
        :param end:
        """

        # 每天的假期, pd.Sereis, date: type
        self.holidays = self.get_holiday_json()

        self.begin = begin or self.yearbegin()
        self.end = end or self.yearend()  # 次年1月10日
        if self.holidays.shape[0]:
            end = max(self.holidays.index)
            end = pd.to_datetime(end)
            self.end = self.end.replace(end.year + 1)

        # 交易日历
        self.calendar = self.getCalendar()

    @staticmethod
    def yearbegin():
        now = arrow.now()
        return arrow.get("%s-01-01 00:00:00" % now.year).date()

    @staticmethod
    def yearend():
        now = arrow.now()
        return arrow.get("%s-01-10 00:00:00" % (now.year + 1)).date()

    def get_holiday_json(self):
        """
        读取假期时间表
        :return:
        """
        path = os.path.join(pwd, 'holiday.json')
        return pd.read_json(path, typ="series").sort_index()

    def getCalendar(self):
        """
        生成交易日
        :return:
        """
        # 加载日历的年份
        tradecalendar = pd.DataFrame(data=pd.date_range(self.begin, self.end), columns=['date'])

        # 标记普周末的日期类型
        types, weekdays = self._weekend_trade_day_type(tradecalendar["date"])
        tradecalendar["type"] = types
        tradecalendar["weekday"] = weekdays
        tradecalendar["weekday"] += 1
        tradecalendar = tradecalendar.set_index("date", drop=False)

        # 标记长假的日期类型
        tradecalendar = self._holiday_trade_day_type(tradecalendar)

        # 标记交易状态
        tradecalendar = self._tradestatus(tradecalendar)

        return tradecalendar

    def _weekend_trade_day_type(self, dates):
        types = []
        weekdays = []
        for dt in dates:
            weekday = dt.date().weekday()
            # 后处理正常交易日
            if weekday == calendar.MONDAY:
                # 假期后第一个交易日
                _types = TRADE_DAY_TYPE_FIRST
            elif weekday == calendar.FRIDAY:
                # 正常周五
                _types = TRADE_DAY_TYPE_FRI
            elif weekday == calendar.SATURDAY:
                # 正常周六
                _types = TRADE_DAY_TYPE_SAT
            elif weekday == calendar.SUNDAY:
                # 假期
                _types = TRADE_DAY_TYPE_HOLIDAY
            else:
                # 正常交易日
                _types = TRADE_DAY_TYPE_NORMAL

            types.append(_types)
            weekdays.append(weekday)
        return types, weekdays

    def _holiday_trade_day_type(self, tradecalendar):
        """
        节假日的日期类型
        :param dates:
        :return:
        """
        tradecalendar = tradecalendar.copy()
        _type = tradecalendar["type"].to_dict()
        _type.update(self.holidays.to_dict())
        tradecalendar["type"] = pd.Series(_type)

        return tradecalendar

    def _tradestatus(self, tradecalendar):
        tradecalendar = tradecalendar.copy()
        # 下一交易日
        next_td = tradecalendar[(tradecalendar["type"] == TRADE_DAY_TYPE_FIRST)
                                | (tradecalendar["type"] == TRADE_DAY_TYPE_NORMAL)
                                | (tradecalendar["type"] == TRADE_DAY_TYPE_FRI)
                                | (tradecalendar["type"] == TRADE_DAY_TYPE_LAST)].copy()
        # 向后移一天
        next_td['next_td'] = next_td["date"].shift(-1)

        # 获得下一个交易日, 并且向前填充, 即周六周日的下一交易日为下周一
        tradecalendar['next_td'] = next_td['next_td']
        tradecalendar['next_td'] = tradecalendar['next_td'].fillna(method='pad')

        # 当前交易日
        # 假期的当前交易日为下一交易日
        td = tradecalendar[(tradecalendar["type"] == TRADE_DAY_TYPE_SAT)
                           | (tradecalendar["type"] == TRADE_DAY_TYPE_HOLIDAY)
                           | (tradecalendar["type"] == TRADE_DAY_TYPE_HOLIDAY_FIRST)
                           ]

        tradecalendar['tradeday'] = td["next_td"]
        tradecalendar["tradeday"] = tradecalendar['tradeday'].fillna(tradecalendar["date"])

        # 最后一天的数据不完整,去掉
        tradecalendar = tradecalendar[:-1]

        # 日盘 *能* 交易的
        day_trade = pd.Series(False, index=tradecalendar.index)
        day_trade[
            (tradecalendar.type == TRADE_DAY_TYPE_FIRST)  # 假期后第一个交易日
            | (tradecalendar.type == TRADE_DAY_TYPE_NORMAL)  # 正常交易日
            | (tradecalendar.type == TRADE_DAY_TYPE_FRI)  # 正常周五
            # | (tradecalendar.type == TRADE_DAY_TYPE_SAT)  # 正常周六
            # | (tradecalendar.type == TRADE_DAY_TYPE_HOLIDAY)  # 假期
            | (tradecalendar.type == TRADE_DAY_TYPE_LAST)  # 长假前最后一个交易日
            # | (tradecalendar.type == TRADE_DAY_TYPE_HOLIDAY_FIRST)  # 长假第一天
            ] = True
        tradecalendar["day_trade"] = day_trade

        # 夜盘 *能* 易的
        night_trade = pd.Series(False, index=tradecalendar.index)
        night_trade[
            (tradecalendar.type == TRADE_DAY_TYPE_FIRST)  # 假期后第一个交易日
            | (tradecalendar.type == TRADE_DAY_TYPE_NORMAL)  # 正常交易日
            | (tradecalendar.type == TRADE_DAY_TYPE_FRI)  # 正常周五
            # | (tradecalendar.type == TRADE_DAY_TYPE_SAT)  # 正常周六
            # | (tradecalendar.type == TRADE_DAY_TYPE_HOLIDAY)  # 假期
            # | (tradecalendar.type == TRADE_DAY_TYPE_LAST)  # 长假前最后一个交易日
            # | (tradecalendar.type == TRADE_DAY_TYPE_HOLIDAY_FIRST)  # 长假第一天
            ] = True
        tradecalendar["night_trade"] = night_trade

        # 午夜盘不能交易的, 所有假日
        midnight_trade = pd.Series(False, index=tradecalendar.index)
        midnight_trade[
            # (tradecalendar.type == TRADE_DAY_TYPE_FIRST)  # 假期后第一个交易日
            (tradecalendar.type == TRADE_DAY_TYPE_NORMAL)  # 正常交易日
            | (tradecalendar.type == TRADE_DAY_TYPE_FRI)  # 正常周五
            | (tradecalendar.type == TRADE_DAY_TYPE_SAT)  # 正常周六
            # | (tradecalendar.type == TRADE_DAY_TYPE_HOLIDAY)  # 假期
            | (tradecalendar.type == TRADE_DAY_TYPE_LAST)  # 长假前最后一个交易日
            # | (tradecalendar.type == TRADE_DAY_TYPE_HOLIDAY_FIRST)  # 长假第一天
            ] = True
        tradecalendar["midnight_trade"] = midnight_trade

        return tradecalendar

    def _holiday_tradestatus(self, tradecalendar):
        """
        长假的交易状态
        :param tradecalendar:
        :return:
        """

    def get_tradeday(self, now):
        """
        返回一个日期的信息
        :param now:
        :return: bool(是否交易时段), 当前交易日
        >>> now = datetime.datetime(2016,10, 25, 0, 0, 0) # 周五的交易日是下周一
        >>> futureTradeCalendar.get_tradeday(now)
        (True, Timestamp('2016-10-25 00:00:00'))

        """

        t = now.time()
        day = self.calendar.ix[now.date()]
        if DAY_LINE < t < NIGHT_LINE:
            # 日盘, 当前交易日
            return day.day_trade, day.tradeday
        elif NIGHT_LINE < t:
            # 夜盘，下一个交易日
            return day.night_trade, day.next_td
        else:
            # 午夜盘，已经过了零点了，当前交易日
            return day.midnight_trade, day.tradeday

    def get_tradeday_opentime(self, tradeday):
        """
        获得交易日的起始日，比如长假后第一个交易日的起始日应该为节前的最后一个交易日
        :param tradeday: date() OR datetime(2016, 12, 12)
        :return:
        """

        calendar = self.calendar[self.calendar.next_td == tradeday]
        return calendar.index[0].date()


# 交易日历
futureTradeCalendar = FutureTradeCalendar()

futures = list(futures_tradeing_time.keys())
futures.sort()


def get_trading_status(future, now=None, ahead=0, delta=0):
    """
    >>> get_trading_status('rb', now=datetime.time(10,0,0), delta=10)
    3
    >>> future = 'ag'
    >>> today = datetime.date.today()
    >>> for b, e, s in futures_tradeing_time[future]:
    ...     now = datetime.datetime.combine(today, b) + datetime.timedelta(seconds=30)
    ...     s == get_trading_status(future, now.time(), ahead=10, delta=10)
    ...
    True
    True
    True
    True
    True
    True
    True
    True
    >>> get_trading_status(future, datetime.time(0,5,10), ahead=10, delta=10)
    3
    >>> get_trading_status(future, datetime.time(23,59,59), ahead=10, delta=10)
    3
    >>> get_trading_status('ag', datetime.time(0, 0, 0), ahead=10, delta=10)
    3
    >>> get_trading_status('IC', delta=10)
    3

    :param future:
    :param now:
    :param ahead: 提前结束 10, 提前 10秒结束
    :param delta: 延迟开始 5, 延迟5秒开始
    :return:

    """

    if now is None:
        now = arrow.now().time()
    # 时间列表
    trading_time = futures_tradeing_time[future]
    for b, e, s in trading_time:
        # 计算延迟
        if delta != 0:
            b = datetime.datetime.combine(datetime.date.today(), b) + datetime.timedelta(seconds=delta)
            b = b.time()
        if ahead != 0:
            e = datetime.datetime.combine(datetime.date.today(), e) - datetime.timedelta(seconds=ahead)
            e = e.time()
        if b <= now < e or (e < b <= now or now < e < b):  # 后一种情况跨天了
            # 返回对应的状态
            return s
    else:
        # 不在列表中则为休市状态
        return closed


def is_any_trading(now=None, delta=0, ahead=0):
    """
    >>> import datetime
    >>> is_any_trading(datetime.datetime(2016, 10, 22, 15, 56 ,24))
    False

    至少有一个品种在交易中
    :return:
    """
    now = now or datetime.datetime.now()
    is_trade, tradeday = futureTradeCalendar.get_tradeday(now)
    if not is_trade:
        # 当前日/夜/午夜盘不开盘
        return False

    for f in futures:
        if get_trading_status(f, now.time(), delta, ahead) != closed:
            return True
    else:
        return False

# if __name__ == "__main__":
#     doctest.testmod()
