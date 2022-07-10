#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import re

import myconst

def metatext(mySuspectElement):
    
    ''' Check if one of the values of the "class" attribute of element e is
    in the metatextlist. Return True or False.
    '''
    metasearch = False
    for mtxt in myconst.metatextlist:
        if mySuspectElement.get('class') and re.match('.*%s.*' % mtxt, mySuspectElement.get('class')):
            metasearch = True
    return metasearch

def baretextize (treeToBaretextize):
    ''' Empty all elements with "class" including "metatext", then
        Strip all markup from all elements children of <p>
        '''
    for e in treeToBaretextize.findall('.//*', ns):     # Empty...
        if metatext(e):
            e.text = ''
    for p in treeToBaretextize.findall('.//h:p', ns):   # Strip...
        etree.strip_tags(p, '*')
