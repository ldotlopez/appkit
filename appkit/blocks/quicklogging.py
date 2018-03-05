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


# Some of the default handlers are set at the bottom of this file, after all
# class declarations
DEFAULT_HANDLER = None
DEFAULT_FORMATTER = None
DEFAULT_LEVEL = None
DEFAULT_FORMAT = "[%(levelname)s] [%(name)s] %(message)s"


class Level(enum.Enum):
    # From minor to major value
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def __call__(cls, value):
        for x in list(cls):
            if x == value or x.value == value:
                return x

        raise ValueError(value)

    def incr(self):
        return self.step(+1)

    def decr(self):
        return self.step(-1)

    def step(self, n):
        cls = self.__class__
        levels = list(cls)
        curr = levels.index(self)

        new = curr - n
        new = min(new, len(levels) - 1)
        new = max(0, new)

        return levels[new]

    def __add__(self, n):
        return self.step(n)

    def __sub__(self, n):
        return self.step(-n)


class QuickLogger(logging.Logger):
    def __init__(
            self, name=None, level=None, format=DEFAULT_FORMAT,
            handler_class=None, formatter_class=None):

        if name is None:
            name = utils.prog_name()

        if level is None:
            level = DEFAULT_LEVEL
        else:
            level = Level(level)

        if handler_class is None:
            handler_class = DEFAULT_HANDLER

        if formatter_class is None:
            formatter_class = DEFAULT_FORMATTER

        super().__init__(name, level=level.value)

        handler = handler_class()
        handler.setFormatter(formatter_class(format))
        self.addHandler(handler)

    def getChild(self, *args, **kwargs):
        child = super().getChild(*args, **kwargs)
        for handler in self.handlers:
            child.addHandler(handler)

        return child

    # def setLevel(self, level):
    #     if level in Level:
    #         level = level.value

    #     super().setLevel(level)

    # def getEffectiveLevel(self):
    #     return Level(super().getEffectiveLevel())


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


DEFAULT_HANDLER = DefaultHandler
DEFAULT_FORMATTER = DefaultFormatter
DEFAULT_LEVEL = Level.DEBUG
