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

# FIXME: Rename appkit.loggertools to appkit.blocks.easylogging
from appkit import loggertools as el


class TestLogging(unittest.TestCase):
    def setUp(self):
        el.setLevel(el.DEFAULT_LEVEL)
        el.clearLoggers()

    def test_level_incr_decr(self):
        self.assertEqual(
            el.Level.incr(el.Level.INFO),
            el.Level.DEBUG)

        self.assertEqual(
            el.Level.decr(el.Level.DEBUG),
            el.Level.INFO)

        self.assertEqual(
            el.Level.decr(el.Level.CRITICAL),
            el.Level.CRITICAL)

        self.assertEqual(
            el.Level.incr(el.Level.DEBUG),
            el.Level.DEBUG)

    def test_get_loger(self):
        l1 = el.getLogger()
        l2 = el.getLogger()
        self.assertTrue(l1 is l2)

    def test_set_level(self):
        el.setLevel(el.Level.INFO)
        l1 = el.getLogger()
        self.assertEqual(el.Level.ensure(l1.level), el.Level.INFO)

        el.setLevel(el.Level.WARNING)
        self.assertEqual(el.Level.ensure(l1.level), el.Level.WARNING)

    # def test_set_handler(self):
    #     class FooHandler(loggertools.DefaultHandler):
    #         pass

    #     loggertools.setHandler(FooHandler)

    #     logger = loggertools.getLogger('foo')
    #     self.assertTrue(isinstance(logger.handlers[0], FooHandler))


if __name__ == '__main__':
    unittest.main()
