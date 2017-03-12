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
from appkit import uritools


class TestSha1(unittest.TestCase):
    def test_is_sha1(self):
        self.assertTrue(uritools.is_sha1_urn(
            'urn:sha1:adc83b19e793491b1c6ea0fd8b46cd9f32e592fc'))

    def test_base32_string(self):
        self.assertFalse(uritools.is_sha1_urn(
            'urn:sha1:SQ5HALIG6NCZTLXB7DNI56PXFFQDDVUZ'))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            uritools.is_sha1_urn(1)

    def test_empty(self):
        with self.assertRaises(ValueError):
            uritools.is_sha1_urn('')

    def test_random_string(self):
        self.assertFalse(uritools.is_sha1_urn('test:random-string'))


if __name__ == '__main__':
    unittest.main()
