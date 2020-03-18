#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module unifies m1.xml and m2.xml into one file '''

from shutil import copyfile
from lxml import etree
from myconst import ns, xmlpath

debug = False


def unify():
    ''' Unify the two files '''

    # Parse m1.xml:
    m1_file = '%s%s.xml' % (xmlpath, 'm1-par-out')
    m1_tree = etree.parse(m1_file)

    # Parse m2.xml:
    m2_file = '%s%s.xml' % (xmlpath, 'm2-par-out')
    m2_tree = etree.parse(m2_file)

    # Copy m1.xml to template.xml
    template_file = '%s%s.xml' % (xmlpath, 'template')
    copyfile(m1_file, template_file)

    # Parse template.xml
    template_tree = etree.parse(template_file)

    # Set output file name chronicon.xml
    chronicon_file = '%s%s.xml' % (xmlpath, 'chronicon')

    # Find <body> elements
    m1_body = m1_tree.find('.//t:body', ns)
    m2_body = m2_tree.find('.//t:body', ns)
    template_body = template_tree.find('.//t:body', ns)

    # Empty <body> of template.xml
    for x in template_body:
        template_body.remove(x)

    # Pour content of m1.xml's <body> into template.xml:
    for x in m1_body:
        template_body.append(x)

    # Pour content of m2.xml's <body> into chronicon.xml:
    for x in m2_body:
        template_body.append(x)

    # Write tree to output file template.xml:
    template_tree.write(chronicon_file,
                        encoding='UTF-8', method='xml',
                        pretty_print=True, xml_declaration=True)
