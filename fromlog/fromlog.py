# coding=utf8

class FromVnpyCtaLog(object):
    """
    用于解析 vnpy 中的 CTA 策略框架的 log
    """

    def __init__(self, connect):
        self.conn = connect  # 到 mongodb 的数据库链接


    def orderAndTrade(self, future):
        """
        查询下单下单及成交
        :return:
        """


    def warn(self, future):
        """
        查询警告信息
        :param future:
        :return:
        """

    def error(self, future):
        """
        查询报错信息
        :param future:
        :return:
        """
