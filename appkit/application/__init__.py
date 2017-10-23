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


from appkit.blocks import (
    extensionmanager,
    quicklogging,
    signaler,
    store
)


import abc
import copy
import re
import warnings


__all__ = [
    'Application',
    'Parameter',
    'ArgumentsError',
    'ConfigurationError',
    'ExtensionError',
    'ExtensionNotFoundError',
    'RequirementError'
]


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


class Extension(extensionmanager.Extension):
    def __init__(self, shell, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shell = shell


class Application(extensionmanager.ExtensionManager):
    DEFAULT_SETTINGS = {}

    def __init__(self,
                 name,
                 *args,
                 pluginpath=None, settings=None, logger=None,
                 signals=None,
                 **kwargs):

        if pluginpath is not None:
            warnings.warn('pluginpath is ignored')

        if logger is None:
            logger = quicklogging.QuickLogger(quicklogging.Level.DEBUG)

        if settings is None:
            settings = store.Store()

        if signals is None:
            signals = signaler.Signaler()

        super().__init__(name, *args, **kwargs)
        self.logger = logger
        self.settings = settings
        self.signals = signals

        for (key, value) in self.DEFAULT_SETTINGS.items():
            self.settings.set(key, value)

    def get_extension(self, extension_point, name, *args, **kwargs):
        return super().get_extension(extension_point, name, self.get_shell(),
                                     *args, **kwargs)

    @abc.abstractmethod
    def get_shell(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def main(self, **params):
        raise NotImplementedError()


class Applet(extensionmanager.Extension):
    HELP = ""
    CHILDREN = ()
    PARAMETERS = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = {}
        self.parent = None

        for (name, child_cls) in self.CHILDREN:
            self.children[name] = self.create_child(name, child_cls, *args,
                                                    **kwargs)

    def create_child(self, name, child_cls, *args, **kwargs):
        child = child_cls(*args, **kwargs)
        child.parent = self
        return child

    @property
    def root(self):
        root = self.parent
        if not root:
            return self

        while root.parent:
            root = root.parent

        return root

    @abc.abstractmethod
    def main(self, **parameters):
        raise NotImplementedError()

    @abc.abstractmethod
    def validator(self, **parameters):
        raise NotImplementedError()


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
