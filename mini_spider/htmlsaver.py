#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This module provides classes to save the downloaded html content

Classes:
    HtmlSaver, execute as a daemoned thread to save the htmls

"""
import os
import collections
import threading
import logging

import interface
import errors


class HtmlSaver(threading.Thread, interface.Worker):
    """execute as a daemoned thread to save the htmls
    Args:
        output_dir, the absolute directory path where to save the htmls
    """

    def __init__(self, output_dir):
        self.output_dir = output_dir
        self._stopped = threading.Event()

        # protect the set and queue
        self.lock = threading.Lock()
        self.html_set = set()
        self.html_queue = collections.deque()

        super(HtmlSaver, self).__init__()
        self.daemon = True

        self._make_dir()

    def _make_dir(self):
        if not os.path.exists(self.output_dir):
            try:
                os.mkdir(self.output_dir)
            except IOError as e:
                raise errors.ArgumentFileError(e)

    def put(self, uh):
        with self.lock:
            if uh not in self.html_set:
                self.html_queue.append(uh)
                self.html_set.add(uh)
                logging.debug('get one uh, %s', uh)

    def _get(self):
        with self.lock:
            try:
                return self.html_queue.popleft()
            except IndexError:
                pass

    def _save(self, uh):
        filename = os.path.join(self.output_dir, uh.url)
        with open(filename, 'w') as outfile:
            try:
                outfile.write(uh.html)
            except IOError as e:
                logging.warn('save html error, %s', uh)
            except UnicodeDecodeError as e:
                logging.warn('can not save the html, %s', uh)
            else:
                logging.info('save one html, %s', uh)

    def run(self):
        while not self._stopped.is_set():
            uh = self._get()
            if not uh:
                self._stopped.wait(0.1)
            else:
                self._save(uh)
        logging.info('htmlsaver runs over')

    def terminate(self):
        self._stopped.set()
        # no need lock, self.run and put is not in use
        for uh in self.html_queue:
            self._save(uh)

        # when crtl-c, it may fail with very low chance
        assert not self.html_queue
        logging.info('all downloaded htmls saved')


if __name__ == '__main__':
    HtmlSaver('.')

