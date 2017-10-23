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


SUBCOMMAND_ATTR = '_subcommand'
SUBCOMMANDS_SEPARATOR = '_'

assert SUBCOMMAND_ATTR.startswith(SUBCOMMANDS_SEPARATOR)


def shift_namespace_keys(ns):
    """
    Utility function to rewrite arguparse.Namespace in order to pass it to
    subcommands
    """

    if not hasattr(ns, SUBCOMMAND_ATTR):
        msg = "Namespace has no {attr} attribute"
        msg = msg.format(attr=SUBCOMMAND_ATTR)
        raise ValueError(ns, msg)

    # Get and delete sub_attr
    sub_value = getattr(ns, SUBCOMMAND_ATTR)
    delattr(ns, SUBCOMMAND_ATTR)

    # Get all related attributes:
    # - The inmediate _subcommand_x
    # - Others like _subcommand_x_*
    discr = SUBCOMMAND_ATTR + SUBCOMMANDS_SEPARATOR + sub_value
    attrs = [attr for attr in vars(ns)
             if (attr == discr or
                 attr.startswith(discr + SUBCOMMANDS_SEPARATOR))]

    # Split those attrs into pieces and sort by the number of pieces
    attrs_and_parts = [
        (attr, attr.split(SUBCOMMANDS_SEPARATOR))
        for attr in attrs]
    attrs_and_parts = sorted(
        attrs_and_parts,
        key=lambda x: len(x[1]))

    # Rewrite namespace moving attributes
    for (oldattr, parts) in attrs_and_parts:
        newattr = (
            SUBCOMMAND_ATTR +
            ''.join(SUBCOMMANDS_SEPARATOR + part for part in parts[3:]))
        setattr(ns, newattr, getattr(ns, oldattr))
        delattr(ns, oldattr)


class ConsoleCommandExtension(application.Applet,  application.Extension):
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

    def execute(self, arguments):
        # If we haven't children, _subcommand mustn't be set
        if not self.children:
            assert not hasattr(arguments, SUBCOMMAND_ATTR)

        # however if we have children, _subcommand must be valid or None
        else:
            subcommand = getattr(arguments, SUBCOMMAND_ATTR)
            assert subcommand is None or subcommand in self.children

        # If we have children and a valid _subcommand go deeper
        if not self.children or arguments._subcommand is None:
            return self.main(**vars(arguments))

        # Run own's main
        else:
            # Strip _subcommand
            subcommand = arguments._subcommand

            # Replace sub args
            shift_namespace_keys(arguments)
            return self.children[subcommand].execute(arguments)


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
        kwargs = {}
        for name in 'verbose quiet config_files plugins'.split():
            kwargs[name] = parameters.pop(name)

        self.parameters = self.__class__._Parameters(**kwargs)

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
        # Parse arguments
        # Run App.consume_application_parameters()
        # App has subcommands?
        # `-> No
        #     Run App.main() with all command line arguments
        # `-> Yes
        #     Subcommand has been specified?
        #     `-> No
        #         Run App.main() with remaining parameters
        #     `-> Yes
        #         Run ConsoleCommandExtension.main() with remaining parameters

        params = vars(arguments)
        self.consume_application_parameters(params)

        cmds = self.get_commands()

        # def _run_main():
        #     return self.main(**vars(arguments))

        # cmds = self.get_commands()

        # if not cmds:
        #     return _run_main()

        # subcommand = getattr(arguments, '_subcommand', None)
        # if subcommand is None:
        #     return _run_main()

        # cmd = self.get_command(subcommand)
        # self.consume_application_arguments(arguments)

        # shift_namespace_keys(arguments)
        # return cmd.execute(arguments)
