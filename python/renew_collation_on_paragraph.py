#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This script re-collates paragraph xmlid and replaces
    its collation in juxta_file (e.g. m1.xml or m2-charlie.xml
    CollateX documentation:
        http://interedition.github.io/collatex/pythonport.html
    With 'dry', don't overwrite original juxta file.
    '''

from lxml import etree
from collatex import Collation, collate
from myconst import ns
from shutil import copyfile, move
from datetime import datetime
import sys

#######################
# Files and variables #
#######################

debug = False
dry = False
chunk_file = '2-bravo'

if chunk_file == '1':

    print_siglum = 'wit-42000'  # Garufi
    print_file = '../xml/g-simple.xml'

    # MS A o A2 (Not taking MS O into account: I won't collate O)
    ms_siglum = 'wit-41999'
    ms_file = '../xml/a1-simple.xml'

    juxta_file = '../xml/m1.xml'
    juxta_file_out = '../xml/m1-collatex-out.xml'

elif chunk_file == '2-alfa':

    print_siglum = 'wit-42040'  # Bonetti
    print_file = '../xml/bonetti-2-alfa-simple.xml'

    # MS A o A2 (Not taking MS O into account: I won't collate O)
    ms_siglum = 'wit-42039'
    ms_file = '../xml/a2-sorted-2-alfa-simple.xml'

    juxta_file = '../xml/m2-alfa.xml'
    juxta_file_out = '../xml/m2-alfa-collatex-out.xml'

elif chunk_file == '2-bravo':

    print_siglum = 'wit-42008'  # Bonetti
    print_file = '../xml/bonetti-2-bravo-simple.xml'

    # MS A o A2 (Not taking MS O into account: I won't collate O)
    ms_siglum = 'wit-42007'
    ms_file = '../xml/a2-sorted-2-bravo-simple.xml'

    juxta_file = '../xml/m2-bravo.xml'
    juxta_file_out = '../xml/m2-bravo-collatex-out.xml'

elif chunk_file == '2-charlie':

    print_siglum = 'wit-41981'  # Bonetti
    print_file = '../xml/bonetti-2-charlie-simple.xml'

    ms_siglum = 'wit-41980'  # MS A (non so se anche A2)
    ms_file = '../xml/a2-sorted-2-charlie-simple.xml'

    juxta_file = '../xml/m2-charlie.xml'
    juxta_file_out = '../xml/m2-charlie-collatex-out.xml'


########################################
# Create backup of original Juxta file #
########################################

now = datetime.now()
time_stamp = now.strftime('_orig_%Y-%m-%d_%H-%M-%S')
# os.rename(juxta_file, juxta_file + '_' + time_stamp)
backup_filename = juxta_file.replace('.xml', '%s.xml' % time_stamp)
copyfile(juxta_file, backup_filename)

print('[renew_collation_on_paragraph.py]\n')
print('Working on file {}\nCreated backup file in {}\n'.format(
    juxta_file, backup_filename))

# Get xml:id as argument
try:
    xmlid = sys.argv[1]
    print('Working on paragraph with xmlid «{}»:\n'.format(xmlid))
except IndexError as error:
    print('Error ({}): please provide the xml:id to re-collate'.format(
        error))


################
# Input chunks #
################

def chunk(in_file, xmlid):

    # Input chunk from input juxta file

    chunk = ''
    found = False
    start_tag = '[p xml:id="%s"]' % xmlid
    end_tag = '[/p]'
    with open(in_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        # The following code will fail if start and end
        # tag are in the same line

        # If you met the start tag
        if start_tag in line:
            if debug:  # debug
                print('Found start')
            found = True
            before = line.split(start_tag)[0]
            after = line.split(start_tag)[1]
            if debug:
                print('Before: «{}»'.format(before))
                print('Start tag: «{}»'.format(start_tag))
                print('After: «{}»'.format(after))
            # Old code:
            # Add the 2nd part of line to the chunk
            # chunk = ''.join([start_tag, after])
            # New code:
            chunk = after
            # Leave the placeholder in its place
            # in the file (in a blank new line)
            # line = ''.join([before, start_tag, '\n', placeholder])

        elif (found is True and end_tag in line):
            found = False
            before = line.split(end_tag)[0]
            after = line.split(end_tag)[1]
            if debug:
                print('Before: «{}»'.format(before))
                print('End tag: «{}»'.format(end_tag))
                print('After: «{}»'.format(after))
            # Old code:
            # Add the 1st part it to he chunk
            # chunk = ''.join([chunk, before, end_tag])
            # New code:
            chunk = ''.join([chunk, before])
            # line = ''.join([end_tag, after])

        # If you had met the start tag earlier
        elif found is True:
            # Add it to the chunk
            chunk = ''.join([chunk, line])
            # Remove it from the file
            line = ''

    if debug:  # debug
        print(chunk)
    return chunk


print_chunk = chunk(print_file, xmlid)
ms_chunk = chunk(ms_file, xmlid)

if print_chunk == '' and ms_chunk == '':
    print(('\n\t[renew_collation_on_paragraph.py] Paragraph {}'
          ' NOT FOUND in file {}\n\tIs {} the right file?\n\n').format(
        xmlid, juxta_file, juxta_file))


###########
# Collate #
###########

collation = Collation()
collation.add_plain_witness(print_siglum, print_chunk)
collation.add_plain_witness(ms_siglum, ms_chunk)
output_string = collate(collation, output='tei',
                        segmentation=False,
                        near_match=True,
                        indent=False)


################################
# Add empty <rdg> when missing #
################################

element = etree.fromstring(output_string)
for app in element.findall('.//t:app', ns):
    if len(app) == 1:
        rdg = app[0]
        wit = rdg.get('wit')
        # If output only has print reading:
        if wit == '#%s' % print_siglum:
            ms_rdg = etree.SubElement(app, '{%s}rdg' % ns['t'])
            ms_rdg.set('wit', '#%s' % ms_siglum)
            app.append(ms_rdg)
        # If output only has MS reading:
        elif wit == '#%s' % ms_siglum:
            print_rdg = etree.SubElement(app, '{%s}rdg' % ns['t'])
            print_rdg.set('wit', '#%s' % print_siglum)
            app.insert(0, print_rdg)  # Print reading comes first

output_str2 = (etree.tostring(element, encoding='Unicode'))
start_interedition = ('<cx:apparatus xmlns="http://www.tei-c.org/ns/1.0"'
                      ' xmlns:cx="http://interedition.eu/collatex/ns/1.0">')
end_interedition = '</cx:apparatus>'
output_str2 = output_str2.replace(start_interedition, '')
output_str2 = output_str2.replace(end_interedition, '')
output_str2 = output_str2.replace('\n', '')
output_str2 = output_str2.replace('\n\n', '\n')  # Remove empty lines
output_str2 = output_str2.replace('<app>', '\n<app>')
output_str2 = output_str2.replace('<rdg', '\n   <rdg')
# output_str2 = output_str2.replace('</rdg>', '</rdg>\n')
output_str2 = output_str2.replace('</app>', '\n</app>')

if True:
    print(output_str2)


##################
# Output to file #
##################

start_tag = '[p xml:id=&quot;%s&quot;]' % xmlid
end_tag = '[/p]'
with open(juxta_file, 'r') as f:
    lines = f.readlines()

with open(juxta_file_out, 'w') as f:
    found = False
    for line in lines:
        # If you met the start tag
        if start_tag in line:
            if debug:  # debug
                print('Found start')
            found = True
            before = line.split(start_tag)[0]
            after = line.split(start_tag)[1]
            if debug:
                print('Before: «{}»'.format(before))
                print('Start tag: «{}»'.format(start_tag))
                print('After: «{}»'.format(after))
            new_line = ''.join([before, start_tag, output_str2])
            print(new_line, file=f, end='')

        elif (found is True and end_tag in line):
            found = False
            before = line.split(end_tag)[0]
            after = line.split(end_tag)[1]
            if debug:
                print('Before: «{}»'.format(before))
                print('End tag: «{}»'.format(end_tag))
                print('After: «{}»'.format(after))
            new_line = ''.join([end_tag, after])
            print(new_line, file=f, end='')

        # If you had met the start tag earlier
        # (if we're in the chunk)
        elif found is True:
            pass

        # If we're outside of the chunk
        elif found is False:
            new_line = line
            print(new_line, file=f, end='')

if not dry:
    move(juxta_file_out, juxta_file)
# copyfile(juxta_file, backup_filename)
