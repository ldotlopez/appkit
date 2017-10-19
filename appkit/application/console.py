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


import abc
import argparse
import collections
import functools
import sys

from appkit import application


def shift_namespace_keys(ns):
    if not hasattr(ns, '_subcommand'):
        raise ValueError('no _subcommand attr in ns')

    # Drop the value
    sub_value = ns._subcommand
    delattr(ns, '_subcommand')

    attrs = [attr for attr in vars(ns)
             if (attr == '_subcommand_' + sub_value or
                 attr.startswith('_subcommand_' + sub_value + '_'))]

    attrs_and_parts = [(attr, attr.split('_')) for attr in attrs]
    attrs_and_parts = sorted(attrs_and_parts, key=lambda x: len(x[1]))

    for (oldattr, parts) in attrs_and_parts:
        newattr = '_subcommand' + ''.join('_' + part for part in parts[3:])
        setattr(ns, newattr, getattr(ns, oldattr))
        delattr(ns, oldattr)


class ConsoleCommandExtension_old(application.Applet, application.Extension):
    HELP = ''
    PARAMETERS = ()

    def setup_argparser(self, parser, base=None):
        if self.children:
            dest = base + '-subcommand' if base else 'subcommand'
            chidren_parsers = parser.add_subparsers(dest=dest)
            for (name, child) in self.children.items():
                child_parser = chidren_parsers.add_parser(name)
                base = base + '-' + name if base else name
                child.setup_argparser(child_parser, base)

        for param in self.PARAMETERS:
            fn = parser.add_argument

            if param.short_flag:
                fn = functools.partial(fn, param.short_flag)

            fn = functools.partial(fn, param.long_flag)
            fn(**param.kwargs)

    @abc.abstractmethod
    def main(self, app, args):
        raise NotImplementedError()


class ConsoleCommandExtension(application.Applet,  application.Extension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup_parser(self, parser, command_path):
        # Prepare a subparser for our children
        if self.children:
            dest = '_subcommand_' + '_'.join(command_path)
            children_parsers = parser.add_subparsers(dest=dest)

        for (name, child) in self.children.items():
            child_parser = children_parsers.add_parser(name)
            child.setup_parser(
                parser=child_parser, command_path=command_path + [name])

        for parameter in self.PARAMETERS:
            fn = parser.add_argument
            if parameter.short_flag:
                fn = functools.partial(fn, parameter.short_flag)
            if parameter.long_flag:
                fn = functools.partial(fn, parameter.long_flag)
            fn(**parameter.kwargs)

    def execute_from_args(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]

        parser = self.setup_parser()
        arguments = parser.parse_args(argv)
        return self.execute(arguments)

    def execute(self, arguments):
        # If we haven't children, _subcommand mustn't be set
        if not self.children:
            assert not hasattr(arguments, '_subcommand')

        # however if we have children, _subcommand must be valid or None
        else:
            assert (
                arguments._subcommand is None or
                arguments._subcommand in self.children)

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


class ConsoleAppMixin:
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
            children_parser = parser.add_subparsers(dest='_subcommand')

        for (name, cmd) in cmds:
            cmd_parser = self.create_command_subparser(
                children_parser, name, cmd)

            cmd.setup_parser(cmd_parser, [name])

    def execute_from_args_(self, *args):
        assert (isinstance(args, collections.Iterable))
        assert all([isinstance(x, str) for x in args])

        argparser = self.build_base_argument_parser()
        commands = list(self.get_commands())

        if False and len(commands) == 1:
            # Single command mode
            (cmdname, cmdext) = commands[0]
            cmdext.setup_argparser(argparser)
            args = argparser.parse_args(args)

        else:
            subparser = argparser.add_subparsers(
                title='subcommands',
                dest='subcommand',
                description='valid subcommands',
                help='additional help')

            # Multiple command mode
            subargparsers = {}
            for (cmdname, cmdext) in sorted(commands):
                subargparsers[cmdname] = subparser.add_parser(
                    cmdname,
                    help=cmdext.HELP)
                cmdext.setup_parser(subargparsers[cmdname])

            args = argparser.parse_args(args)
            if not args.subcommand:
                argparser.print_help()
                return

            cmdname = args.subcommand

        try:
            # Reuse commands
            tmp = dict(commands)
            return tmp[cmdname].execute(args)

        except application.ArgumentsError as e:
            if len(commands) > 1:
                subargparsers[args.subcommand].print_help()
            else:
                argparser.print_help()

            print("\nError message: {}".format(e), file=sys.stderr)

        except Exception as e:
            msg = "Unhandled exception «{exctype}» from «{name}»: {e}"
            msg = msg.format(
                exctype=e.__class__.__module__ + '.' + e.__class__.__name__,
                name=tmp[cmdname].__class__,
                e=str(e))
            self.logger.critical(msg)
            raise

    def execute_from_args(self, args=None):
        if args is None:
            args = sys.argv[1:]

        assert (isinstance(args, collections.Iterable))
        assert all([isinstance(x, str) for x in args])

        parser = self.create_parser()
        self.setup_parser(parser)

        arguments = parser.parse_args(args)
        return self.execute(arguments)

    def consume_application_arguments(self, arguments):
        kwargs = {}
        for name in 'verbose quiet config_files plugins'.split():
            kwargs[name] = getattr(arguments, name)
            delattr(arguments, name)

        self.params = self.__class__._Parameters(**kwargs)

    def execute(self, arguments):
        def _run_main():
            return self.main(**vars(arguments))

        print(repr(arguments))
        cmds = self.get_commands()

        if not cmds:
            """
            App without commands, just use Application.main()
            """
            return _run_main()

        subcommand = getattr(arguments, '_subcommand', None)
        if subcommand is None:
            return _run_main()

        cmd = self.get_command(subcommand)
        self.consume_application_arguments(arguments)

        shift_namespace_keys(arguments)
        return cmd.execute(arguments)
