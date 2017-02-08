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


import unittest

from sqlalchemy.ext import declarative
from ldotcommons.sqlalchemy import create_session
from ldotcommons.keyvaluestore import (
    KeyValueManager,
    keyvaluemodel,
)


class TestMisc(unittest.TestCase):
    def setUp(self):  # nopep8
        self.sess = create_session('sqlite:///:memory:')

        # Recreate Base for each test, this is not necessary in a real world
        # app
        Base = declarative.declarative_base()  # nopep8
        Base.metadata.bind = self.sess.get_bind()

        self.model = keyvaluemodel('KV', Base)
        self.store = KeyValueManager(self.model)

        Base.metadata.create_all()

    def test_basics(self):
        tests = [
            ('bool_true', True),
            ('bool_false', False),
            ('int', 1),
            ('float', 1.2),
            ('char', 'bar'),
            ('jsonable', {'foo': 'bar', 'test': 1})
        ]

        for (k, v) in tests:
            self.store.set(k, v)

        for (k, expected_value) in tests:
            store_value = self.store.get(k)
            self.assertEqual(expected_value, store_value)

    def test_reset(self):
        self.store.set('foo', 1)
        self.store.reset('foo')
        with self.assertRaises(KeyError):
            self.store.get('foo')

    def test_defaults(self):
        self.assertEqual(self.store.get('nothing', default='foo'), 'foo')
        with self.assertRaises(KeyError):
            self.store.get('nothing_2')

    def test_override(self):
        self.store.set('foo', 18)
        self.assertEqual(self.store.get('foo'), 18)

        self.store.set('foo', 81)
        self.assertEqual(self.store.get('foo'), 81)

    def test_children(self):
        self.store.set('a.b', 1)
        self.store.set('a.c', 2)

        self.assertEqual(
            ['a.b', 'a.c'],
            sorted(self.store.children('a')))

        self.assertEqual(list(self.store.children('nothing')), [])

if __name__ == '__main__':
    unittest.main()
