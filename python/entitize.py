#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import time
import os
from glob import iglob

ent = [
        ['<lb xmlns="http://www.tei-c.org/ns/1.0" \
         break="no" rend="-" ed="#g"/>', 'gd'],
        ['<lb xmlns="http://www.tei-c.org/ns/1.0" ed="#g"/>', 'gl'],
        ['<lb xmlns="http://www.tei-c.org/ns/1.0" \
         break="no" rend="-" ed="#b"/>', 'bd'],
        ['<lb break="no" rend="-" ed="#b"/>', 'bd'],
        ['<lb xmlns="http://www.tei-c.org/ns/1.0" ed="#b"/>', 'bl'],
        ['<lb ed="#b"/>', 'bl'],
        ['<choice xmlns="http://www.tei-c.org/ns/1.0">\
         <orig xmlns="http://www.tei-c.org/ns/1.0">j</orig>\
         <reg xmlns="http://www.tei-c.org/ns/1.0" type="j">i</reg>\
         </choice>', 'jj'],
        ['<choice xmlns="http://www.tei-c.org/ns/1.0">\
         <orig xmlns="http://www.tei-c.org/ns/1.0">v</orig>\
         <reg xmlns="http://www.tei-c.org/ns/1.0" type="v">u</reg>\
         </choice>', 'uu'],
        ]


def entitize(filename):
    ''' Replace long tags with their corresponding entities '''

    # Backup original file
    datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
    input_filename = ''.join(['../xml/', filename, '.xml'])
    backup_filename = ''.join([
        '../xml/ripostiglio/backup/backup_entitization/',
        datetime,
        '_backup_before_entitization_of_',
        filename,
        '.xml'
    ])
    # Create backup of old file:
    os.system('cp %s %s' % (input_filename, backup_filename))

    with open(input_filename, 'r') as IN:
        output_filename = input_filename.replace('.xml', '_with_entities.xml')
        with open(output_filename, 'w') as OUT:
            for line in IN:
                if line.startswith('<?') or line.startswith('<!ENTITY'):
                    pass
                else:
                    for e in ent:
                        line = line.replace(e[0], '&%s;' % (e[1]))
                print(line, file=OUT, end='')

    # Overwrite original file:
    os.system('mv %s %s' % (output_filename, input_filename))


'''
entitize('a_juxta')
entitize('bonetti_juxta')
entitize('b')
'''

for f in iglob('../xml/*.xml'):
    base = f.split('/')[-1].split('.')[0]
    print(base)
    entitize(base)
