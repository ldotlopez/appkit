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


import appkit


class BackgroundUpdater(appkit.CommandExtension):
    __extension_name__ = 'background-updater'

    help = 'Change desktop background'
    arguments = (
        appkit.cliargument(
            '-d', '--directory',
            help='Choose random background from directory',
            required=True
        ),
    )

    def run(self, arguments):
        print("Got directory: {}".format(arguments.directory))
        return 0

__sampleapp_extensions__ = [
    BackgroundUpdater
]
