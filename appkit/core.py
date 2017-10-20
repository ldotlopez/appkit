# -*- coding: utf-8 -*-

# Copyright (C) 2015 Luis López <luis@cuarentaydos.com>
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


import argparse
import re
import queue


class SingletonMetaclass(type):
    def __call__(cls, *args, **kwargs):  # nopep8
        instance = getattr(cls, '_instance', None)
        if not instance:
            setattr(cls,
                    '_instance',
                    super(SingletonMetaclass, cls).__call__(*args, **kwargs))
        return cls._instance


class ArgParseDictAction(argparse.Action):
    """
    Convert a series of --foo key=value --foo key2=value2 into a dict like:
    { key: value, key2: value}
    """

    def __call__(self, parser, namespace, values, option_string=None):
        dest = getattr(namespace, self.dest)
        if dest is None:
            dest = {}

        parts = values.split('=')
        key = parts[0]
        value = ''.join(parts[1:])

        dest[key] = value

        setattr(namespace, self.dest, dest)


class QueueIterable(queue.Queue):
    def __iter__(self):
        while True:
            try:
                x = self.get_nowait()
                yield x
            except queue.Empty:
                break


class NullType:
    def __unicode__(self):
        return 'Null'

    def __getattr__(self, attr):
        return self

    def __getitem__(self, key):
        return self

    def __call__(self):
        return self

    __str__ = __unicode__


class NullSingleton(NullType, metaclass=SingletonMetaclass):
    def __repr__(self):
        return 'Null'


class UndefinedType:
    def __unicode__(self):
        return 'Undefined'

    __str__ = __unicode__


class UndefinedSingleton(UndefinedType, metaclass=SingletonMetaclass):
    def __repr__(self):
        return 'Undefined'


NoneType = type(None)
RegexpType = type(re.compile(r''))


Null = NullSingleton()
Undefined = UndefinedSingleton()
