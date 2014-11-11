#!/usr/bin/env python
#-*- coding:utf-8 -*-
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
spider module tests

Authors: fanchao(fanchao@baidu.com)
Date:    2014/10/28 17:23:06
"""
import unittest


from mini_spider import spider
from mini_spider import errors


class UrlHtmlParserTest(unittest.TestCase):
    """Test UrlHtmlParser"""

    def test_html_parser(self):
        """test html parser"""

        parser = spider.UrlHtmlParser()
        parser.feed('<h1></h1>')

    def test_get_urls(self):
        """test get_urls method"""

        parser = spider.UrlHtmlParser()
        urls = parser.get_urls("<a href=com>baidu</a><img src=src></img>")
        self.assertListEqual(['com','src'], urls)


if __name__ == '__main__':
    unittest.main()
