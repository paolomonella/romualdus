#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module includes one big function, extracting/dividing
    the layers from the TEI XML source file. See the documentation
    of the function below for details.
    '''

from lxml import etree

from myconst import xmlpath, ns, tei_ns


def a_unifier(siglum1='a1', siglum2='a2', uniSiglum='a-1and2unified'):
    xmlfile1 = '%s%s.xml' % (xmlpath, siglum1)
    tree1 = etree.parse(xmlfile1)
    body1 = tree1.find('.//t:body', ns)

    xmlfile2 = '%s%s.xml' % (xmlpath, siglum2)
    tree2 = etree.parse(xmlfile2)
    body2 = tree2.find('.//t:body', ns)

    for child in body2:
        if child.tag != tei_ns + 'interp' and \
           child.get('type') != 'bonetti-is-collation-exemplar-from-here-on':
            body1.append(child)

    print(('\n[a_rearranger.py]: I\'m re-unifying '
           '{}.xml and {}.xml into {}.xml '
           '(for the old GL/AL HTML'
           'visualization) ').format(siglum1, siglum2, uniSiglum))

    xmlfileUnified = '%s%s.xml' % (xmlpath, uniSiglum)

    tree1.write(xmlfileUnified, encoding='UTF-8', method='xml',
                pretty_print=True, xml_declaration=True)
