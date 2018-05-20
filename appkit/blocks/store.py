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


import copy
import json
import re


import appkit


class FormatError(Exception):
    pass


class IllegalKeyError(ValueError):
    def __unicode__(self):
        return "Illegal key: '{}'".format(self.args[0])

    __str__ = __unicode__


class KeyNotFoundError(KeyError):
    def __unicode__(self):
        return "Key not found: '{}'".format(self.args[0])

    __str__ = __unicode__


class ValidationError(Exception):
    def __init__(self, key, value, msg):
        self.key = key
        self.value = value
        self.msg = msg

    def __unicode__(self):
        return "Invalid value {} for key '{}': {}".format(
            repr(self.value), self.key, self.msg or 'no reason')

    __str__ = __unicode__


def flatten_dict(d, separator):
    if not isinstance(d, dict):
        raise TypeError()

    ret = {}

    for (k, v) in d.items():
        if isinstance(v, dict):
            subret = flatten_dict(v, separator)
            subret = {k + separator + subk: subv
                      for (subk, subv) in subret.items()}
            ret.update(subret)
        else:
            ret[k] = v

    return ret


class TypeValidator:
    def __init__(self, type_map):
        self.type_map = type_map

    def __call__(self, k, v):
        if k in self.type_map:
            try:
                return self.type_map[k](v)
            except Exception:
                pass

            raise ValidationError(k, v, 'Incompatible type')

        return v


class Store:
    def __init__(self, items={}, validators=[], separator='.'):
        self._d = {}
        self._validators = []
        self._separator = separator

        for validator in validators:
            self.add_validator(validator)

        self.update(items)

    def _process_key(self, key):
        if not isinstance(key, str):
            raise IllegalKeyError(key)

        parts = key.split(self._separator)
        if not all([re.match('^[a-z0-9\-]+$', x) for x in parts]):
            raise IllegalKeyError(key)

        return parts

    def validate_value_for_key(self, key, value):
        for vfunc in self._validators:
            value = vfunc(key, value)

        return value

    def _get_subdict(self, key, create=False):
        d = self._d

        parts = self._process_key(key)
        for idx, p in enumerate(parts[:-1]):
            if p not in d and create:
                d[p] = {}

            # Override existing values with dicts is allowed
            # Subclass Store or use a validator if this behaviour needs to be
            # changed
            if p in d and not isinstance(d[p], dict):
                d[p] = {}

            if p not in d:
                raise KeyNotFoundError(self._separator.join(parts[:idx]))

            d = d[p]

        return parts[-1], d

    def empty(self):
        self._d = {}

    def replace(self, data):
        self.empty()
        self.update(data)

    def update(self, data):
        for (k, v) in flatten_dict(data, self._separator).items():
            self.set(k, v)

    def dump(self, stream):
        buff = json.dumps(self.get(None), sort_keys=True, indent=4)
        stream.write(buff)

    def load(self, stream):
        try:
            data = flatten_dict(json.loads(stream.read()), self._separator)
        except json.decoder.JSONDecodeError as e:
            raise FormatError() from e

        for (k, v) in data.items():
            self.set(k, v)

    def load_arguments(self, args):
        for (k, v) in vars(args).items():
            self.set(k, v)

    def add_validator(self, fn):
        self._validators.append(fn)

    def set(self, key, value):
        subkey, d = self._get_subdict(key, create=True)
        v = self.validate_value_for_key(key, value)
        d[subkey] = v

    def get(self, key, default=appkit.Undefined):
        if key is None:
            return self._d

        try:
            subkey, d = self._get_subdict(key, create=False)
            return copy.deepcopy(d[subkey])

        except (KeyNotFoundError, KeyError) as e:
            if default != appkit.Undefined:
                return copy.deepcopy(default)
            else:
                pass  # Mask real exception

        raise KeyNotFoundError(key)

    def delete(self, key):
        subkey, d = self._get_subdict(key)
        try:
            del(d[subkey])
            return
        except KeyError:
            pass  # Mask real exception

        raise KeyNotFoundError(key)

    def children(self, key=None):
        if key is None:
            return list(self._d.keys())

        subkey, d = self._get_subdict(key)
        try:
            return list(d[subkey].keys())
        except KeyError as e:
            pass  # Mask real exception

        raise KeyNotFoundError(key)

    def all_keys(self):
        return flatten_dict(self._d, self._separator)

    def has_key(self, key):
        try:
            subkey, d = self._get_subdict(key)
        except KeyNotFoundError:
            return False

        return subkey in d

    def has_namespace(self, ns):
        try:
            subns, d = self._get_subdict(ns)
        except KeyNotFoundError:
            return False

        return subns in d and isinstance(d[subns], dict)

    __contains__ = has_key
    __setitem__ = get
    __setitem__ = set
    __delitem__ = delete
