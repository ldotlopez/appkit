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
from appkit import (
    testtools,
    uritools
)


<<<<<<< HEAD
class TestAlterQuery(testtools.TestCaseWithSameURLMixin, unittest.TestCase):
    def test_simple(self):
        url1 = 'http://foo.com/?foo=bar'
        url2 = 'http://foo.com/?foo=x'

        self.assertSameURL(
            uritools.alter_query_params(url1, dict(foo='x')),
            url2)

    def test_add(self):
        url1 = 'http://foo.com/'
        url2 = 'http://foo.com/?foo=x'

        self.assertSameURL(
            uritools.alter_query_params(url1, dict(foo='x')),
            url2)

    def test_del(self):
        url1 = 'http://foo.com/?foo=x&bar=y'
        url2 = 'http://foo.com/?foo=x'

        self.assertSameURL(
            uritools.alter_query_params(url1, dict(bar=None)),
            url2)

    def test_multiple_to_single(self):
        url1 = 'http://foo.com/?foo=x&foo=y'
        url2 = 'http://foo.com/?foo=x'

        self.assertSameURL(
            uritools.alter_query_params(url1, dict(foo='x')),
            url2)

    def test_multiple_to_other_mult(self):
        url1 = 'http://foo.com/?foo=x&foo=y'
        url2 = 'http://foo.com/?foo=a&foo=b&foo=c'

        self.assertSameURL(
            uritools.alter_query_params(url1, dict(foo=['a', 'b', 'c'])),
            url2)

    def test_multiple_to_none(self):
        url1 = 'http://foo.com/?foo=x&foo=y'
        url2 = 'http://foo.com/'

        self.assertSameURL(
            uritools.alter_query_params(url1, dict(foo=None)),
            url2)

    def test_modify_single_skip_multiple(self):
        url1 = 'http://foo.com/?foo=x&foo=y&bar=a'
        url2 = 'http://foo.com/?foo=x&bar=b&foo=y'

        self.assertSameURL(
            uritools.alter_query_params(url1, dict(bar='b')),
            url2)

    def test_safe_chars(self):
        url1 = 'magnet:?xt=urn:bthi:001&dn=001&tr=a&tr=b'
        url2 = 'magnet:?xt=urn:bthi:002&dn=001&tr=a&tr=b'
        newurl = uritools.alter_query_params(url1, dict(xt='urn:bthi:002'), safe=':')

        self.assertSameURL(url2, newurl)
        self.assertTrue('urn:bthi:002' in newurl)


if __name__ == '__main__':
    unittest.main()
