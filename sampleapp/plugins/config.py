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


from appkit.application.console import ConsoleCommandExtension


class ConfigOpGet(ConsoleCommandExtension):
    def main(self):
        print("config get ()")


class ConfigOpSet(ConsoleCommandExtension):
    def main(self):
        print("config set ()")


class ConfigOps(ConsoleCommandExtension):
    CHILDREN = (
        ('get', ConfigOpGet),
        ('set', ConfigOpSet)
    )


class ConfigReset(ConsoleCommandExtension):
    pass


class ConfigCommand(ConsoleCommandExtension):
    __extension_name__ = 'config'

    HELP = 'Optional command'
    CHILDREN = (
        ('ops', ConfigOps),
        ('reset', ConfigReset)
    )


__sampleapp_extensions__ = [
    ConfigCommand
]
