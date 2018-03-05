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


from appkit import (
    Undefined,
    utils
)


import json
import pickle
import re


try:
    import sqlalchemy
    from sqlalchemy import orm, event
    from sqlalchemy.ext import declarative
    from sqlalchemy.orm import exc
    Base = declarative.declarative_base()
except ImportError:
    import warnings
    warnings.warn("sqlalchemy not available. Try `pip install sqlalchemy`.")
    raise


def _re_fn(regexp, other):
    return re.search(regexp, other, re.IGNORECASE) is not None


def create_engine(uri='sqlite:///:memory:', echo=False):
    engine = sqlalchemy.create_engine(uri, echo=echo)

    # @property
    # def __monkeypatch_Base_query(self):
    #     return self.session.query(self)

    # Base.metadata.create_all(bind=engine)

    # Monkeypatch magic
    # setattr(Base, 'engine', engine)
    # setattr(Base, 'session', create_session(engine=engine))
    # setattr(Base.__class__, 'query', __monkeypatch_Base_query)

    # Enable regexp and foreign_keys functionality for sqlite connections
    if uri.startswith('sqlite:///'):
        @event.listens_for(engine, "begin")
        def do_begin(conn):
            conn.connection.create_function('regexp', 2, _re_fn)

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(conn, record):
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_session(uri=None, engine=None, echo=False):
    if not engine:
        engine = create_engine(uri=uri, echo=echo)

    sess = orm.sessionmaker()
    sess.configure(bind=engine)
    Base.metadata.create_all(engine)
    session = sess()

    # session = orm.scoped_session(orm.sessionmaker(bind=engine))

    return session


def query_from_params(conn, mapping, **params):

    # # This code can be used for add type-safety to this function
    # from sqlalchemy.sql import sqltypes

    # columns = self._mapping.__table__.columns
    # for (colname, column) in columns.items():
    #     columntype = column.type
    #     if isinstance(columntype, sqltypes.String):
    #         self._ops[(colname, None)] = self.by_string
    #         self._ops[(colname, 'like')] = self.by_string_like
    #         self._ops[(colname, 'regexp')] = self.by_string_regexp

    #     if isinstance(columntype, sqltypes.Integer):
    #         self._ops[(colname, 'min')] = self.by_amount_min
    #         self._ops[(colname, 'max')] = self.by_amount_max

    q = conn.query(mapping)

    for (prop, value) in params.items():
        if '_' in prop:
            key = '_'.join(prop.split('_')[:-1])
            mod = prop.split('_')[-1]
        else:
            key = prop
            mod = None

        attr = getattr(mapping, key, None)

        if mod == 'like':
            q = q.filter(attr.like(value))

        elif mod == 'regexp':
            q = q.filter(attr.op('regexp')(value))

        elif mod == 'min':
            value = utils.parse_size(value)
            q = q.filter(attr >= value)

        elif mod == 'max':
            value = utils.parse_size(value)
            q = q.filter(attr <= value)

        else:
            q = q.filter(attr == value)

    return q


def glob_to_like(x, wide=False):
    for (g, l) in (('*', '%'), ('.', '_')):
        x = x.replace(g, l)

    if wide:
        if not x.startswith('%'):
            x = '%' + x

        if not x.endswith('%'):
            x = x + '%'

    return x


def install_model(session, model):
    model.metadata.create_all(session.connection())


def uninstall_model(session, model):
    model.__table__.drop(session.connection())


def get(session, model, **kwargs):
    query = session.query(model).filter_by(**kwargs)
    count = query.count()

    if count == 0:
        return None
    if count == 1:
        return query.one()
    else:
        return query.all()


def get_or_create(session, model, **kwargs):
    o = get(session, model, **kwargs)

    if o:
        return o, False
    else:
        return model(**kwargs), True


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


class KeyValueManager:
    def __init__(self, model, session=None):
        if not session:
            engine = model.metadata.bind
            if not engine:
                msg = ("Model '{model}' is not bind to any engine an session "
                       "argument is None")
                msg = msg.format(model=repr(model))
                raise TypeError(msg)

            session = create_session(engine=model.metadata.bind)

        self._sess = session
        self._model = model

    @property
    def _query(self):
        return self._sess.query(self._model)

    def get(self, k, default=Undefined):
        try:
            item = self._query.filter(self._model.key == k).one()
        except exc.NoResultFound:
            if default is Undefined:
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


class _KeyValueItem:
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    key = sqlalchemy.Column(sqlalchemy.String, name='key', nullable=False)
    _value = sqlalchemy.Column(sqlalchemy.String, name='value')
    _type = sqlalchemy.Column(sqlalchemy.String, name='type', default='str',
                              nullable=False)

    _resolved = Undefined

    def __init__(self, key, value, type=None):
        type, value = self._native_to_internal(value)
        super().__init__(key=key, _value=value, _type=type)

    @property
    def value(self):
        return self._interal_to_native(self._type, self._value)

    @value.setter
    def value(self, v):
        self._type, self._value = self._native_to_internal(v)

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

        else:
            raise TypeError(typ)

        raise ValueError((type, value))

    def __repr__(self):
        return "<{classname} {key}={value}>".format(
            classname=self.__class__.__name__,
            key=self.key,
            value=self.value)
