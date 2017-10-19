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


"""Cache services"""

import abc
import hashlib
import os
import pickle
import shutil
import sys
import tempfile
import time


def _now():
    return time.time()


class CacheKeyError(KeyError):
    """
    Base class for cache errors
    """
    pass


class CacheKeyMissError(CacheKeyError):
    """
    Requested key is missing in cache
    """
    pass


class CacheKeyExpiredError(CacheKeyError):
    """
    Requested key is expired in cache
    """
    pass


class CacheIOError(IOError):
    """
    Cache error related to I/O errors
    """
    pass


class CacheOSError(OSError):
    """
    Cache error related to OS errors
    """
    pass


class BaseCache:
    """
    Abstract base class for all appkit caches
    """
    def __init__(self, delta=0, *args, **kwargs):
        try:
            delta = float(delta)
        except ValueError as e:
            msg = "delta must be an int/float"
            raise TypeError(msg) from e

        if delta < 0:
            delta = sys.maxsize

        self.delta = delta

    @abc.abstractmethod
    def get(self, key):
        """
        Returns the requested key from the cache.
        Parameters:
          key - Any hasheble object.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def set(self, key, value):
        """
        Stores value into cache associated with key.
        Parameters:
          key - Any hasheble object.
          value - Value to store
        """
        raise NotImplementedError()


class NullCache(BaseCache):
    def get(self, key):
        raise CacheKeyMissError(key)

    def set(self, key, data):
        pass


class MemoryCache(BaseCache):
    def __init__(self, delta=-1):
        super().__init__(delta=delta)
        self._mem = {}

    def get(self, key):
        if key not in self._mem:
            raise CacheKeyMissError(key)

        ts, value = self._mem[key]
        now = _now()

        if now - ts > self.delta:
            del(self._mem[key])
            raise CacheKeyExpiredError(key)

        return value

    def set(self, key, value):
        self._mem[key] = (_now(), value)

    def delete(self, key):
        try:
            del(self._mem[key])
        except KeyError:
            pass

    def purge(self):
        expired = []
        now = _now()

        for (key, (ts, dummy)) in self._mem.items():
            if now - ts > self.delta:
                expired.append(key)

        for key in expired:
            self.delete(key)


class DiskCache(BaseCache):
    def __init__(self, basedir=None, delta=-1):
        """
        Disk-based cache.
        Parameters:
          basedir - Root path for cache. Auxiliar cache files will be stored
                    under this path. If None is suplied then a temporal dir
                    will be used.
          delta - Seconds needed before a entry is considered expired. Zero or
                  negative values means that entries will never expire.
          hashfun - A callable that will be use to transform keys into strings.
        """
        self.basedir = basedir
        self._is_tmp = False

        if not self.basedir:
            self.basedir = tempfile.mkdtemp()
            self._is_tmp = True

    def _on_disk_path(self, key):
        hashed = hashlib.sha1(key.encode('utf-8')).hexdigest()
        return os.path.join(
            self.basedir, hashed[:0], hashed[:1], hashed[:2], hashed)

    def set(self, key, value):
        p = self._on_disk_path(key)
        dname = os.path.dirname(p)

        os.makedirs(dname, exist_ok=True)
        with open(p, 'wb') as fh:
            fh.write(pickle.dumps(value))

    def get(self, key, delta=None):
        on_disk = self._on_disk_path(key)
        try:
            s = os.stat(on_disk)

        except (OSError, IOError) as e:
            raise CacheKeyMissError(key) from e

        delta = delta or self.delta
        if time.mktime(time.localtime()) - s.st_mtime > delta:
            os.unlink(on_disk)
            raise CacheKeyExpiredError(key)

        try:
            with open(on_disk, 'rb') as fh:
                return pickle.loads(fh.read())

        except EOFError as e:
            os.unlink(on_disk)
            raise CacheKeyError(key) from e

        except IOError as e:
            raise CacheIOError() from e

        except OSError as e:
            raise CacheOSError() from e

    def __del__(self):
        if self._is_tmp:
            shutil.rmtree(self.basedir)
