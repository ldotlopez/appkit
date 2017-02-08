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


from ldotcommons import utils


class AttribDictWithRO(utils.AttribDict):
    RO = ['foo']


class AttribDictWithAccessors(utils.AttribDict):
    SETTERS = ['foo']
    GETTERS = ['bar']

    def set_foo(self, value):
        self['foo'] = value + 1

    def get_bar(self):
        return self['bar'] - 1


class TestAttribDict(unittest.TestCase):
    def test_init_named_params(self):
        ad = utils.AttribDict(a=1, b=2)
        self.assertTrue('a' in ad)
        self.assertTrue('b' in ad)
        self.assertFalse('c' in ad)
        self.assertEqual(ad.a, 1)
        self.assertEqual(ad.b, 2)

    def test_init_from_dict(self):
        ad = utils.AttribDict({'a': 1, 'b': 2})
        self.assertTrue('a' in ad)
        self.assertTrue('b' in ad)
        self.assertFalse('c' in ad)
        self.assertEqual(ad.a, 1)
        self.assertEqual(ad.b, 2)

    def test_init_from_kwargs(self):
        ad = utils.AttribDict(**{'a': 1, 'b': 2})
        self.assertTrue('a' in ad)
        self.assertTrue('b' in ad)
        self.assertFalse('c' in ad)
        self.assertEqual(ad.a, 1)
        self.assertEqual(ad.b, 2)

    def test_iter(self):
        ad = utils.AttribDict(a=1, b=2)
        self.assertEqual(set(ad.keys()), set(('a', 'b')))

    def test_ro_attribute(self):
        ad = AttribDictWithRO(a=1, b=2, foo=3)
        with self.assertRaises(utils.ReadOnlyAttribute):
            ad.foo = 4

    def test_accessors(self):
        ad = AttribDictWithAccessors()
        ad.foo = 1
        ad.bar = 1
        self.assertEqual(ad.foo, 2)
        self.assertEqual(ad.bar, 0)

if __name__ == '__main__':
    unittest.main()
