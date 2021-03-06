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


from appkit.db import sqlalchemyutils as sautils

import json
import pickle

import sqlalchemy
from sqlalchemy.ext import declarative
from sqlalchemy.orm import exc


_UNDEF = object()


def keyvaluemodel_for_session(name, session, tablename=None):
    base = declarative.declarative_base()
    base.metadata.bind = session.get_bind()

    return keyvaluemodel(name, base, tablename)


def keyvaluemodel(name, base, extra_dict={}):
    if not (isinstance(name, str) and name != ''):
        raise TypeError('name must be a non-empty str')

    class_dict = {
        '__tablename__': name.lower()
    }
    class_dict.update(extra_dict)

    newcls = type(
        name,
        (_KeyValueItem, base),
        class_dict)

    return newcls


class _KeyValueItem:
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    key = sqlalchemy.Column(sqlalchemy.String, name='key', nullable=False)
    _value = sqlalchemy.Column(sqlalchemy.String, name='value')
    _typ = sqlalchemy.Column(sqlalchemy.String, name='type', default='str',
                             nullable=False)

    _resolved = _UNDEF

    def __init__(self, key, value, typ=None):
        self.key = key
        self._typ, self._value = self._native_to_internal(value)
        if typ:
            self._typ = typ

    @property
    def value(self):
        return self._interal_to_native(self._typ, self._value)

    @value.setter
    def value(self, v):
        self._typ, self._value = self._native_to_internal(v)

    @staticmethod
    def _native_to_internal(value):
        if isinstance(value, str):
            typ = 'str'

        elif isinstance(value, bool):
            typ = 'bool'
            value = '1' if value else '0'

        elif isinstance(value, int):
            typ = 'int'
            value = str(value)

        elif isinstance(value, float):
            typ = 'float'
            value = str(value)

        else:
            try:
                value = json.dumps(value)
                typ = 'json'

            except TypeError:
                value = pickle.dumps(value)
                typ = 'pickle'

        return (typ, value)

    @staticmethod
    def _interal_to_native(typ, value):
        if typ == 'bool':
            return (value != '0')

        elif typ == 'int':
            return int(value)

        elif typ == 'float':
            return float(value)

        elif typ == 'str':
            return str(value)

        elif typ == 'json':
            return json.loads(value)

        elif typ == 'pickle':
            return pickle.loads(value)

        raise ValueError((typ, value))

    def __repr__(self):
        return "<{classname} {key}={value}>".format(
            classname=self.__class__.__name__,
            key=self.key,
            value=self.value)


class KeyValueManager:
    def __init__(self, model, session=None):
        if not session:
            engine = model.metadata.bind
            if not engine:
                msg = ("Model '{model}' is not bind to any engine an session "
                       "argument is None")
                msg = msg.format(model=repr(model))
                raise TypeError(msg)

            session = sautils.create_session(engine=model.metadata.bind)

        self._sess = session
        self._model = model

    @property
    def _query(self):
        return self._sess.query(self._model)

    def get(self, k, default=_UNDEF):
        try:
            item = self._query.filter(self._model.key == k).one()
        except exc.NoResultFound:
            if default is _UNDEF:
                raise KeyError(k)
            else:
                return default

        return item.value

    def set(self, k, v):
        try:
            item = self._query.filter(self._model.key == k).one()
            item.value = v
        except exc.NoResultFound:
            item = self._model(key=k, value=v)
            self._sess.add(item)

        self._sess.commit()

    def reset(self, k):
        try:
            item = self._query.filter(self._model.key == k).one()
        except KeyError:
            pass

        self._sess.delete(item)
        self._sess.commit()

    def children(self, k):
        return map(
            lambda x: x.key,
            self._query.filter(self._model.key.startswith(k+".")))
