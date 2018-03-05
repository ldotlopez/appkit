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


import argparse
import collections
import functools
import sys

from appkit import application
from appkit.blocks import (
    extensionmanager,
    quicklogging
)


SUBCOMMAND_ATTR = '_subcommand'
SUBCOMMANDS_SEPARATOR = '_'

assert SUBCOMMAND_ATTR.startswith(SUBCOMMANDS_SEPARATOR)


def shift_dict(d, shift_prefix=SUBCOMMAND_ATTR,
               separator=SUBCOMMANDS_SEPARATOR):
    key = d.pop(shift_prefix, None)
    if key is None:
        return

    # Get all related attributes:
    # - The inmediate _KEY_x
    # - Others like _subcommand_KEY_*
    discriminator = shift_prefix + separator + key

    attrs = [attr for attr in d
             if (attr == discriminator or
                 attr.startswith(discriminator + separator))]

    # Split those attrs into pieces and sort by the number of pieces
    attrs_and_parts = [
        (attr, attr.split(separator))
        for attr in attrs]
    attrs_and_parts = sorted(
        attrs_and_parts,
        key=lambda x: len(x[1]))

    # Rewrite namespace moving attributes
    for (oldattr, parts) in attrs_and_parts:
        newattr = (
            shift_prefix +
            ''.join(separator + part for part in parts[3:]))
        d[newattr] = d.pop(oldattr)


class ConsoleCommandExtension(application.Applet,  extensionmanager.Extension):
    def setup_parser(self, parser, command_path):
        # Insert command children
        if self.children:
            dest = (
                SUBCOMMAND_ATTR +
                ''.join(SUBCOMMANDS_SEPARATOR + x for x in command_path))
            children_parsers = parser.add_subparsers(dest=dest)

        for (name, child) in self.children.items():
            child_parser = children_parsers.add_parser(name)
            child.setup_parser(
                parser=child_parser, command_path=command_path + [name])

        # Insert command flags
        for parameter in self.PARAMETERS:
            fn = parser.add_argument
            if parameter.short_flag:
                fn = functools.partial(fn, parameter.short_flag)
            if parameter.long_flag:
                fn = functools.partial(fn, parameter.long_flag)
            fn(**parameter.kwargs)

    def execute(self, parameters):
        # Do some checks
        have_subcommand = SUBCOMMAND_ATTR in parameters
        if have_subcommand:
            subcommand = parameters[SUBCOMMAND_ATTR]
            assert subcommand is not None
            assert subcommand in self.children

        if not self.children:
            assert have_subcommand is False

        # Check for execution code
        if not self.children or not have_subcommand:
            return self.main(**parameters)

        else:
            subcommand = parameters[SUBCOMMAND_ATTR]
            shift_dict(parameters)
            return self.children[subcommand].execute(parameters)


class ConsoleApplicationMixin:
    COMMAND_EXTENSION_POINT = ConsoleCommandExtension

    _Parameters = collections.namedtuple(
        '_Parameters',
        ['verbose', 'quiet', 'config_files', 'plugins'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_extension_point(self.__class__.COMMAND_EXTENSION_POINT)

    def get_commands(self):
        return self.get_extensions_for(self.__class__.COMMAND_EXTENSION_POINT)

    def get_command(self, name):
        return self.get_extension(self.__class__.COMMAND_EXTENSION_POINT, name)

    def create_parser(self):
        return argparse.ArgumentParser(add_help=True)

    def create_command_subparser(self, children_parser, name, command):
        return children_parser.add_parser(name, add_help=True)

    def setup_parser(self, parser):
        parser.add_argument(
            '-v', '--verbose',
            dest='verbose',
            default=0,
            action='count')

        parser.add_argument(
            '-q', '--quiet',
            dest='quiet',
            default=0,
            action='count')

        parser.add_argument(
            '-c', '--config-file',
            dest='config_files',
            action='append',
            default=[])

        parser.add_argument(
            '--plugin',
            dest='plugins',
            action='append',
            default=[])

        cmds = self.get_commands()

        if cmds:
            children_parser = parser.add_subparsers(dest=SUBCOMMAND_ATTR)

        for (name, cmd) in cmds:
            cmd_parser = self.create_command_subparser(
                children_parser, name, cmd)

            cmd.setup_parser(cmd_parser, [name])

    def consume_application_parameters(self, parameters):
        quiet = parameters.pop('quiet')
        verbose = parameters.pop('verbose')

        log_level = quicklogging.Level.WARNING + verbose - quiet
        self.logger.setLevel(log_level.value)

        plugins = parameters.pop('plugins')
        for plugin in plugins:
            self.load_plugin(plugin)

        config_files = parameters.pop('config_files')

        # FIXME: Change store API to allow loading files
        # for cf in config_files:
        #     self.settings.load(cf)

    def execute_from_args(self, args=None):
        if args is None:
            args = sys.argv[1:]

        assert (isinstance(args, collections.Iterable))
        assert all([isinstance(x, str) for x in args])

        parser = self.create_parser()
        self.setup_parser(parser)

        arguments = parser.parse_args(args)
        return self.execute(arguments)

    def execute(self, arguments):
        # Program flow:
        #
        # Convert arguments to paramters (namespace -> dict)
        # Run App.consume_application_parameters()
        # App has subcommands?
        # `-> Yes
        #     Subcommand has been specified?
        #     `-> Yes
        #         Run ConsoleCommandExtension.main() with remaining parameters
        #     `-> No
        #         Run App.main() with remaining parameters
        # `-> No
        #     Run App.main() with all command line arguments

        parameters = vars(arguments)
        self.consume_application_parameters(parameters)

        cmds = dict(self.get_commands())

        if not cmds:
            return self.main(*+parameters)

        subcommand = parameters[SUBCOMMAND_ATTR]
        shift_dict(parameters)
        if not subcommand:
            return self.main(**parameters)

        return cmds[subcommand].execute(parameters)
