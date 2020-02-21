#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import time
import os
from glob import iglob

ent_old = {
        'gd': '<lb xmlns="http://www.tei-c.org/ns/1.0" break="no" rend="-" ed="#g"/>',
        'gl': '<lb xmlns="http://www.tei-c.org/ns/1.0" ed="#g"/>',
        'bd': '<lb xmlns="http://www.tei-c.org/ns/1.0" break="no" rend="-" ed="#b"/>',
        'bl': '<lb xmlns="http://www.tei-c.org/ns/1.0" ed="#b"/>',
        'jj': '<choice xmlns="http://www.tei-c.org/ns/1.0"><orig xmlns="http://www.tei-c.org/ns/1.0">j</orig><reg xmlns="http://www.tei-c.org/ns/1.0" type="j">i</reg></choice>',
        'uu': '<choice xmlns="http://www.tei-c.org/ns/1.0"><orig xmlns="http://www.tei-c.org/ns/1.0">v</orig><reg xmlns="http://www.tei-c.org/ns/1.0" type="v">u</reg></choice>',
        }

ent = [
        ['<lb xmlns="http://www.tei-c.org/ns/1.0" break="no" rend="-" ed="#g"/>', 'gd'],
        ['<lb xmlns="http://www.tei-c.org/ns/1.0" ed="#g"/>', 'gl'],
        ['<lb xmlns="http://www.tei-c.org/ns/1.0" break="no" rend="-" ed="#b"/>', 'bd'],
        ['<lb break="no" rend="-" ed="#b"/>', 'bd'],
        ['<lb xmlns="http://www.tei-c.org/ns/1.0" ed="#b"/>', 'bl'],
        ['<lb ed="#b"/>', 'bl'],
        ['<choice xmlns="http://www.tei-c.org/ns/1.0"><orig xmlns="http://www.tei-c.org/ns/1.0">j</orig><reg xmlns="http://www.tei-c.org/ns/1.0" type="j">i</reg></choice>', 'jj'],
        ['<choice xmlns="http://www.tei-c.org/ns/1.0"><orig xmlns="http://www.tei-c.org/ns/1.0">v</orig><reg xmlns="http://www.tei-c.org/ns/1.0" type="v">u</reg></choice>', 'uu'],
        ]

def entitize (filename):
    ''' Replace long tags with their corresponding entities '''

    # Backup original file
    datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
    input_filename = ''.join(['../xml/', filename, '.xml'])
    #backup_filename = '_'.join([datetime, ms, 'id-spreading-backup.xml'])
    #backup_filename = input_filename.replace('.xml', '_backup_before_entitization_' + datetime + '.xml')
    backup_filename = ''.join(['../xml/ripostiglio/backup/backup_entitization/',
        datetime, '_backup_before_entitization_of_', filename, '.xml'])
    os.system('cp %s %s' % (input_filename, backup_filename)) # Create backup of old file

    with open (input_filename, 'r') as IN:
        output_filename = input_filename.replace('.xml', '_with_entities.xml')
        with open (output_filename, 'w') as OUT:
            for l in IN:
                if l.startswith('<?') or l.startswith('<!ENTITY'):
                    pass
                else:
                    for e in ent:
                        l = l.replace(e[0], '&%s;' % (e[1]))
                print(l, file=OUT, end='')

    os.system('mv %s %s' % (output_filename, input_filename)) # Overwrite original file

'''
entitize('a_juxta')
entitize('bonetti_juxta')
entitize('b')
'''

for f in iglob('../xml/*.xml'):
    base = f.split('/')[-1].split('.')[0]
    print(base)
    entitize(base)
