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


from appkit import application


class Service(application.Extension):
    def __init__(self, app):
        super().__init__()
        self.app = app


class ApplicationMixin:
    SERVICE_EXTENSION_POINT = Service

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_extension_point(self.__class__.SERVICE_EXTENSION_POINT)
        self._services = {}

    def register_extension_class(self, cls):
        super().register_extension_class(cls)
        if issubclass(cls, self.__class__.SERVICE_EXTENSION_POINT):
            self._services[cls.__extension_name__] = cls(self)

    def _register_as_service(self, name, obj):
        """
        Method to register any instance as a service.
        This is a little hack to allow some stuff work in appkit
        """
        assert isinstance(obj, object)
        assert name not in self._services
        self._services[name] = obj

    def get_extension(self, extension_point, name, *args, **kwargs):
        assert isinstance(extension_point, type)
        assert isinstance(name, str)

        # Check requested extension is a service
        if extension_point == self.__class__.SERVICE_EXTENSION_POINT and \
           name in self._services:
            return self._services[name]

        return super().get_extension(extension_point, name,
                                     *args, **kwargs)

    def get_service(self, name):
        return self.get_extension(self.__class__.SERVICE_EXTENSION_POINT, name)
