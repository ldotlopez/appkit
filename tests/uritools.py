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


class TestAlterQuery(unittest.TestCase):
    def test_simple_replace(self):
        self.assertEqual(uritools.alter_query_param(
            'http://foo.com/?a=a', 'a', 'x'),
            'http://foo.com/?a=x')

    def test_add(self):
        self.assertEqual(uritools.alter_query_param(
            'http://foo.com/', 'a', 'x'),
            'http://foo.com/?a=x')

    def test_remove(self):
        self.assertEqual(uritools.alter_query_param(
            'http://foo.com/?a=x', 'a', None),
            'http://foo.com/')

    def test_keep_unset(self):
        import ipdb; ipdb.set_trace(); pass
        self.assertEqual(uritools.alter_query_param(
            'http://foo.com/?a=x', 'a', None, keep_unset=True),
            'http://foo.com/?a=')

    def test_reserved(self):
        self.assertEqual(uritools.alter_query_param(
            'http://foo.com/?a=#', 'a', 'x:x', safe=':'),
            'http://foo.com/?a=x:x')

if __name__ == '__main__':
    unittest.main()
