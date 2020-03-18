#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module includes one big function, extracting/dividing
    the layers from the TEI XML source file. See the documentation
    of the function below for details.
    '''

from lxml import etree
from copy import deepcopy

from myconst import xmlpath, splitpath, ns


def a_splitter(siglum_a1='a1', siglum_a2='a2',
               siglum_uni='a', quiet=False):

    # File names
    xmlfile_uni = '%s%s.xml' % (xmlpath, siglum_uni)
    xmlfile_a1 = '%s%s.xml' % (splitpath, siglum_a1)
    xmlfile_a2 = '%s%s.xml' % (splitpath, siglum_a2)

    # Parse a.xml
    tree_uni = etree.parse(xmlfile_uni)

    # Create deep copies of the original tree for a1 and for a2
    # (because the teiHeader and the general XML tree structure
    #  of a1.xml and a2.xml will be the same of that of a.xml)
    tree_a1 = deepcopy(tree_uni)
    tree_a2 = deepcopy(tree_uni)

    # Find the two <body>es
    body_a1 = tree_a1.find('.//t:body', ns)
    body_a2 = tree_a2.find('.//t:body', ns)

    # a1
    light = 'green'
    for child in body_a1:
        if (child.tag == '{%s}milestone' % (ns['t']) and
            child.get('type') ==
                'bonetti-is-collation-exemplar-from-here-on'):
            light = 'red'
        if light == 'red':
            body_a1.remove(child)

    # a2
    light = 'red'
    for child in body_a2:
        if (child.tag == '{%s}milestone' % (ns['t']) and
            child.get('type') ==
                'bonetti-is-collation-exemplar-from-here-on'):
            light = 'green'
        if light == 'red':
            body_a2.remove(child)

    # Insert <interp>s into a2.xml too
    interps = body_a1.findall('.//t:%s' % ('interp'), ns)
    for interp in reversed(interps):
        new_interp = deepcopy(interp)
        body_a2.insert(0, new_interp)
        print(''.join(new_interp.itertext()))

    if not quiet:
        print(('\n[a_splitter.py]: I\'m splitting'
               ' {}.xml into {}.xml and {}.xml'
               ' for separate JuxtaCommons'
               ' collation.').format(siglum_uni, siglum_a1, siglum_a2))

    # Write a1.xml
    tree_a1.write(xmlfile_a1, encoding='UTF-8', method='xml',
                  pretty_print=True, xml_declaration=True)
    # Write a2.xml
    tree_a2.write(xmlfile_a2, encoding='UTF-8', method='xml',
                  pretty_print=True, xml_declaration=True)


a_splitter()
