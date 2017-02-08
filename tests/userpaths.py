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

from ldotcommons import utils

import appdirs


class UserPathsOSX(unittest.TestCase):
    def setUp(self):
        appdirs.system = 'darwin'

    def test_prog_name(self):
        self.assertEqual(utils.prog_name('simple'), 'Simple')
        self.assertEqual(utils.prog_name('foo-bar'), 'Foo Bar')
        self.assertEqual(utils.prog_name('foo-bar.py'), 'Foo Bar')
        self.assertEqual(utils.prog_name('a.b.py'), 'A.b')

    def test_basic_configfile(self):
        self.assertEqual(
            utils.prog_config_file(),
            os.path.expanduser('~/Library/Application Support/Userpaths.ini'))

    def test_config(self):
        self.assertEqual(
            utils.user_path('config'),
            os.path.expanduser('~/Library/Application Support/Userpaths'))

        self.assertEqual(
            utils.user_path('config', 'foo.cfg'),
            os.path.expanduser('~/Library/Application Support/Userpaths/Foo.cfg'))

    def test_user_data(self):
        self.assertEqual(
            utils.user_path('data'),
            os.path.expanduser('~/Library/Application Support/Userpaths'))

        self.assertEqual(
            utils.user_path('data', 'foo'),
            os.path.expanduser('~/Library/Application Support/Userpaths/Foo'))

    def test_user_cache(self):
        self.assertEqual(
            utils.user_path('cache'),
            os.path.expanduser('~/Library/Caches/Userpaths'))

        self.assertEqual(
            utils.user_path('cache', 'foo'),
            os.path.expanduser('~/Library/Caches/Userpaths/Foo'))


class UserPathsLinux(unittest.TestCase):
    def setUp(self):
        appdirs.system = 'linux'

    def test_prog_name(self):
        self.assertEqual(utils.prog_name('simple'), 'simple')
        self.assertEqual(utils.prog_name('foo-bar'), 'foo-bar')
        self.assertEqual(utils.prog_name('foo-bar.py'), 'foo-bar')
        self.assertEqual(utils.prog_name('a.b.py'), 'a.b')

    def test_basic_configfile(self):
        self.assertEqual(
            utils.prog_config_file(),
            os.path.expanduser('~/.config/userpaths.ini'))

    def test_configfile(self):
        self.assertEqual(
            utils.user_path('config'),
            os.path.expanduser('~/.config/userpaths'))

        self.assertEqual(
            utils.user_path('config', 'foo.cfg'),
            os.path.expanduser('~/.config/userpaths/foo.cfg'))

    def test_user_data_dir(self):
        self.assertEqual(
            utils.user_path('data'),
            os.path.expanduser('~/.local/share/userpaths'))

        self.assertEqual(
            utils.user_path('data', 'foo'),
            os.path.expanduser('~/.local/share/userpaths/foo'))

    def test_user_cache(self):
        self.assertEqual(
            utils.user_path('cache'),
            os.path.expanduser('~/.cache/userpaths'))

        self.assertEqual(
            utils.user_path('cache', 'foo'),
            os.path.expanduser('~/.cache/userpaths/foo'))


if __name__ == '__main__':
    unittest.main()
