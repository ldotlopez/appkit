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

import os
import tempfile
import random

from ldotcommons import fetchers, logging, utils


class TestFactory(unittest.TestCase):
    def test_factory(self):
        d = [
            ('mock', fetchers.MockFetcher),
            ('urllib', fetchers.UrllibFetcher)
        ]

        for (name, cls) in d:
            f = fetchers.Fetcher(name)
            self.assertTrue(isinstance(f, cls))


class TestMock(unittest.TestCase):
    def test_fetch(self):
        url = 'http://this-is-a-fake-url.com/sample.html'

        base = tempfile.mkdtemp()
        mockfile = os.path.join(base, utils.slugify(url))

        randstr = str(random.random())
        with open(mockfile, 'w+') as fh:
            fh.write(randstr)
            fh.close()

        fetcher = fetchers.MockFetcher(basedir=base)
        buff = fetcher.fetch(url)

        self.assertEqual(buff, randstr)


class TestUrllib(unittest.TestCase):
    def test_fetch(self):
        url = 'http://google.co.uk/'

        fetcher = fetchers.UrllibFetcher(cache=False)
        buff = fetcher.fetch(url).decode('iso-8859-1')
        self.assertTrue(buff.index('<') >= 0)


if __name__ == '__main__':
    logging.set_level(0)
    unittest.main()
