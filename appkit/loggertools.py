# -*- coding: utf-8 -*-

# Copyright (C) 2012 Jacobo Tarragón
# Copyright (C) 2015 Luis López
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


from appkit import utils


import enum
import logging


try:
    import colorama
    _has_color = True
except ImportError:
    _has_color = False


_loggers = dict()
_logLevel = None


DEFAULT_HANDLER = None
DEFAULT_FORMATTER = None
DEFAULT_FORMAT = "[%(levelname)s] [%(name)s] %(message)s"


class Level(enum.Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def incr(cls, val, n=1):
        l = list(cls)
        idx = l.index(val)
        new = max(0, idx - n)
        return l[new]

    @classmethod
    def decr(cls, val, n=1):
        l = list(cls)
        idx = l.index(val)
        new = min(len(l) - 1, idx + n)
        return l[new]


class DefaultHandler(logging.StreamHandler):
    pass


class DefaultFormatter(logging.Formatter):
    if _has_color:
        COLOR_MAP = {
            logging.DEBUG: colorama.Fore.CYAN,
            logging.INFO: colorama.Fore.GREEN,
            logging.WARNING: colorama.Fore.YELLOW,
            logging.ERROR: colorama.Fore.RED,
            logging.CRITICAL: colorama.Back.RED,
        }
    else:
        COLOR_MAP = {}

    def format(self, record):
        s = super().format(record)

        color = self.COLOR_MAP.get(record.levelno)
        if color:
            s = color + s + colorama.Style.RESET_ALL

        return s


def setLevel(level):
    """
    Set global logging level for all appkit.logging loggers
    """
    global _loggers
    global _logLevel

    _logLevel = level
    for (name, logger) in _loggers.items():
        logger.setLevel(level.value)


def getLevel():
    """
    Get global logging level for all appkit.logging loggers
    """
    global _logLevel
    return _logLevel


def setHandler(handler):
    if handler is None:
        handler = DefaultHandler

    global DEFAULT_HANDLER
    DEFAULT_HANDLER = handler


def setFormatter(formatter):
    if formatter is None:
        formatter = logging.Formatter

    global DEFAULT_FORMATTER
    DEFAULT_FORMATTER = formatter


def getLogger(key=None, level=None, format=DEFAULT_FORMAT,
              handler_class=None, formatter_class=None):
    global _loggers
    global _logLevel

    if key is None:
        key = utils.prog_name()

    if level is None:
        level = _logLevel.value

    if handler_class is None:
        handler_class = DEFAULT_HANDLER

    if formatter_class is None:
        formatter_class = DEFAULT_FORMATTER

    if key not in _loggers:
        _loggers[key] = logging.getLogger(key)
        _loggers[key].setLevel(level)

        handler = handler_class()
        handler.setFormatter(formatter_class(format))
        _loggers[key].addHandler(handler)

    return _loggers[key]


_logLevel = Level.DEBUG
DEFAULT_HANDLER = DefaultHandler
DEFAULT_FORMATTER = DefaultFormatter
