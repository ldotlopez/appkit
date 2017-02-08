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
from ldotcommons.decorators import accepts, VaArgs, ArgCountError


class TestDecorators(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @accepts(object, bool, int, float, str)
    def basic_func(self, b, i, f, s):
        pass

    @accepts(object, bool, int, float, str, VaArgs)
    def va_args_func(self, b, i, f, s, *args):
        pass

    @accepts(object, bool, int, float, str, VaArgs)
    def va_args_2_func(self, b, i, f, s, *kwargs):
        pass

    def test_basic(self):
        self.basic_func(True, 1, 1.0, 'str')

    def test_arg_count(self):
        try:
            self.basic_func(True, 1, 1.0)
        except ArgCountError:
            pass

    def test_arg_type(self):
        try:
            self.basic_func('str', 1.0, 1, True)
        except TypeError:
            pass

    def test_va_args(self):
        self.va_args_func(True, 1, 1.0, 'str', 'a', 'b', 'c')
 
if __name__ == '__main__':
    unittest.main()
