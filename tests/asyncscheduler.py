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


import asyncio


from appkit.blocks import asyncscheduler

_log = []


class _TestException(Exception):
    pass


class BeforeException(_TestException):
    pass


class AfterException(_TestException):
    pass


@asyncio.coroutine
def test_coro(name, secs=0.1, ret=None, fail_before=False, fail_after=False):
    def _exit(x):
        _log.append((name, x))
        if isinstance(x, Exception):
            raise x
        else:
            return x

    if fail_before:
        return _exit(BeforeException(name))

    # print("sleep", name)
    yield from asyncio.sleep(secs)
    # print("wake", name)

    if fail_after:
        return _exit(AfterException(name))

    return _exit(ret)


class AsyncSchedulerTest(unittest.TestCase):
    def setUp(self):
        global _log
        _log = []

    def get_sched(self, *args, **kwargs):
        return asyncscheduler.AsyncScheduler(*args, **kwargs)

    def test_some_coro_takes_longer_and_ignored(self):
        s = self.get_sched(timeout=0.3, maxtasks=2)
        s.sched(test_coro('a', ret=1))
        s.sched(test_coro('b', ret=2, secs=0.4))
        s.sched(test_coro('c', ret=3))
        s.sched(test_coro('d', ret=4))
        s.run()

        log = dict(_log)
        self.assertTrue('b' not in log)

    def test_fail_after(self):
        s = self.get_sched(timeout=0.2, maxtasks=1)
        s.sched(test_coro('fail', fail_after=True))
        s.sched(test_coro('c', ret='1'))
        s.sched(test_coro('d', ret='2'))
        s.run()

        log = dict(_log)
        self.assertTrue(isinstance(log['fail'], AfterException))
        self.assertTrue(log['c'] == '1')
        self.assertTrue(log['d'] == '2')

    def test_fail_doesnt_raises_because_of_timeout(self):
        s = self.get_sched(timeout=0.3, maxtasks=2)
        s.sched(test_coro('fail', secs=1))
        s.run()

        self.assertEqual(_log, [])

    def test_coro_doesnt_run_because_of_timeout(self):
        s = self.get_sched(timeout=0.3, maxtasks=2)
        s.sched(test_coro('timeout', secs=1))
        s.run()

        self.assertEqual(_log, [])


if __name__ == '__main__':
    unittest.main()
