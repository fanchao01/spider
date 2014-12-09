#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This module provides the spider worker

Classes:
    Spider, the spider worker
    UrlHtmlParser, the paser to parse the url to get child urls
"""
import logging
import urllib2
import HTMLParser
import threading
import re

import errors
from mini_spider import utils


_ESCAPE_CHARS = {'-': '_', '.': '_', '/': '_'}
_STRIP_STRINGS = {'#', '?', 'http://', 'https://', '%', '<', '>'}


class Spider(object):
    """spider worker, each spider has one thread
    
    Args:
        url_cache, the instance of UrlQueue to cache the <url, level>
        html_saver, the instance of HtmlSaver to save the html
        target_url_regx, the target urls in regular express
    """

    def __init__(self, url_cache, html_saver, target_url_regx):
        self.url_cache = url_cache
        self.html_saver = html_saver
        self.url_re = re.compile(target_url_regx)

        self.html_parser = UrlHtmlParser()
        self._stopped = False

    @property
    def stopped(self):
        return self._stopped

    def stop(self):
        self._stopped = True

    def run(self):
        try:
            ul = self.url_cache.get()
            url, level = ul.url, ul.level

            html = self.download(url)
            if html:
                sub_urls = self.parse(html)
                self.cache(url, level, sub_urls)

        except errors.QueueEmptyError:
            self._stopped = True
            logging.info('get no url')

    def download(self, url):
        """inner method to download the url
        """

        html = None
        try:
            # ignore the redirect url case
            request = urllib2.urlopen(url, timeout=0.5)
            html = request.read()

            try:
                charset = request.headers.getparam('charset') or 'gbk'
                html = html.decode(charset)
            except UnicodeDecodeError:
                html = None
                raise

            if self.url_re.match(url):
                self.save(url, html)

        except urllib2.HTTPError as e:
            logging.warn('http error, code: %d, url: %s', e.code, url)
        except urllib2.URLError as e:
            logging.warn('url error, reason: %s, url: %s', e.reason, url)
        except UnicodeDecodeError as e:
            logging.warn('can not decode the url, throw away: %s', url)
        except Exception as e:
            logging.error('unknown error happened: %s', e)

        return html

    def parse(self, html):
        if html:
            return self.html_parser.get_urls(html)

    def save(self, url, html):
        if html:
            url = self.escape_url(url)
            uh = utils.UrlHtmlTuple(url, html)
            self.html_saver.put(uh)

    def cache(self, url, level, sub_urls):
        for su in sub_urls:
            if su.startswith('/'):
                if su.startswith('//'):
                    su =  'http:' + su
                else:
                    su = url + su
            self.url_cache.put(utils.UrlLevelTuple(su, level + 1))

    @classmethod
    def escape_url(cls, url):
        for s in _STRIP_STRINGS:
            url = url.replace(s, '')

        for c, rc in _ESCAPE_CHARS.items():
            url = url.replace(c, rc)

        return url


# HTMLParser is an old-style class
# derived from object is backward compatibility
class UrlHtmlParser(HTMLParser.HTMLParser, object):
    """parse the urls to get child urls
    """
    def __init__(self, *args, **kwargs):
        self.urls = []
        super(UrlHtmlParser, self).__init__(*args, **kwargs)

    def handle_starttag(self, tag, attrs):
        # TODO: simplify it with tag
        for k, v in attrs:
            if k == 'href' or k == 'src':
                self.urls.append(v.strip())

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

    def get_urls(self, html):
        try:
            self.feed(html)
        except HTMLParser.HTMLParseError as e:
            logging.warn('html parse error')
        return self.urls


if __name__ == '__main__':
    UrlHtmlParser('')
    Spider([], [], '')

