#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import time
import codecs  # Модуль для чтения в разных кодировках

from cliff.lister import Lister
from cliff.command import Command


class Files(Lister):
    """Show text file in the current directory.

    The file name and size are printed by default."""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_arg):
        return (('Name', 'Size', 'File create time'),
                ((n, os.stat(n).st_size, time.ctime(os.stat(n).st_ctime))
                for n in os.listdir('.') if n[-3:] == 'txt'))


class ReadFile(Command):
    """Read txt file from disk in tuple."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ReadFile, self).get_parser(prog_name)
        parser.add_argument('filename', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        filetuple = []
        self.log.debug('FILEREAD: start...')
        try:
            with codecs.open(parsed_args.filename, encoding='UTF-8') as file_object:
            # with закроет файл, если что-то пойдет не так
                for line in file_object:
                    # Удаляем лишние пробелы и табы
                    line = line.strip(' \t\n')
                    line = ' '.join(line.split())
                    if len(line) > 1: filetuple.append(line)
        except IOError as er:  # Обработка отсутствия файла
            self.log.error(u'Can\'t open the "{0}" file'.format(er.filename))
        if len(filetuple) > 0: self.app.file_txt = tuple(filetuple)
        self.log.info('READFILE: importing %s line(s)' % len(filetuple))
        return 0
