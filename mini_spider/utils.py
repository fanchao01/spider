#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This module provides utilities used in this program

Classes:
    UrlLevelTuple, container for url and its level
    UrlHtmlTuple, container for url and its content
    UrlQueue, a queue to contain the UrlLeveltuple,
        the core compoment of the spider
"""
import logging
import threading
import collections

from mini_spider import errors


class UrlLevelTuple(object):
    """container of the url and its level
    
    Args:
        url, the original url
        level, the url's level
    """

    __slots__ = ('url', 'level')

    def __init__(self, url, level):
        self.url = url
        self.level = level

    def __hash__(self):
        return hash(self.url)

    def __repr__(self):
        return 'url: %s, level: %s' % (self.url, self.level)


class UrlHtmlTuple(object):
    """container of the url and its content

    Args:
        url, the escaped url, used as filename
        html, the content of the url to save
    """

    __slots__ = ('url', 'html')

    def __init__(self, url, html):
        self.url = url
        self.html = html

    def __hash__(self):
        return hash(self.url)

    def __repr__(self):
        return "url: %s, length: %d" % (self.url, len(self.html))


class UrlQueue(object):
    """the queue to contain the <url, level>

    Args:
        max_workers, the max number of workers on this queue
        max_level, the max number of level to spider
        current_level, the first at first
    """

    def __init__(self, max_workers, max_level, current_level=0):
        self._lock = threading.Lock()

        self._urls = collections.defaultdict(set)
        # use for O(1) found
        self._urls_set = set()

        self._current_level = current_level
        self._max_level = max_level

        self._max_workers = max_workers
        self._waiting_workers = 0
        self._waiting_queue = threading.Condition(self._lock)

    def put(self, ul):
        with self._lock:
            if ul.level <= self._max_level and ul.url not in self._urls_set:
                self._urls[ul.level].add(ul)
                self._urls_set.add(ul.url)
                logging.debug('urlqueue put one url, %s', ul)

                if ul.level <= self._current_level:
                    self._waiting_queue.notify()
        logging.debug('url queue has url levels: %d', len(self._urls))

    def get(self):
        with self._lock:
            try:
                # set's pop return a random element
                ul = self._urls[self._current_level].pop()
            except KeyError:
                # urls all done at current_level, go next
                if self._waiting_workers + 1 >= self._max_workers:
                    assert not self._urls[self._current_level]
                    self._current_level += 1
                    self._waiting_queue.notify_all()
                else:
                    self._waiting_workers += 1
                    self._waiting_queue.wait()
                    self._waiting_workers -= 1

                try:
                    # waken to try again
                    ul = self._urls[self._current_level].pop()
                except KeyError:
                    # no urls at all
                    raise errors.QueueEmptyError()

            finally:
                if not self._urls[self._current_level]:
                    try:
                        del self._urls[self._current_level]
                    except KeyError:
                        pass

        logging.debug('get one url: %s', ul)
        return ul

    def terminate(self):
        with self._lock:
            self._waiting_queue.notify_all()

    def empty(self):
        with self._lock:
            return len(self._urls) == 0


if __name__ == '__main__':
    UrlQueue(0, 1)

