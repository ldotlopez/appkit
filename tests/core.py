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


import argparse
import re


from appkit import (
    ArgParseDictAction,
    NoneType,
    Null,
    QueueIterable,
    RegexpType,
    SingletonMetaclass
)


class TestCoreTypes(unittest.TestCase):
    def test_singleton(self):
        class A(metaclass=SingletonMetaclass):
            pass

        self.assertTrue(A() is A())

    def test_argparse_dict_action(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--kv', dest='dict', default={},
                            action=ArgParseDictAction)
        args = parser.parse_args('--kv a=1 --kv b=2'.split())
        self.assertTrue(args.dict['a'] == '1')
        self.assertTrue(args.dict['b'] == '2')

    def test_none_type(self):
        self.assertTrue(isinstance(None, NoneType))

    def test_null_singleton(self):
        n1 = Null()
        n2 = Null()

        self.assertTrue(n1 is n2 is Null)

    def test_null_attrs(self):
        n = Null()
        self.assertTrue(n is n.foo is n.foo.bar)

    def test_null_item(self):
        n = Null()
        self.assertTrue(n is n['foo'] is n['foo']['bar'] is n[0] is Null)

    def test_queue_iterable(self):
        q = QueueIterable()
        q.put(1)
        q.put(2)
        q.put(3)

        res = []
        for x in q:
            res.append(x)

        self.assertEqual(
            res,
            [1, 2, 3])

    def test_regexp_type(self):
        self.assertTrue(isinstance(re.compile('.*'), RegexpType))


if __name__ == '__main__':
    unittest.main()