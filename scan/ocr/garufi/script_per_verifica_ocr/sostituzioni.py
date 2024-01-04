#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob, re, time, os

R = {
                ',,,':    ',',
                ',,':    ',',
                ',,.':    '.',
                '"':    '',
                '«':    '',
                '»':    '',
                '*':    '',
                '„':    '',
                '–':    '-',
                '—':    '-',
                '^':    '',
                '  ':    ' ',
                ' .':    '.',
                ' ,':    ',',
        }

for path in glob.glob('g*txt'):
    with open(path) as IN:

        temppath = 'temp_' + path

        with open(temppath, 'w') as OUT:

            # Backup old file
            datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
            backup_filename = ''.join(['ripostiglio/', datetime, '_', path])
            os.system('cp %s %s' % (path, backup_filename))

            for l in IN:
                l = re.sub('\d', '', l)    # Remove digits
                for u in R:
                    l = l.replace(u, R[u])
                l = l.strip()
                print(l, file=OUT)
    os.system('mv %s %s' % (temppath, path))
