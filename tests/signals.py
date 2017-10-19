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
from unittest import mock


from appkit import signaler


class TestSignaler(unittest.TestCase):
    def get_signaler(self, *args, **kwargs):
        return signaler.Signaler(*args, **kwargs)

    def test_send_recv(self):
        s = self.get_signaler()
        callback = mock.Mock()

        s.register('foo')
        s.connect('foo', callback, weak=False)
        s.send('foo')

        self.assertEqual(callback.call_count, 1)

    def test_send_recv_with_args(self):
        s = self.get_signaler()
        callback = mock.Mock()

        s.register('foo')
        s.connect('foo', callback, weak=False)
        s.send('foo', a=1, b=2)

        callback.assert_called_once_with(
            None, a=1, b=2)

    def test_disconnect(self):
        s = self.get_signaler()
        callback = mock.Mock()

        s.register('foo')

        s.connect('foo', callback, weak=False)
        s.send('foo')

        s.disconnect('foo', callback)
        s.send('foo')

        self.assertEqual(callback.call_count, 1)

    def test_duplicated_register(self):
        s = self.get_signaler()
        s.register('foo')
        with self.assertRaises(signaler.DuplicatedSignalError) as cm:
            s.register('foo')

        self.assertEqual(cm.exception.args[0], 'foo')


if __name__ == '__main__':
    unittest.main()
