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


import configparser
import datetime
import enum
import functools
import os
import re
import sys
import time
import warnings

import appdirs


# Argument handling

def argument(*args, **kwargs):
    """argparse argument wrapper to ease the command argument definitions"""
    def wrapped_arguments():
        return args, kwargs

    return wrapped_arguments


#
# User paths
#

def prog_config_file(prog=None):
    if prog is None:
        prog = prog_name()

    return user_path(UserPathType.CONFIG) + '.ini'


def prog_name(prog=sys.argv[0]):
    prog = os.path.basename(prog)
    prog = os.path.splitext(prog)[0]

    if appdirs.system == 'linux':
        prog = re.sub(r'[\-\s]+', '-', prog).lower()
    else:
        prog = ' '.join([x.capitalize() for x in re.split(r'[\-\s]+', prog)])

    return prog


def user_path(typ, name=None, prog=None, create=False, is_folder=None):
    m = {
        UserPathType.CONFIG: appdirs.user_config_dir,
        UserPathType.DATA: appdirs.user_data_dir,
        UserPathType.CACHE: appdirs.user_cache_dir
    }

    if prog is None:
        prog = prog_name()

    if is_folder is None:
        is_folder = name is None

    if typ not in m:
        raise ValueError("Invalid user_path type: '{type}'".format(type=typ))

    ret = m[typ](prog)
    if name is not None:
        # Fix name for OSX
        if appdirs.system == 'darwin':
            name = os.path.sep.join([x.capitalize()
                                    for x in name.split(os.path.sep)])
        ret = os.path.join(m[typ](prog), name)

    if create:
        if is_folder is True:
            mkdir_target = ret
        else:
            mkdir_target = os.path.split(ret)[0]

        if not os.path.exists(mkdir_target):
            os.makedirs(mkdir_target)

    return ret


class UserPathType(enum.Enum):
    CONFIG = appdirs.user_config_dir
    DATA = appdirs.user_data_dir
    CACHE = appdirs.user_cache_dir


#
# datetime
#

def utcnow_timestamp():
    warnings.warn('Use ldotcommons.utils.now_timestamp(utc=True)')
    return now_timestamp(utc=True)


def now_timestamp(utc=False):
    dt = datetime.datetime.utcnow() if utc else datetime.datetime.now()
    return int(time.mktime(dt.timetuple()))


#
# Configparser stuff
#

def configparser_to_dict(cp):
    return {section:
            {k: v for (k, v) in cp[section].items()}
            for section in cp.sections()}


def ini_load(path):
    cp = configparser.ConfigParser()
    with open(path, 'r') as fh:
        cp.read_file(fh)

    return configparser_to_dict(cp)


def ini_dump(d, path):
    cp = configparser.ConfigParser()

    for (section, pairs) in d.items():
        cp[section] = {k: v for (k, v) in pairs.items()}

    fh = open(path, 'w+')
    cp.write(fh)
    fh.close()


#
# Different parsing functions
#

def parse_interval(string):
    _table = {
        'S': 1,
        'M': 60,
        'H': 60*60,
        'd': 60*60*24,
        'w': 60*60*24*7,
        'm': 60*60*24*30,
        'y': 60*60*24*365,
    }
    if isinstance(string, (int)):
        string = str(string)

    if not isinstance(string, str):
        raise TypeError(string)

    m = re.match(r'^(?P<amount>\d+)\s*(?P<modifier>[SMHdwmy])?$', string)
    if not m:
        raise ValueError(string)

    amount = int(m.group('amount'))
    multiplier = _table.get(m.group('modifier') or 'S')
    return amount*multiplier


def parse_size(string):
    suffixes = ['k', 'm', 'g', 't', 'p', 'e', 'z', 'y']
    _table = {key: 1000 ** (idx + 1)
              for (idx, key) in enumerate(suffixes)}

    string = string.replace(',', '.')
    m = re.search(r'^(?P<value>[0-9\.]+)\s*((?P<mod>[kmgtphezy])b?)?$',
                  string.lower())
    if not m:
        raise ValueError()

    value = m.groupdict().get('value')
    mod = m.groupdict().get('mod')

    if '.' in value:
        value = float(value)
    else:
        value = int(value)

    if mod in _table:
        value = value * _table[mod]

    return value


def parse_date(string):
    _table = [
        (r'^\d{4}.\d{2}.\d{2}.\d{2}.\d{2}', '%Y %m %d %H %M'),
        (r'^\d{4}.\d{2}.\d{2}$', '%Y %m %d'),
        (r'^\d{4}.\d{2}$', '%Y %m')
    ]

    if isinstance(string, int):
        return string

    string = re.sub(r'[:\.\-\s/]', ' ', string.strip())

    for (regexp, fmt) in _table:
        if not re.search(regexp, string):
            continue

        dt = datetime.datetime.strptime(string, fmt)
        return int(time.mktime(dt.timetuple()))

    raise ValueError(string)


#
# String manipulation
#
def slugify(s, max_len=0, allowed_chars=r'a-zA-Z0-9\-\.'):
    s = re.sub(r'[^' + allowed_chars + r']', '-', s)
    return s[:max_len] if max_len > 0 else s


def shortify(s, length=50):
    """
    Returns a shortified version of s
    """
    return "…" + s[-(length - 1):] if len(s) > length else s


def word_split(s):
    ret = []
    idx = 0
    protected = False

    for c in s:
        # Setup element
        if len(ret) <= idx:
            ret.insert(idx, '')

        if c in ('\'', '"'):
            protected = not protected
            continue

        if c == ' ' and not protected:
            idx += 1
        else:
            ret[idx] += c


#
# Iterators manipulation
#

def ichunks(it, size):
    """
    Generator function.
    Yields slices with "size"  elements from it iterable.
    Last slice could have less elements.
    """
    while True:
        ret = []
        for x in range(size):
            try:
                ret.append(next(it))
            except StopIteration:
                if ret:
                    yield ret
                return

        yield ret


#
# Decorators
#

def generator_as_list(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return [x for x in fn(*args, **kwargs)]

    return wrapper


def generator_as_dict(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return {k: v for (k, v) in fn(*args, **kwargs)}

    return wrapper
