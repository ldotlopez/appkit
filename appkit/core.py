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


import re


class SingletonMetaclass(type):
    def __call__(cls, *args, **kwargs):  # nopep8
        instance = getattr(cls, '_instance', None)
        if not instance:
            setattr(cls,
                    '_instance',
                    super(SingletonMetaclass, cls).__call__(*args, **kwargs))
        return cls._instance


class UndefinedType:
    def __unicode__(self):
        return 'Undefined'

    __str__ = __unicode__


class UndefinedSingleton(UndefinedType, metaclass=SingletonMetaclass):
    def __repr__(self):
        return 'Undefined'


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


NoneType = type(None)
RegexpType = type(re.compile(r''))


Null = NullSingleton()
Undefined = UndefinedSingleton()
