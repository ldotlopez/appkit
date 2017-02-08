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

from ldotcommons import store


class SelectorInterfaceTest(unittest.TestCase):
    def test_get_set(self):
        s = store.Store()

        s.set('x', 1)
        self.assertEqual(s.get('x'), 1)
        self.assertEqual(s.get(None), {'x': 1})

    def test_delete(self):
        s = store.Store()

        s.set('x', 1)
        s.delete('x')
        with self.assertRaises(store.KeyNotFoundError) as cm:
            s.get('x')
        self.assertEqual(cm.exception.args[0], 'x')

        self.assertEqual(s.get(None), {})

    def test_get_with_default(self):
        s = store.Store()

        self.assertEqual(s.get('foo', default=3), 3)
        self.assertEqual(s.get('foo', default='x'), 'x')
        with self.assertRaises(store.KeyNotFoundError) as cm:
            s.get('foo')
        self.assertEqual(cm.exception.args[0], 'foo')

        self.assertEqual(s.get(None), {})

    def test_all_keys(self):
        s = store.Store()
        s.set('x', 1)
        s.set('y.a', 2)
        s.set('y.b', 2)

        self.assertEqual(
            set(s.all_keys()),
            set(['x', 'y.a', 'y.b']))

    def test_has_key(self):
        s = store.Store()
        s.set('x', 1)
        s.set('y.a', 2)
        s.set('y.b', 2)

        self.assertTrue(s.has_key('x'))
        self.assertTrue(s.has_key('y'))
        self.assertTrue(s.has_key('y.a'))

    def test_has_ns(self):
        s = store.Store()
        s.set('x', 1)
        s.set('y.a', 2)
        s.set('y.b', 2)

        self.assertFalse(s.has_namespace('x'))
        self.assertFalse(s.has_namespace('y.a'))
        self.assertTrue(s.has_namespace('y'))
        self.assertFalse(s.has_namespace('z'))

    def test_override(self):
        s = store.Store()
        s.set('x', 1)
        s.set('x', 'a')
        self.assertEqual(s.get('x'), 'a')
        self.assertEqual(s.get(None), {'x': 'a'})

    def test_empty(self):
        s = store.Store()
        s.set('x', 1)
        s.empty()

        self.assertFalse(s.has_key('x'))

    def test_replace(self):
        s = store.Store()
        s.set('x', 1)
        s.replace({'y': 2})

        self.assertFalse(s.has_key('x'))
        self.assertTrue(s.has_key('y'))

    def test_override_with_dict(self):
        s = store.Store()
        s.set('x', 1)
        s.set('x', 'a')
        self.assertEqual(s.get('x'), 'a')
        self.assertEqual(s.get(None), {'x': 'a'})

    def test_key_not_found(self):
        s = store.Store()

        with self.assertRaises(store.KeyNotFoundError) as cm:
            s.get('y')
        self.assertEqual(cm.exception.args[0], 'y')

        self.assertEqual(s.get(None), {})

    def test_children(self):
        s = store.Store()
        s.set('a.b.x', 1)
        s.set('a.b.y', 2)
        s.set('a.b.z', 3)
        s.set('a.c.w', 4)

        self.assertEqual(
            set(s.children('a.b')),
            set(['x', 'y', 'z']))

        self.assertEqual(
            set(s.children('a')),
            set(['b', 'c']))

        self.assertEqual(
            s.children(None),
            ['a'])

    def test_complex(self):
        s = store.Store()

        s.set('a.b.c', 3)
        self.assertEqual(s.get('a.b.c'), 3)
        self.assertEqual(s.get('a.b'), {'c': 3})
        self.assertEqual(s.get('a'), {'b': {'c': 3}})
        self.assertEqual(s.get(None), {'a': {'b': {'c': 3}}})

        s.set('a.k.a', 1)
        s.delete('a.b')
        self.assertEqual(s.get(None), {'a': {'k': {'a': 1}}})

        with self.assertRaises(store.KeyNotFoundError) as cm:
            s.get('a.b')
        self.assertEqual(cm.exception.args[0], 'a.b')

    def test_validator_simple(self):
        def validator(k, v):
            if k == 'int' and not isinstance(v, int):
                raise store.ValidationError(k, v, 'not int')

            return v

        s = store.Store()
        s.add_validator(validator)

        s.set('int', 1)
        with self.assertRaises(store.ValidationError):
            s.set('int', 'a')

    def test_validator_alters_value(self):
        def validator(k, v):
            if k == 'int' and not isinstance(v, int):
                try:
                    v = int(v)
                except ValueError:
                    raise store.ValidationError(k, v, 'not int')

            return v

        s = store.Store()
        s.add_validator(validator)

        s.set('int', 1.1)
        self.assertEqual(s.get('int'), 1)
        with self.assertRaises(store.ValidationError):
            s.set('int', 'a')

    def test_illegal_keys(self):
        s = store.Store()

        with self.assertRaises(store.IllegalKeyError):
            s.set(1, 1)

        with self.assertRaises(store.IllegalKeyError):
            s.set('.x', 1)

        with self.assertRaises(store.IllegalKeyError):
            s.set('.x', 1)

        with self.assertRaises(store.IllegalKeyError):
            s.set('x.', 1)

        with self.assertRaises(store.IllegalKeyError):
            s.set('x..a', 1)

    def test_dottet_value(self):
        s = store.Store()
        s.set('a.b', 'c.d')
        self.assertEqual(s.get('a.b'), 'c.d')

if __name__ == '__main__':
    unittest.main()
