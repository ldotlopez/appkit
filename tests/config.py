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
from ldotcommons import config


class TestRecord(unittest.TestCase):
    def setUp(self):
        pass

    def test_init_with_args(self):
        a = config.Record({'foo': 1, 'bar': 'x'})
        self.assertEqual(a.get('foo'), 1)

        b = config.Record()
        b.set('foo', 1)
        b.set('bar', 'x')

        self.assertEqual(a, b)

    def test_setget(self):
        s = config.Record()
        s.set('foo', 1)
        s.set('bar', 'x')
        s.set('x.y', [])

        self.assertEqual(s.get('foo'), 1)
        self.assertEqual(s.get('bar'), 'x')
        self.assertEqual(s.get('x.y'), [])

    def test_nonexistent_key(self):
        s = config.Record()
        with self.assertRaises(KeyError):
            s.get('foo')

    def test_delete(self):
        s = config.Record()
        s.set('foo', 1)
        s.set('foo.bar', 2)

        s.delete('foo')

        with self.assertRaises(KeyError):
            s.get('foo.bar')

        with self.assertRaises(KeyError):
            s.get('foo')

    def test_eq(self):
        data = {
            'foo': 1,
            'x.y': 'z',
            'dict': {'a': 'b'}
            }

        a = config.Record(**data.copy())
        b = config.Record(**data.copy())

        self.assertEqual(a, b)

    def test_sub(self):
        x = config.Record({
            'foo': 1,
            'bar.x': 'x',
            'bar.y': 'y',
            })

        y = config.Record({
            'x': 'x',
            'y': 'y',
        })

        self.assertEqual(x.sub('bar'), y)

    def test_children(self):
        x = config.Record({
            'foo': 1,
            'bar.x': 'x',
            'bar.y': 'y',
            })
        self.assertEqual(set(x.children('bar')), set(['x', 'y']))


class TestRecordAttr(unittest.TestCase):
    def test_getset(self):
        x = config.RecordAttr({'foo': 1, 'bar': 'x', 'a.b': 2})
        self.assertEqual(x.foo, 1)
        self.assertEqual(x.a.b, 2)


if __name__ == '__main__':
    unittest.main()
