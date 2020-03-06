#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module includes one big function, extracting/dividing
    the layers from the TEI XML source file. See the documentation
    of the function below for details.
    '''

from lxml import etree

import myconst
from myconst import ns, tei_ns

xmlfile1 = '%s/a1.xml' % (myconst.xmlpath)
tree1 = etree.parse(xmlfile1)
body1 = tree1.find('.//t:body', ns)

xmlfile2 = '%s/a2.xml' % (myconst.xmlpath)
tree2 = etree.parse(xmlfile2)
body2 = tree2.find('.//t:body', ns)

for child in body2:
    if child.tag != tei_ns + 'interp' and \
       child.get('type') != 'bonetti-is-collation-exemplar-from-here-on':
        body1.append(child)

xmlfileUnified = '%s/a-1and2unified.xml' % (myconst.xmlpath)

print('a_rearranger.py: I\'m re-arranging a1.xml and a2.xml \
      into a-1and2unified.xml (for the old GL/AL HTML visualization)')
tree1.write(xmlfileUnified, encoding='UTF-8', method='xml',
            pretty_print=True, xml_declaration=True)
