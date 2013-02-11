#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import re

from cliff.command import Command

minword = 3          # минимальная длина последнего слова в строке
endpos = '!.?'       # Знаки окончания предложения
reg_1 = re.compile(r'([,!\.\?:…])(?=\s)')
wordgrammar = {
    'and': 15, 'where': 10, 'while': 10, 'with': 10, 'how': 10,
    'before': 10, 'was': 8,
	'the': 3, 'he': 4, 'to': 3
}


class ParserText(Command):
    """Parser text tuple and preparation for a network file."""

    log = logging.getLogger(__name__)
    FIFO = []
    depthword = 0

    def probabilityfun(self, word, pos):
        p = 20
        if len(word) < minword + 2:
            p += minword + 2 - len(word)
        # if abs(pos - self.depthword / 2) < 3:
            # p += 3 - abs(pos - self.depthword / 2)
        if pos > self.depthword - 5:
            p -= 5 - (self.depthword - pos)
        if word in wordgrammar: p += wordgrammar[word]
        self.log.debug('TEXTPARSER:probabilityfun word=%s, pos=%d, depth=%d, rating=%d' \
            % (word, pos, self.depthword, p))
        return p

    def splitlongsubstring(self, tempstr, FIFO, maxlen):
        vsum = 0
        substword = []
        words = tempstr.split(' ')  # разбили фразу по словам...
        self.depthword = len(words)
        lenwords = map(lambda x: len(x), words)  # список длин слов
        # список вероятностей переноса
        probabilitywords = [self.probabilityfun(words[x], x) for x in xrange(self.depthword)]
        # Считаем подстроки
        for x in xrange(self.depthword):
            vsum += lenwords[x]  # Кол-во символов, если добавить слово

            if vsum > maxlen - 13:  # Собственно критерий переноса
                ps = probabilitywords[max(0, x - 6):x]
                ps.reverse()
                i = 5 - ps.index(max(ps)) + max(0, x - 6)
                vsum = reduce(lambda res, x: res + x, lenwords[i:x], )
                self.log.debug('TEXTPARSER:splitlongsubstring x=%d, i=%d, vsum=%d' % (x, i, vsum))
                substword.append(i)

        # Формируем подстроки
        if len(substword) == 0:  # Пограничный случай, подстрока == WIDE_WORLD
            FIFO.append(tempstr.lstrip())
            return ''

        FIFO.append(' '.join(words[:substword[0]]))
        for x in xrange(len(substword) - 1):
            FIFO.append(' '.join(words[substword[x]:substword[x + 1]]))
        return ' '.join(words[substword[-1]:])

    def take_action(self, parsed_args):
        maxlen = int(self.app_args.max_wide)
        self.log.debug('PARSERTEXT: max_wide=%d' % maxlen)

        tempstr = ''
        for line in self.app.file_txt:
            if len(line) > maxlen:
                iter = reg_1.split(line)
                for subline in iter:
                    # Добавляем к строке знаки препинания
                    if len(subline) == 1:
                        tempstr += subline
                        continue

                    self.log.debug('PARSER: len=%s: tempstr - %s' % (len(tempstr), tempstr))

                    # Остатки больше maxlen, разбиваем на подстроки.
                    if len(tempstr) > maxlen:
                        tempstr = self.splitlongsubstring(tempstr, self.FIFO, maxlen)

                    # Можем собрать две части?
                    if len(subline) + len(tempstr) <= maxlen:
                        # Может не надо добавлять пару слов к концу предложения
                        if len(tempstr) > 1 and \
                           tempstr[-1] in endpos and \
                           len(subline) < maxlen / 4:
                            self.FIFO.append(tempstr.lstrip())
                            tempstr = subline.lstrip()
                        else:
                            tempstr += subline
                            continue
                    else:
                        if len(tempstr) > 0 and \
                           len(tempstr) < maxlen / 4 and\
                           not (tempstr[-1] in endpos):  # Вводный слова, обороты
                            tempstr += subline
                            continue

                        if len(tempstr.lstrip()) > 0:
                            self.FIFO.append(tempstr.lstrip())
                        tempstr = subline.lstrip()

                if len(tempstr) > maxlen:
                    tempstr = self.splitlongsubstring(tempstr, self.FIFO, maxlen)
                if len(tempstr) > 0:
                    self.FIFO.append(tempstr.lstrip())
                    tempstr = ''
            else:
                self.FIFO.append(line.lstrip())
        self.app.file_srt = self.FIFO
        return 0
