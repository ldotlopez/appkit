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
import tempfile
import time
from builtins import (
    IOError as _IOError,
    KeyError as _KeyError,
    OSError as _OSError
)


def hashfunc(key):
    """
    Default hash function for appkit.cache.Disk
    Uses hex-encoded sha1 algorithm to hash keys.
    Parameters:
      key - key to `stringify`.
    """
    return hashlib.sha1(key.encode('utf-8')).hexdigest()


class Base:
    """
    Abstract base class for all appkit caches
    """
    def __init__(self, *args, **kwargs):
        """
        Initialization for Cache implemetations. This is a stub.
        """
        pass

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


class Null(Base):
    def get(self, key):
        raise KeyMissError(key)

    def set(self, key, data):
        pass


class Disk(Base):
    def __init__(self, basedir=None, delta=-1, hashfunc=hashfunc):
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
        self.delta = delta
        self._is_tmp = False

        if not self.basedir:
            self.basedir = tempfile.mkdtemp()
            self._is_tmp = True

    def _on_disk_path(self, key):
        hashed = hashfunc(key)
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

        except (_OSError, _IOError) as e:
            raise KeyMissError(key) from e

        delta = delta or self.delta
        if delta >= 0 and \
           (time.mktime(time.localtime()) - s.st_mtime > delta):
            os.unlink(on_disk)
            raise KeyExpiredError(key)

        try:
            with open(on_disk, 'rb') as fh:
                return pickle.loads(fh.read())

        except EOFError as e:
            os.unlink(on_disk)
            raise KeyError(key) from e

        except _IOError as e:
            raise IOError() from e

        except _OSError as e:
            raise OSError() from e

    def __del__(self):
        if self._is_tmp:
            shutil.rmtree(self.basedir)


class KeyError(_KeyError):
    """
    Base class for cache errors
    """
    pass


class KeyMissError(KeyError):
    """
    Requested key is missing in cache
    """
    pass


class KeyExpiredError(KeyError):
    """
    Requested key is expired in cache
    """
    pass


class IOError(_IOError):
    """
    Cache error related to I/O errors
    """
    pass


class OSError(_OSError):
    """
    Cache error related to OS errors
    """
    pass
