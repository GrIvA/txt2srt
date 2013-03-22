#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
from cliff.app import App
from cliff.commandmanager import CommandManager
# from cliff.command import Command

from cli_cmnd.file_list import Files
from cli_cmnd.file_list import ReadFile
from cli_cmnd.text_parser import ParserText
from cli_cmnd.display import Display


class GeneApp(App):
    file_txt = ()
    file_srt = []
    log = logging.getLogger(__name__)

    def __init__(self):
        command = CommandManager('gene.app')
        super(GeneApp, self).__init__(
            description='sample app',
            version='0.3',
            command_manager=command,
        )
        self.parser.add_argument(
            '-i', '--interprettry',
            default=False,
            action='store_true',
            help='try interpret the read file',
        )
        self.parser.add_argument(
            '-n', '--no-time',
            default=False,
            dest='no_time',
            action='store_true',
            help='no display number/time SRT line',
        )
        self.parser.add_argument(
            '-m', '--max-wide',
            action='store',
            dest='max_wide',
            # const=80,
            default=80,
            help='max wide each line',
        )
        commands = {
            'textparse': ParserText,
            'readfile': ReadFile,
            'files': Files,
            'display': Display
        }
        for k, v in commands.iteritems():
            command.add_command(k, v)

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        # print cmd.__dict__
        if cmd.app_args.interprettry and cmd.__class__.__name__ == 'ReadFile':
            # print self.file_txt
            self.run_subcommand(['textparse'])
            self.run_subcommand(['display'])
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    app = GeneApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
