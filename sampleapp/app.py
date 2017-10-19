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
from appkit.application import console


class App(console.ConsoleAppMixin, application.App):
    def __init__(self):
        super().__init__('sampleapp')
        self.load_plugin('dirop')
        self.load_plugin('config')
        # self.load_plugin('nested')

    def setup_argument_parser(self, parser):
        super().setup_argument_parser(parser)
        parser.add_argument(
            '--magic',
            action='store_true',
            help='Do magic'
        )

    def main(self, magic=False, **params):
        print("=> {} magic {}".format(
            'with' if magic else 'without',
            ':-D' if magic else ':-('))

        for (k, v) in params.items():
            print("{}={}".format(k, v))

    def handle_application_parameters(self, magic, **kwargs):
        super().handle_application_parameters(**kwargs)
        print("magic:", magic)
        self.magic = magic
