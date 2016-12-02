# coding=utf8
"""
直接通过 loadNav 函数从指定数据库中获取净值
"""

import arrow
import pymongo
import pandas as pd

# 数据库设定
MONGO_HOST = ("localhost", 27017)

DBN = "test_funddb"
COLLECTION = "test_balance"


def save_entry(entry, host=None, port=None, dbn=None, collection=None):
    """
    保存流水条目到数据库

    :param entry:
    :param host:
    :param port:
    :param dbn:
    :param collection:
    :return:
    """
    collection = get_collection(host, port, dbn, collection)
    # 保存
    collection.update({"ctime": entry.ctime}, entry.to_db(), upsert=True)


class Entry(object):
    """
    流水的条目
    """

    def __init__(self, balance, dw=0, ctime=None):
        """
        1. 直接调整权益
        2. 如果有出入金，那么在出入金后，直接使用出入金后的权益

        :param balance: 当前权益，如果有出入金，那么是出入金后的值
        :param dw: 出入金
        """
        self.balance = balance
        self.dw = 0
        self.ctime = ctime or arrow.now().datetime

    def to_db(self):
        return {k:v for k,v in self.__dict__.items() if v is not None}

def get_collection(host=None, port=None, dbn=None, collection=None):
    host = host or MONGO_HOST[0]
    port = port or MONGO_HOST[1]
    dbn = dbn or DBN
    collection = collection or COLLECTION

    # 获取原始数据
    return pymongo.MongoClient(host, port)[dbn][collection]



def get_nav(host=None, port=None, dbn=None, collection=None):
    """
    获得最新净值

    :param host:
    :param dbn:
    :param collection:
    :return:
    """
    df = cal_nav(host, port, dbn, collection)
    return df.nav.values[-1]


def cal_nav(host=None, port=None, dbn=None, collection=None):
    """
    计算净值

    :return:
    """
    collection = get_collection(host, port, dbn, collection)
    df = pd.DataFrame([d for d in collection.find()])

    if df.shape[0] == 0:
        raise ValueError("no data")

    df = df.sort_values("ctime", ascending=True)
    # 补齐入金
    df["dw"] = df["dw"].fillna(0)
    # 入金前净值
    df["pre"] = df["balance"] - df["dw"]
    # 计算涨幅
    df["rise"] = df["pre"] / df["balance"].shift(1)
    # 计算净值
    df["nav"] = df["rise"].fillna(1).cumprod()
    # 计算份额
    df["unit"] = df["balance"] / df["nav"]
    return df.drop("_id", axis=1)



