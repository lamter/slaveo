# coding: utf-8

import pandas as pd
import numpy as np
import datetime
import os
import json

import loadhistory


class LoadFuturesContract:
    """
    加载合约
    """
    SOURCE_VNPY = 'vnpy'

    def __init__(self, path, source, his_path):
        """

        :param path:
        :return:
        """
        self.path = path  # 合约文件路径
        self.source = source  # 合约文件来源
        self.data = None  # 合约信息
        self.his_path = his_path  # 历史数据文件路径

        # 载入合约数据
        self.load()

    def load(self):
        """
        加载合约
        :return:
        """
        if self.source == self.SOURCE_VNPY:
            return self.loadFromVnpy()

    def loadFromVnpy(self):
        """
        从 vnpy 中加载
        :return:
        """
        self.data = pd.read_csv(
            self.path,
            encoding='gbk',
        )

    def toTurtle(self):
        """
        清洗格式,用于海龟法则
        :return:
        """
        hy = self.data

        # 只选期货
        hy = hy[hy.productClass == "期货"]

        # 按照交易所分组
        exchange_group = hy.groupby("exchange")

        cf = None
        # 上海期货交易所, 郑州商品交易所, 大连商品交易所, 中金所
        for g in ["SHFE", "CZCE", "DCE", "CFFEX"]:
            if cf is None:
                cf = exchange_group.get_group(g)
            else:
                cf = cf.append(exchange_group.get_group(g))

        # 标的物
        cf['future'] = cf.symbol.apply(self.filter_future)

        # 交割月
        cf['mon'] = cf.symbol.apply(self.filter_mon)

        # 通达信中导出来的历史数据文件名
        tdx = cf.symbol.apply(lambda x: x.upper() + '.txt')
        s = tdx.value_counts()
        if s[s > 1].shape[0] != 0:
            # 合约名查重
            content = 'repeat contract name!'
            raise ValueError(content)

        # 剔除当月
        today = datetime.date.today()
        m = today.strftime('%Y%m')[-3:]
        cf = cf[cf.symbol.str.endswith(m) == False]

        # 删除次月
        next_month = today + datetime.timedelta(days=1)
        while next_month.month == today.month:
            next_month += datetime.timedelta(days=1)
        nm = next_month.strftime('%Y%m')[-3:]
        cf = cf[cf.symbol.str.endswith(nm) == False]

        # 删除前月
        pre_month = today + datetime.timedelta(days=1)
        while pre_month.month == today.month:
            pre_month -= datetime.timedelta(days=1)
        pm = pre_month.strftime('%Y%m')[-3:]
        cf = cf[cf.symbol.str.endswith(pm) == False]

        # 5日成交量
        cf = self.volume_from_tdx(cf, 5)

        # 取出5日平均成交额过10亿的合约
        cf = cf[cf.amount >= 10 ** 10]

        # 取出5日成交最多的2个合约
        max_volume = cf.groupby('future').apply(lambda t: t[t.volume == t.volume.max()])

        # 获得可用于海龟策略的合约
        return max_volume

    def volume_from_tdx(self, cf, num=5):
        """
        获得5个bar的成交额
        :param p:
        :return:
        """
        # 从目录获得对应的文件名
        files = None
        for path, n, files in os.walk(self.his_path):
            files = [f for f in files if '#' in f]
            break
        files = pd.DataFrame(
            {
                'path': [os.path.join(self.his_path, f) for f in files],
                'contract': [f.split('#')[1] for f in files]
            }
        )

        # 标的物
        files['future'] = files.contract.apply(self.filter_future)
        files['future'] = files.future.apply(lambda x: x[:-4])

        # 交割月
        files['mon'] = files.contract.apply(self.filter_mon)

        old_symbols = set(cf['symbol'])

        cf = pd.merge(cf, files, left_on=['future', 'mon'], right_on=['future', 'mon'])
        new_symbols = set(cf['symbol'])

        # 检查合约是否丢失
        if old_symbols != new_symbols:
            exe = 'less: %s' % ','.join(old_symbols - new_symbols)
            exe += '\nmore: %s' % ','.join(new_symbols - old_symbols)
            raise ValueError(exe)

        # 逐个计算最近5日的交易量
        volumes = []
        prices = []
        for index in cf.index:
            path = cf['path'][index]
            symbol = cf['symbol'][index]
            his = loadhistory.LoadTdxDailyHis(path, symbol)
            # 5日成交求和
            volume = his.data["volume"][-num:].mean()
            volumes.append(volume)
            price = his.data["close"][-num:].mean()
            prices.append(price)

        cf["volume"] = pd.DataFrame(volumes, dtype=np.int)
        cf["price"] = pd.DataFrame(prices, dtype=np.int)
        amount = cf.price * cf.volume * cf.size
        amount = amount.astype(np.float)
        cf['amount'] = amount

        return cf

    @staticmethod
    def filter_future(symbol, up=True):
        nums = str(list(range(0, 10)))
        return ''.join([i.upper() for i in symbol if i not in nums])

    @staticmethod
    def filter_mon(symbol):
        nums = str(list(range(0, 10)))
        return ''.join([i.upper() for i in symbol if i in nums][-3:])

    def to_vnpy_dr(self):
        """
        用于 vnpy 的实盘缓存数据
        :return:
        """
        hy = self.data

        # 只选期货
        hy = hy[hy.productClass == "期货"]

        # 按照交易所分组
        exchange_group = hy.groupby("exchange")

        cf = None
        # 上海期货交易所, 郑州商品交易所, 大连商品交易所, 中金所
        for g in ["SHFE", "CZCE", "DCE", "CFFEX"]:
            if cf is None:
                cf = exchange_group.get_group(g)
            else:
                cf = cf.append(exchange_group.get_group(g))
        contracts = []
        for i in cf.symbol.values:
            contracts.append([i, 'CTP'])
        return json.dumps(contracts)[1:-1]

    @staticmethod
    def to_vnpy_cta_setting(cf, setting):
        """
        用于 VNPY 的 CTA_setting.json 文件的配置
        :param df:
        :return:
        """
        cf = cf.reset_index(drop=True)

        lack = []
        for i in ['name_suffix', 'className']:
            if i not in setting:
                lack.append(i)
        if lack:
            raise ValueError(u"%s not in setting" % ','.join(lack))

        df = pd.DataFrame({'vtSymbol': cf.symbol, "future": cf.future})

        # name
        name_suffix = setting.pop('name_suffix')
        df["name"] = cf.symbol.apply(lambda x: x + name_suffix)
        for k, v in setting.items():
            df[k] = v
        return df.to_dict()
