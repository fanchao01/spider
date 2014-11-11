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
import os
import unittest

from mini_spider import errors
from mini_spider import argument


_CONFIG = """
[log]
# test comment
level = 10
filename = filename

[spider]
url_list_files: ./urls
output_directory: ./output
max_depth: 1
crawl_interval: 1
target_url: .*\.(gif|png|jpg|bmp)$
thread_count: 8
"""


class ArgParserTest(unittest.TestCase):
    """Test ArgParser"""

    def setUp(self):
        self.config = 'test.conf'
        with open(self.config, 'w') as outfile:
            outfile.write(_CONFIG)

    def tearDown(self):
        if os.path.exists(self.config):
            os.unlink(self.config)

    def test_get_log_option(self):
        """test get_log_option"""

        parser = argument.ArgParser('.')
        parser.parse(['-c', self.config])
        self.assertEqual(parser.get_log_option('level', int), 10)
        self.assertRaises(errors.ArgumentError,
                          parser.get_log_option,
                          'no')

    def test_get_spider_option(self):
        """test get_spider_option"""
        
        parser = argument.ArgParser('.')
        parser.parse(['-c', self.config])
        self.assertEqual(parser.get_spider_option('thread_count', int), 8)


if __name__ == '__main__':
    unittest.main()

