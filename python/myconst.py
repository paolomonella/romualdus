#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

# File paths
xmlpath = '../xml/'
# simplifiedpath = '../xml/juxtacommons/'
simplifiedpath = '../xml/'
csvpath = '../csv/'
htmlpath = '../html/'
jsonpath = '../json/'
simplifiedsuffix = '-simple'
juxta_par_and_sigla_suffix = '-par'


# Metatext markers
# The e.text of HTML elements having @class="pb">, @class="garufi" etc.
# should not undergo the GL-to-AL substitutions
# (but their e.tail should):
metatextlist = ['pb', 'cb', 'garufi', 'note']

# XML/HTML namespaces

ns = {
    # for TEI XML:
    't': 'http://www.tei-c.org/ns/1.0',
    # for attributes like xml:id:
    'xml': 'http://www.w3.org/XML/1998/namespace',
    # for (X)HTML output
    'h': 'http://www.w3.org/1999/xhtml'}

tei_ns = "{%s}" % ns['t']
xml_ns = "{%s}" % ns['xml']
html_ns = "{%s}" % ns['h']


# Whitespace and punctuation
# These whitespace Unicode chars will be allowed at both GL and AL:
myspace = [' ', '\n', '\t']

# alp = A(lphabetic) L(ayer) P(unctuation).
# These chars are AL punctuation that will nevertheless be allowed also
# in the GL XML code and will be removed when extracting/visualizing the GL
alp = [r'.', ',', ':', ';', '!', '?', "'", '–', '—', '(', ')', '…']

# These chars will be considered legal by the lint at both GL and AL:
legal = myspace + alp
