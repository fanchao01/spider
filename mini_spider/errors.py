#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
This module provides all exceptions used in this program.
All the exceptions must derived from the BaseError

Exceptions:
    BaseError, the ultimate base exception
    ArgumentError, the base exception of argument parser exceptions
    ArgumentFileError, raised when the necessary file/directory do not exist
    ArgumentSectionError, raised when the necessary section missed in configure file
    ArgumentOptionError, raised when the necessary option missed in configure file
    QueueEmptyError, raised when the queue is empty
    UrlError, raised when url parser error happened
"""


class BaseError(BaseException):
    """The Ultimate base exception"""


class ArgumentError(BaseError):
    """Argument parser base exception"""


class ArgumentSectionError(ArgumentError):
    """Section missed in config file"""


class ArgumentFileError(ArgumentError):
    """File in arguments does not exits"""


class ArgumentOptionError(ArgumentError):
    """Option missed in config file"""


class QueueEmptyError(BaseError):
    """Queue empty error"""


class UrlError(BaseError):
    """Url download error"""

