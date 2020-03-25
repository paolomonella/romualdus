#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This script re-collates paragraph xmlid and replaces
    its collation in juxta_file (e.g. m1.xml or m2-charlie.xml
    CollateX documentation:
        http://interedition.github.io/collatex/pythonport.html
    '''

from lxml import etree
from collatex import Collation, collate
from myconst import ns

#######################
# Files and variables #
#######################

debug = False

print_siglum = 'wit-41980'  # m2-charlie.xml
print_file = '../xml/bonetti-2-charlie-simple.xml'
ms_siglum = 'wit-41981'  # m2-charlie.xml (MS A)
ms_file = '../xml/a2-sorted-2-charlie-simple.xml'

juxta_file = '../xml/m2-charlie.xml'
juxta_file_out = '../xml/m2-charlie-collatex-out.xml'

xmlid = 'g190.9-191.2'


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


print_chunk = chunk(ms_file, xmlid)
ms_chunk = chunk(print_file, xmlid)


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
output_str2 = output_str2.replace('<app>', '\n<app>\n')
output_str2 = output_str2.replace('<rdg', '   <rdg')
output_str2 = output_str2.replace('</rdg>', '</rdg>\n')

if True:
    print('[collatex_for_romualdus_simple_text.py]')
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
            new_line = ''.join([before, start_tag, 'foooo', output_str2])
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
