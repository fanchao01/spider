#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This module provides an arguments parser class

Classes:
    ArgumentParser: a argument parser
"""

__all__ = ['ArgParser']

import os
import argparse
import ConfigParser

from mini_spider import errors


# actually, it is used as must-specified options in spider config
_CONFIG_DEFAULT_DICT = {
    'url_list_files': './urls',
    'output_directory': './output',
    'max_depth': 1,
    'crawl_interval': 1,
    'target_url': '.*\.(gif|png|jpg|bmp)',
    'thread_count': 8,
}
_CONFIG_SECION = 'spider'


class ArgParser(object):
    """ a class to manage the arguments

    Args:
        workdir, the absolute path of the work directory

    Methods:
        get_spider_option, get the option of the spider section in configure file
        get_log_option, get the option of the log section in configure file
    """
        
    def __init__(self, workdir):
        self._work_dir = workdir

        self.arg_parser = argparse.ArgumentParser(
            description='mini_spider in python for learn',
            prog='mini_spider')

        self.arg_parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s-0.0.1',
                            help='show the version of this program')

        self.arg_parser.add_argument('-c', '--config',
                            nargs='?',
                            default='./config/spider.conf',
                            help='specify the configure file, default: ./spider.conf')

        self.config_parser = ConfigParser.ConfigParser()

    def parse(self, argv):
        """parse the argument and check the enviroment

        Args:
            argv, the argunment of the program from command line

        Raises:
            errors.ArgumentFIleError, necessary files and directories do not exist
            errors.ArgumentOptionError, necessary options do no exist
            errors.ArgumentSectionError, necessary sections do no exist
        """

        parser = self.arg_parser.parse_args(argv)
        if not os.path.exists(parser.config):
            raise errors.ArgumentFileError('config file not existed: {0}'.format(parser.config))

        self.config_parser.read(parser.config)
        if not self.config_parser.has_section(_CONFIG_SECION):
            raise errors.ArgumentSectionError('No Section of {0}'.format(_CONFIG_SECION))

        for option in _CONFIG_DEFAULT_DICT:
            if not self.config_parser.has_option(_CONFIG_SECION, option):
                raise errors.ArgumentOptionError('No Option of {0}'.format(option))

    def _get_from_section(self, section, option, type):
        try:
            option_value  = self.config_parser.get(section, option)
            if type == dir:
                option_value = os.path.join(self._work_dir, option_value)
            else:
                option_value = type(option_value)
        except (TypeError, ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
            raise errors.ArgumentError(e)

        return option_value

    def get_spider_option(self, option, type=str):
        return self._get_from_section(_CONFIG_SECION, option, type)

    def get_log_option(self, option, type=str, default=None):
        option_value = self._get_from_section('log', option, type)

        if not option_value:
            option_value = default

        if not option_value:
            raise errors.ArgumentOptionError(
                'config error, no option, section: {0}, option: {1}, default: {2}'.
                format('log', option, defualt))
        
        return option_value


if __name__ == '__main__':
    ArgParser('.')

