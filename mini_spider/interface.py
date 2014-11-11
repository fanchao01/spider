#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This module provides base classes drived by othe classes.
Classes:
    Worker: interface class drived by HtmlSaver and Spider which execute as thread
"""


class Worker(object):
    """thread classes should drived from this class"""

    def run(self):
        raise NotImplementError

    def terminate(self):
        raise NotImplementError


if __name__ == '__main__':
    pass

