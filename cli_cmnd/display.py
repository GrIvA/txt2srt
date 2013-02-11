#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging

from cliff.command import Command

timestep_titr = 10
timestep_notitr = 2


class Display(Command):
    """Show SRT on display."""

    timestump = '00:00:20'
    titrnum = 0  # number titr

    log = logging.getLogger(__name__)

    @property
    def titrnumber(self):
        self.titrnum += 1
        return self.titrnum

    @property
    def starttime(self):
        self.timestump = self.addstump(timestep_notitr)
        return self.timestump

    @property
    def endtime(self):
        self.timestump = self.addstump(timestep_titr)
        return self.timestump

    def addstump(self, timestump):
        t = self.timestump.split(':')
        i, sec = divmod(int(t[2]) + timestump, 60)
        i, mn = divmod(i + int(t[1]), 60)
        hr = (i + int(t[0])) % 24
        return '%02d:%02d:%02d' % (hr, mn, sec)

    def safeprint(self, s):
        try:
            self.app.stdout.write(s)
        except UnicodeEncodeError:
            if sys.version_info >= (3,):
                self.app.stdout.write(s.encode('utf8').decode(sys.stdout.encoding))
            else:
                self.app.stdout.write(s.encode('utf8'))

    def take_action(self, parsed_args):
        for l in self.app.file_srt:
            if not self.app_args.no_time:
                self.app.stdout.write('%d\n' % self.titrnumber)
                self.app.stdout.write('%s,000 --> %s,900\n' % (self.starttime, self.endtime))
            self.safeprint(l + '\n')
            if not self.app_args.no_time: self.app.stdout.write('\n')
        return 0
