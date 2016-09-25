# coding: utf-8

import sys
import os

sys.path.append(os.path.split(os.getcwd())[0])
from unittest import TestCase, mock

from scout import BaseScout


class TestDonchianChannel(TestCase):
    """
    测试 唐奇安通道突破买入 的初始化
    """

    def setUp(self):
        """

        :return:
        """
        self.path = "../tmp"
        self.base = BaseScout(self.path)
        self.codes = [
            "000025",  # 特力A
            "600868",  # 梅雁吉祥
        ]