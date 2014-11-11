#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import print_function

__author__ = 'fanchao01'

"""
This module provides the entrance

Program:
    usage: python main.py [-c configfile]
    arguments:
        -c --config, specify the config file, default './config/spider.conf'
        -v --verion, show the version of the program
        -h --help, show this usage
"""

import os
import sys
import signal

from mini_spider import argument
from mini_spider import errors
from mini_spider import log
from mini_spider import scheduler as _scheduler


_CWD = os.path.dirname(os.path.realpath(__name__))


def logger(parser):
    """log configure.
    
    configure the log, specify the level and filename

    Args:
        parser: the instance of ArgumentParser
    """
    filename = parser.get_log_option('filename', str)
    level = parser.get_log_option('level', int)
    log.init_log(filename, level=level)


class ExitManager(object):
    """manager the callback functions when signal happened
    
    Impelemented with Singleton Pattern.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.funcs = []

    def register(self, func, *args, **kwargs):
        self.funcs.append((func, args, kwargs))

    def __call__(self, signum, frame):
        for func, args, kwargs in self.funcs:
            func(*args, **kwargs)


def main(argv):
    # windows has not SIGTERM signal
    signals = [signal.SIGINT, signal.SIGTERM]
    try:
        signals.append(signal.SIGQUIT)
    except AttributeError:
        pass

    for sig in signals:
        signal.signal(sig, signal.SIG_IGN)

    try:
        arg_parser = argument.ArgParser(_CWD)
        arg_parser.parse(argv)

        logger(arg_parser)

        scheduler = _scheduler.Scheduler(arg_parser)
        scheduler.init()

    except errors.ArgumentError as e:
        print('argument error, exit:\n\t%s' % e, file=sys.stderr)
        return 1

    except errors.QueueEmpty as e:
        print('no urls to spider, exit.' % e, file=sys.stderr)
        return 0

    exit_manager = ExitManager()
    exit_manager.register(scheduler.terminate)

    for sig in signals:
        signal.signal(sig, exit_manager)

    return scheduler.execute()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

