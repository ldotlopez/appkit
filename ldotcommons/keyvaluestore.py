from ldotcommons.sqlalchemy import create_session, declarative
from sqlalchemy import Column, String
import json
import pickle
from sqlalchemy.orm import exc

_UNDEF = object()


def keyvaluemodel_for_session(name, session, tablename=None):
    base = declarative.declarative_base()
    base.metadata.bind = session.get_bind()

    return keyvaluemodel(name, base, tablename)


def keyvaluemodel(name, base, tablename=None):
    if not (isinstance(name, str) and name != ''):
        raise TypeError('name must be a non-empty str')

    if not ((isinstance(tablename, str) and tablename != '') or
            (tablename is None)):
        raise TypeError('tablename must be a non-empty str')

    if tablename is None:
        tablename = name.lower()

    newcls = type(
        name,
        (_KeyValueItem, base),
        dict(__tablename__=tablename))

    return newcls


class _KeyValueItem:
    key = Column(String, name='key', primary_key=True,
                 unique=True, nullable=False)
    _value = Column(String, name='value')
    _typ = Column(String(), name='type', default='str', nullable=False)

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


class KeyValueManager:
    def __init__(self, model):
        self._sess = create_session(engine=model.metadata.bind)
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
