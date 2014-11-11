#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This module provides classes to manage the threads

Classes:
    SpiderThread, spider works in this classes
    Scheduler, manage all the threads

Date:    2014/10/29 17:23:06
"""
import os
import logging
import threading

import htmlsaver
import utils
import errors
import interface
import spider


class SpiderThread(threading.Thread, interface.Worker):
    """the spider thread
    
    Args:
        spider, the spider worker
        crawl_interval, the work interval of the spider
        args, arguments passed to spider
        kwargs, positional arguments passed to spider
    """
    
    def __init__(self, spider, crawl_interval, *args, **kwargs):
        self.spider = spider
        self.stopped = threading.Event()
        self.crawl_interval = crawl_interval

        super(SpiderThread, self).__init__(*args, **kwargs)
        self.daemon = True

    def run(self):
        while True:
            if self.spider.stopped:
                logging.info('spider thread will be exiting by spider')
                break

            if not self.stopped.wait(self.crawl_interval):
                self.spider.run()
            else:
                self.spider.stop()
                logging.info('spider thread will be exiting by thread')

    def terminate(self):
        self.stopped.set()
        logging.info('spider thread will be exiting by terminate')


class Scheduler(object):
    """manage all the threads
    
    Args:
        arg_parser, the argument parser
    """

    def __init__(self, arg_parser):
        self.thread_num = arg_parser.get_spider_option('thread_count', int)
        self.max_level = arg_parser.get_spider_option('max_depth', int)
        self.output_dir = arg_parser.get_spider_option('output_directory', dir)
        self.target_url_regx = arg_parser.get_spider_option('target_url', str)
        self.crawl_interval = arg_parser.get_spider_option('crawl_interval', float)
        self.urls_cache = utils.UrlQueue(self.thread_num, self.max_level)
        self.saver = htmlsaver.HtmlSaver(self.output_dir)

        self.workers = [self.saver, ]

        self._put_level_zero_urls(arg_parser.get_spider_option('url_list_files', str))

    def _put_level_zero_urls(self, urls_file):
        if not os.path.exists(urls_file):
            raise errors.ArgumentFileError(
                '`file not exits: {0}'.format(urls_file))

        try:
            with open(urls_file, 'r') as infile:
                for url in infile:
                    self.urls_cache.put(utils.UrlLevelTuple(url=url.strip(), level=0))
        except IOError as e:
            logging.warn('file can not read: %s', f)

        if self.urls_cache.empty():
            raise errors.QueueEmptyError('no urls at fisrt')

    def init(self):
        """initial method to prepare the environmetn"""
        
        for i in range(self.thread_num):
            worker = spider.Spider(self.urls_cache, self.saver, self.target_url_regx)
            self.workers.append(SpiderThread(worker, self.crawl_interval))

    def execute(self):
        """start all threads and run"""

        for worker in self.workers:
            worker.start()

        while self.workers:
            # all sipder thread exits, kill htmlsaver actively
            if len(self.workers) == 1:
                self.saver.terminate()

            for worker in self.workers[:]:
                worker.join(self.crawl_interval)
                if not worker.is_alive():
                    self.workers.remove(worker)
                    logging.info('worker thread is removed: %d', worker.ident)

        logging.info('all worker thread exited, exit now')

    def terminate(self):
        # html_saver should stop at last
        for worker in reversed(self.workers):
            worker.terminate()


if __name__ == '__main__':
    Scheduler()

