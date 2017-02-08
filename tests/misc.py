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
from ldotcommons.misc import url_strip_query_param, url_get_query_param


class TestMisc(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_url_param_get(self):
        u = 'http://test.com/?foo=bar&abc=def&z=1'

        # Get foo
        self.assertEqual(url_get_query_param(u, 'foo'), 'bar')

        # Get non existent parameter
        self.assertRaises(KeyError, url_get_query_param, u, 'xxxx')

    def test_url_param_strip(self):
        u = 'http://test.com/?foo=bar&abc=def&z=1'

        # Non existent parameter
        self.assertEqual(url_strip_query_param(u, 'xxx'), u)

        # Try some variations
        self.assertEqual(url_strip_query_param(u, 'foo'), 'http://test.com/?abc=def&z=1')
        self.assertEqual(url_strip_query_param(u, 'abc'), 'http://test.com/?foo=bar&z=1')
        self.assertEqual(url_strip_query_param(u, 'z'),   'http://test.com/?foo=bar&abc=def')

        # Check corner cases
        u = 'http://test.com/?'
        self.assertEqual(url_strip_query_param(u, 'xxx'), u)

if __name__ == '__main__':
    unittest.main()
