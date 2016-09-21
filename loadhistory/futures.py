# coding: utf-8


import pymongo
import pandas as pd
import datetime

try:
    from .newbar import NewMinuteBar, NewDayBar
except SystemError:
    pass


class LoadBase:
    """
    导入期货历史数据
    """

    def __init__(self, path, symbol):
        """

        :param path: 数据路径
        :param contract: 合约名
        :return:
        """
        self.symbol = symbol
        client = pymongo.MongoClient("localhost", 27017)
        self.db_bar1 = client["VnTrader_1Min_Db"][symbol]
        self.db_bar10 = client["VnTrader_10Min_Db"][symbol]
        self.db_day_bar1 = client["VnTrader_Daily_Db"][symbol]
        self.data = self.load(path)

    def load(self, path):
        # 取得 actionDay, 有些 date 是 trade day ,夜盘问题
        # self.get_action_day(None)
        raise NotImplementedError

    def get_action_day(self, df):
        """
        将 Index 转为
        :return:
        """
        # 下午8点肯定收盘了
        close_time = datetime.time(20)

        def action_day(dt):
            if dt.time() > close_time:
                # 日期前移1天
                return dt - datetime.timedelta(days=1)
            else:
                # 不变
                return dt

        df['datetime'] = df['datetime'].apply(action_day)
        return df

    def to_vnpy(self):
        """
        导入到vnpy的数据库中
        :return:
        """
        raise NotImplementedError


class LoadTdxMinHis(LoadBase):
    """
    从通达信的历史数据导入分钟
    """

    def load(self, path):
        df = pd.read_csv(
            path,
            # index_col='datetime',
            names=['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'position', 'settlement'],
            parse_dates={'datetime': ["date", "time"]},
            keep_date_col=True,
            engine="python",
            skip_footer=1,
            encoding='gbk',
        )

        # 获得 action day
        return self.get_action_day(df)

    def to_vnpy(self):
        """
        导入到vnpy的数据库中
        :return:
        """
        self.to_vnpy_bar1()
        self.to_vnpy_bar10()

    def to_vnpy_bar1(self):
        db_bar1 = self.db_bar1
        data = self.data
        print(u"清空数据库%s" % db_bar1)
        db_bar1.drop()
        db_bar1.insert_many(data.to_dict('record'))

    def to_vnpy_bar10(self):
        db_bar10 = self.db_bar10
        data = self.data
        # 转为10分钟K线
        bar10 = NewMinuteBar(data, 10).new()
        print(u"清空数据库%s" % db_bar10)
        db_bar10.drop()
        db_bar10.insert_many(bar10.to_dict('record'))


class LoadTdxDailyHis(LoadBase):
    """
    从通达信的历史数据导入, 日线数据
    """

    def load(self, path):
        return pd.read_csv(
            path,
            # index_col='datetime',
            names=['date', 'open', 'high', 'low', 'close', 'volume', 'position', 'settlement'],
            parse_dates={'datetime': ["date"]},
            keep_date_col=True,
            engine="python",
            skip_footer=1,
            encoding='gbk',
        )

    def to_vnpy(self):
        """
        :return:
        """
        self.to_vnpy_day_bar1()

    def to_vnpy_day_bar1(self):
        """
        分钟线计算收盘价是不准确的,因为有收盘价和结算价,有些结算价是收盘最后3分钟的平均价格
        :return:
        """
        db_day_bar1 = self.db_day_bar1
        data = self.data
        db_day_bar1.drop()
        db_day_bar1.insert(data.to_dict('record'))
