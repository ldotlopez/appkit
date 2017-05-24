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


import copy
import re
import warnings


from appkit import extensionmanager
from appkit import loggertools


class BaseApplication(extensionmanager.ExtensionManager):
    def __init__(self, name, *args, pluginpath=None, logger=None, **kwargs):
        if pluginpath is not None:
            warnings.warn('pluginpath is ignored')

        if logger is None:
            logger = loggertools.getLogger('extension-manager')

        super().__init__(name, *args, **kwargs)
        self.logger = loggertools.getLogger(name)


class Extension(extensionmanager.Extension):
    pass


class Parameter:
    def __init__(self, name, abbr=None, **kwargs):
        if not re.match(r'^[a-z0-9-_]+$', name, re.IGNORECASE):
            raise ValueError(name)

        if abbr and len(abbr) != 1:
            msg = "abbr must be a single letter"
            raise ValueError(abbr, msg)

        self.name = str(name).replace('-', '_')
        self.abbr = str(abbr) if abbr else None
        self.kwargs = copy.copy(kwargs)

    @property
    def short_flag(self):
        if not self.abbr:
            return None

        return '-' + self.abbr

    @property
    def long_flag(self):
        return '--' + self.name.replace('_', '-')

class ExtensionNotFoundError(extensionmanager.ExtensionNotFoundError):
    pass


class ExtensionError(Exception):
    pass


class ConfigurationError(ExtensionError):
    pass


class ArgumentsError(ExtensionError):
    pass


class RequirementError(ExtensionError):
    pass
