# coding=utf-8
import unittest
from unittest import defaultTestLoader

# 获取所有测试用例


def get_allcase():
    discover = unittest.defaultTestLoader.discover('.', pattern="test*.py")
    suite = unittest.TestSuite()
    suite.addTest(discover)
    return suite


if __name__ == '__main__':
    # 运行所有测试用例
    runner = unittest.TextTestRunner()
    runner.run(get_allcase())
