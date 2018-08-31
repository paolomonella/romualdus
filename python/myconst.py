#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

# File paths
csvpath = '../csv/'
xmlpath = '../xml/'
htmlpath = '../html/'

# Metatext markers
metatextlist = ['pb', 'cb', 'garufi', 'note']   # The e.text of HTML elements having @class="pb">, @class="garufi" etc.
                                                # should not undergo the GL-to-AL substitutions (but their e.tail should)

# XML/HTML namespaces
ns = {'t': 'http://www.tei-c.org/ns/1.0',               # for TEI XML
        'xml': 'http://www.w3.org/XML/1998/namespace',  # for attributes like xml:id
        'h': 'http://www.w3.org/1999/xhtml'}            # for (X)HTML output  

tei_ns  = "{%s}" % ns['t']
xml_ns  = "{%s}" % ns['xml']
html_ns = "{%s}" % ns['h']


# Whitespace and punctuation
myspace = [' ', '\n', '\t']             # These whitespace Unicode chars will be allowed at both GL and AL

alp = [r'.', ',', ':', ';', '!', '?', "'", '–', '—', '(', ')']   # alp = A(lphabetic) L(ayer) P(unctuation):
                                        # AL punctuation that will nevertheless be allowed also in the GL XML code.
                                        # These chars will be removed when extracting/visualizing the GL

legal = myspace + alp                   # These chars will be considered legal by the lint at both GL and AL:
