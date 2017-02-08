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
from ldotcommons.versioned_sqlite import VersionedSqlite


class TestVersionedSqlite(unittest.TestCase):
    def setUp(self):
        self._db = VersionedSqlite(':memory:')

    def tearDown(self):
        self._db.close()
        del(self._db)

    def test_migrations(self):
        self.assertTrue(self._db.get_schema_version('main') == -1)

        migrations = (self.schema0, self.schema1)
        self._db.setup('main', migrations)

        self.assertEqual(
            self._db.get_schema_version('main'),
            len(migrations) - 1)

    def schema0(self, curr):
        curr.execute("""
            CREATE TABLE main (
                col1 VARCHAR
            )""")
        return True

    def schema1(self, curr):
        curr.execute("""
            ALTER TABLE main ADD COLUMN col2 INT
            """)
        return True

if __name__ == '__main__':
    unittest.main()
