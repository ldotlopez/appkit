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


import os
import tempfile
import time


from appkit.blocks import cache


class CacheTest:
    def get_cache(self, *args, delta=5, **kwargs):
        return self.CACHE_CLASS(*args, delta=delta, **kwargs)

    def test_get(self):
        c = self.get_cache()

        c.set('x', 1)
        self.assertEqual(c.get('x'), 1)

    def test_override(self):
        c = self.get_cache()

        c.set('x', 1)
        self.assertEqual(c.get('x'), 1)

        c.set('x', 2)
        self.assertEqual(c.get('x'), 2)

    def test_purge(self):
        c = self.get_cache(delta=0.1)

        c.set('x', 1)
        time.sleep(0.2)
        c.purge()

        with self.assertRaises(cache.CacheKeyMissError) as cm:
            c.get('x')
        self.assertEqual(cm.exception.args[0], 'x')

    def test_purge_complex(self):
        c = self.get_cache(delta=0.25)

        c.set('x', 1)
        time.sleep(0.2)

        c.set('y', 2)
        time.sleep(0.1)

        c.purge()  # x purged, y not

        self.assertEqual(c.get('y'), 2)

        with self.assertRaises(cache.CacheKeyMissError) as cm:
            c.get('x')
        self.assertEqual(cm.exception.args[0], 'x')

    def test_cache_miss(self):
        c = self.get_cache()

        with self.assertRaises(cache.CacheKeyMissError) as cm:
            c.get('x')
        self.assertEqual(cm.exception.args[0], 'x')

    def test_cache_expire_instant(self):
        c = self.get_cache(delta=0)

        c.set('x', 1)

        with self.assertRaises(cache.CacheKeyExpiredError) as cm:
            c.get('x')
        self.assertEqual(cm.exception.args[0], 'x')

    def test_cache_expire_in_time(self):
        c = self.get_cache(delta=0.2)
        c.set('x', 1)
        self.assertEqual(c.get('x'), 1)

        time.sleep(0.3)
        with self.assertRaises(cache.CacheKeyExpiredError) as cm:
            c.get('x')
        self.assertEqual(cm.exception.args[0], 'x')

    def test_cache_expire_nevel(self):
        c = self.get_cache(delta=-1)

        c.set('x', 1)
        self.assertEqual(c.get('x'), 1)

        time.sleep(0.1)
        self.assertEqual(c.get('x'), 1)


# class NullCacheTest(CacheTest, unittest.TestCase):
#     CACHE_CLASS = cache.NullCache


class MemoryCacheTest(CacheTest, unittest.TestCase):
    CACHE_CLASS = cache.MemoryCache

    def test_stat(self):
        now = cache._now()
        with tempfile.NamedTemporaryFile() as t:
            st = os.stat(t.name)
            self.assertTrue(now - st.st_mtime < 0.1)


class DiskCacheTest(CacheTest, unittest.TestCase):
    CACHE_CLASS = cache.DiskCache


if __name__ == '__main__':
    unittest.main()
