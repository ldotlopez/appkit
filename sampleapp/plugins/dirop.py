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


from appkit.application import Parameter, console


class DirOP(console.ConsoleCommandExtension):
    __extension_name__ = 'dir-op'

    HELP = 'Change desktop background'
    PARAMETERS = (
        Parameter(
            'directory',
            abbr='d',
            help='Choose random background from directory',
            required=True
        ),
    )

    def validator(self, directory=None):
        if not isinstance(directory, str) or directory == '':
            raise ValueError('Invalid directory: {}'.format(repr(directory)))

        return {
            'directory': directory
        }

    def main(self, directory):
        print("Got directory: {}".format(directory))
        return 0


__sampleapp_extensions__ = [
    DirOP
]
