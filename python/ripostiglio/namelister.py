#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This script parses the ../xml/temp_g.xml file and lists
    the textual content of all its <rs> elements.  '''

import constants
from lxml import etree

def listrs (properNamesInputXmlFile, myNamespace):
    ''' Parse an xml file and print out a list of names marked
        with <rs> in that file. All names in the list are in lowercase.
        '''
    names_tree = etree.parse(properNamesInputXmlFile)
    rss = names_tree.findall('.//%srs' % myNamespace)
    for rs in rss:
        print(rs.text, end=',')
    print('\n---\n')


listrs('../xml/g.xml', constants.tei_ns) 
