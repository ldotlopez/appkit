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


class SingleA(object, metaclass=utils.SingletonMetaclass):
    pass


class SingleB(metaclass=utils.SingletonMetaclass):
    pass


class TestSingleton(unittest.TestCase):
    def test_basic(self):
        a1 = SingleA()
        a2 = SingleA()

        self.assertEqual(a1, a2)
        self.assertTrue(isinstance(a1, SingleA))

    def test_multisingleton(self):
        a1 = SingleA()
        a2 = SingleA()
        b = SingleB()

        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, b)


if __name__ == '__main__':
    unittest.main()
