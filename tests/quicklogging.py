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

from appkit.blocks import quicklogging as ql
import logging


# class TestQuickLogger(unittest.TestCase):
#     def test_level_prop(self):
#         log = ql.QuickLogger(level=ql.Level.INFO)
#         self.assertEqual(
#             log.getEffectiveLevel(),
#             ql.Level.INFO)

#         log = ql.QuickLogger(level=ql.Level.DEBUG)
#         log.setLevel(ql.Level.CRITICAL)
#         self.assertEqual(
#             log.getEffectiveLevel(),
#             ql.Level.CRITICAL)

#         log = ql.QuickLogger(level=ql.Level.DEBUG)
#         log.level = ql.Level.INFO


class TestLevel(unittest.TestCase):
    def test_level_conversion(self):
        self.assertEqual(
            ql.Level(logging.INFO),
            ql.Level.INFO)

        self.assertEqual(
            ql.Level(logging.WARNING),
            ql.Level.WARNING)

    def test_level_incr_decr(self):
        self.assertEqual(
            ql.Level.incr(ql.Level.INFO),
            ql.Level.DEBUG)

        self.assertEqual(
            ql.Level.decr(ql.Level.DEBUG),
            ql.Level.INFO)

        self.assertEqual(
            ql.Level.decr(ql.Level.CRITICAL),
            ql.Level.CRITICAL)

        self.assertEqual(
            ql.Level.incr(ql.Level.DEBUG),
            ql.Level.DEBUG)

    # def test_level_lt(self):
    #     # ipdb> logging.DEBUG.__lt__(logging.INFO)
    #     # True
    #     self.assertTrue(ql.Level.DEBUG < ql.Level.INFO)
    #     self.assertTrue(ql.Level.DEBUG < logging.INFO)
    #     self.assertTrue(ql.Level.INFO == logging.INFO)


if __name__ == '__main__':
    unittest.main()
