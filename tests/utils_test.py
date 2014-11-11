#!/usr/bin/env python
#-*- coding:utf-8 -*-
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
utils module tests

Authors: fanchao(fanchao@baidu.com)
Date:    2014/10/28 17:23:06
"""
import unittest

from mini_spider import errors

from mini_spider import utils


class UrlLeveTupleTest(unittest.TestCase):
    """Test UrlLevelTuple"""

    def test_tuple(self):
        """test the tuple"""

        ul = utils.UrlLevelTuple('url', 'level')
        self.assertEqual(ul.url, 'url')
        self.assertEqual(ul.level, 'level')


class UrlHtmlTupleTest(unittest.TestCase):
    """Test UrlHtmlTuple"""

    def test_tuple(self):
        """test the tuple"""

        uh = utils.UrlHtmlTuple('url', 'html')
        self.assertEqual(uh.url, 'url')
        self.assertEqual(uh.html, 'html')


class UrlQueueTest(unittest.TestCase):
    """Test UrlQueue"""

    def test_put(self):
        """test put items"""

        queue = utils.UrlQueue(1, 2)
        queue.put(utils.UrlLevelTuple('0', 0))
        item = queue.get()
        self.assertEqual(item.url, '0')
        self.assertEqual(item.level, 0)

    def test_put_no_cache(self):
        """test put items with higher level"""

        queue = utils.UrlQueue(1, 1)
        queue.put(utils.UrlLevelTuple('0', 2))
        self.assertTrue(queue.empty())

    def test_raise(self):
        """test exception raised"""

        queue = utils.UrlQueue(1, 1)
        self.assertRaises(errors.QueueEmptyError, queue.get)


if __name__ == '__main__':
    unittest.main()

