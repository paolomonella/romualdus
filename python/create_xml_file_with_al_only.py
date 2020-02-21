#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module includes one big function, extracting/dividing
    the layers from the TEI XML source file and producing
    a TEI XML output file with only the Alphabetic Layer.
    See the documentation of the function below for details.
    '''

import csv
import re
from copy import deepcopy
from lxml import etree

import myconst
from myconst import ns, tei_ns, xml_ns, html_ns 
from other import metatext 
from other import baretextize 
from replace import myReplaceAll
from replace import genericBaseReplaceAll

def reduceParLayersToAlph (par, baretext=False):
    ''' This big function inputs a TEI XML paragraph encoded at two layers (GL and AL)
        and returns the same XML paragraph, but with one layer only (AL)
    '''
    # Read ToS
    toscsvfile = '%s/%s-tos.csv' % (myconst.csvpath, siglum)
    with open(toscsvfile) as atosfile:
        tos = list(list(rec) for rec in csv.reader(atosfile, delimiter='\t')) #reads csv into a list of lists
        # Columns: 0=Grapheme  1=Alphabeme(s)    2=Grapheme visualization  3=Type    4=Notes    5=Image(s)
    
    # Read Abbreviation Combinations file
    combicsvfile = '%s/%s-combi.csv' % (myconst.csvpath, siglum)
    with open(combicsvfile) as combifile:
        combi = list(list(rec) for rec in csv.reader(combifile, delimiter='\t')) #reads csv into a list of lists
        # Columns: 0=Grapheme  1=Alphabeme(s)    2=Notes
    
    #### Transformations specific to AL ####
    
    # Remove  <abbr> tags completely
    for e in alltext.findall('.//h:span[@class="abbr"]', ns):
        if e.tail and e.tail.strip() != '':
            print('Beware! Element <span class="abbr"> has text «' + e.tail +'»')
        else:
            e.getparent().remove(e) # This should be safe b/c abbr never has a tail (otherwise, e.tail would be removed too)
    
    # First, expand common abbreviation combinations applying only to independent/whole words
    for row in combi:
        if re.match('<.*>', row[0]):
            wwgraph = row[0][1:-1]  # This changes "<qd->" to "qd-"
            myReplaceAll(wwgraph, row[1], alltext, wholeWord=True)
    
    # ... then expand specific combinations such as 'q3' (this allows me to create abbr. strings such as 'gnaw'='genera':
    #       the 'aw' part also matches [aeiouy]w and could be expanded as 'am', but this does not happen b/c the specific
    #       abbreviation combination 'gnaw' is expanded before the more generic combination '[aeiouy]w'
    for row in combi:
        if not re.match('<.*>', row[0]) and not re.match('\[.*', row[0]):
            myReplaceAll(row[0], row[1], alltext)

    # ...  then expand more generic common abbreviation combinations such as '[aeiouy]0'
        if re.match('\[.*', row[0]):
            genericBaseReplaceAll(row, alltext)
    

    # ... finally, translate every grapheme (except those into 'metatext' elements) into their standard alphabetic meaning
    for row in tos:
        if row[3] in ['Alphabetic', 'Brevigraph']:
            myReplaceAll(row[0], row[1], alltext)
    
    # Capitalize <rs> words and get rid of <rs> tag (this could have been done via CSS; but it would have been less interoperable)
    for e in alltext.findall('.//h:span[@class="rs"]', ns):
        if e.text:  # If the content of <rs> starts with a text node, capitalize it
            e.text = e.text.capitalize()
        else:   # If not, get the text of <rs>'s first child and capitalize it
            rschild = e[0]
            rschild.text = rschild.text.capitalize()

    if baretext:
        baretextize(alltext)






    #### Change output elements from <body> to <div> ####

    # Change 'g_alltext' root from (XML) <body> to (HTML) <div>
    qg_alltext = etree.QName(g_alltext)
    g_alltext.tag = html_ns + 'div'
    g_alltext.set('id', 'GLdiv')    # Output: (HTML) <div id="GLdiv"> 

    # Change 'alltext' root from (XML) <body> to (HTML) <div>
    qalltext = etree.QName(alltext)
    alltext.tag = html_ns + 'div'
    alltext.set('id', 'ALdiv')    # Output: (HTML) <div id="ALdiv"> 

    return [g_alltext, alltext]


def extractParagraphs (siglum):
    # Parse the XML source tree
    xmlfile = '%s/%s.xml' % (myconst.xmlpath, siglum)
    tree = etree.parse(xmlfile)

    '''
    # Remove line breaks that seem to interfere with string substitutions (in particular, 'tail' stopped at line break)
    for x in tree.findall('.//t:*', ns):
        if x.text: x.text = x.text.replace('\n', ' ')
        if x.tail: x.tail = x.tail.replace('\n', ' ')
        '''
    
    # Identify the <body> in the XML tree 
    alltext = tree.find('.//t:body', ns)
