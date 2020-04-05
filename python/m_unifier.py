#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module unifies m1.xml and m2.xml into one file '''

from shutil import copyfile
from lxml import etree
from myconst import ns, xmlpath

debug = False


def unify():
    ''' Unify the files '''

    # Parse input XML files:
    m1_file = '%s%s.xml' % (xmlpath, 'm1-par-out')
    m1_tree = etree.parse(m1_file)

    m2_alfa_file = '%s%s.xml' % (xmlpath, 'm2-alfa-par-out')
    m2_alfa_tree = etree.parse(m2_alfa_file)

    m2_bravo_file = '%s%s.xml' % (xmlpath, 'm2-bravo-par-out')
    m2_bravo_tree = etree.parse(m2_bravo_file)

    m2_charlie_file = '%s%s.xml' % (xmlpath, 'm2-charlie-par-out')
    m2_charlie_tree = etree.parse(m2_charlie_file)

    # This is the file in which I edited the teiHeader by hand
    template_file = '%s%s.xml' % (xmlpath, 'teiHeader_template.xml')

    # Old code:
    # Copy m1-par-out.xml to template.xml
    # copyfile(m1_file, template_file)

    # Parse template.xml
    template_tree = etree.parse(template_file)

    # Set output file name chronicon.xml
    chronicon_file = '%s%s.xml' % (xmlpath, 'chronicon')

    # Find <body> elements
    m1_body = m1_tree.find('.//t:body', ns)
    m2_alfa_body = m2_alfa_tree.find('.//t:body', ns)
    m2_bravo_body = m2_bravo_tree.find('.//t:body', ns)
    m2_charlie_body = m2_charlie_tree.find('.//t:body', ns)
    template_body = template_tree.find('.//t:body', ns)

    # Empty <body> of template.xml
    for x in template_body:
        template_body.remove(x)

    # Pour content of m1.xml's <body> into template.xml:
    for input_body in [m1_body, m2_alfa_body, m2_bravo_body, m2_charlie_body]:
        for x in input_body:
            template_body.append(x)

    # Write tree to output file template.xml:
    template_tree.write(chronicon_file,
                        encoding='UTF-8', method='xml',
                        pretty_print=True, xml_declaration=True)
