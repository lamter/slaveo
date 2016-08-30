# coding: utf-8

import sys
import os

sys.path.append(os.path.split(os.getcwd())[0])
from unittest import TestCase, mock

from scout import BaseScout


class TestInit(TestCase):
    """
    测试 scout 的初始化
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

    def test_add_underlying_single(self):
        """
        添加单个
        :return:
        """
        self.base.add_underlying(','.join(self.codes))

    def test_add_underlying(self):
        """
        添加单个
        :return:
        """
        self.base.add_underlying(self.codes)


