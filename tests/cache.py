# -*- coding: utf-8 -*-

# Copyright (C) 2017 Luis López <luis@cuarentaydos.com>
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


import time


from appkit import cache


class CacheTest:
    def get_cache(self, *args, **kwargs):
        return self.CACHE_CLASS(*args, **kwargs)

    def test_get(self):
        c = self.get_cache()
        c.set('x', 1)
        self.assertEqual(
            c.get('x'),
            1)

    def test_cache_miss(self):
        c = self.get_cache()
        with self.assertRaises(cache.CacheKeyMissError) as cm:
            c.get('x')

        self.assertEqual(cm.exception.args[0], 'x')

    def test_cache_expire(self):
        c = self.get_cache(delta=0)
        c.set('x', 1)
        time.sleep(0.1)

        with self.assertRaises(cache.CacheKeyExpiredError) as cm:
            c.get('x')

        self.assertEqual(cm.exception.args[0], 'x')


class MemoryCacheTest(CacheTest, unittest.TestCase):
    CACHE_CLASS = cache.MemoryCache


if __name__ == '__main__':
    unittest.main()
