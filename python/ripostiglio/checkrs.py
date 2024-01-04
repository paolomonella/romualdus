#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


import constants
from lxml import etree

def checkrs (myPropNamesInputFile):
    ''' This function parses an XML file, performs a textual search
        on the XML file for each proper name listed in file
        rs.txt, and checks that each of the occurrences of each name
        in the XML files is marked with a <rs> tag.
        If this is not the case, the script prints out the XML file name,
        the parent element including the name, and that element's text. '''
    names_tree = etree.parse(myPropNamesInputFile)
    regexpNS = 'http://exslt.org/regular-expressions'
    find = etree.XPath(
            '//text()[re:match(., "romul", "i")]/parent::*',
            namespaces={'re':regexpNS})
    ''' §§§ TO BE CONTINUED: instead of "romul", put a string variable with names
        taken from rs.txt'''

    # Doc: http://exslt.org/regexp/ e http://exslt.org/regexp/functions/test/index.html
    for r in find(names_tree):
        if r.tag != constants.tei_ns + 'rs':
            print('%s %10s' % (myPropNamesInputFile, r.tag))
            print(' '.join([t.strip() for t in r.itertext()]))


print('\n-----------------------\n\nNEW SEARCH: \n')
#for myf in ['../xml/a.xml', '../xml/g.xml']:
for myf in ['../xml/g.xml']:
    checkrs(myf)

