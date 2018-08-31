#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module includes one big function, extracting/dividing
    the layers from the TEI XML source file. See the documentation
    of the function below for details.
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

def extractLayers (siglum, baretext=False):
    ''' This big function inputs the siglum of the manuscript ("a", "b" etc.) and returns a list of two lxml HTML elements:
        g_alltext is (HTML) <div id="GLdiv"> (containing the GL HTML output as a number of HTML <p> elements)
        a_alltext is (HTML) <div id="ALdiv"> (containing the AL HTML output as a number of HTML <p> elements)
        If baretext = True, the only tags in g_alltext and a_alltext will be <div> (root) and a series of
        <p> children elements, and all other XML tags will be stripped out.
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
    
    # Parse the XML source tree
    xmlfile = '%s/%s.xml' % (myconst.xmlpath, siglum)
    tree = etree.parse(xmlfile)

    for x in tree.findall('.//t:*', ns):
        # Remove line breaks that seem to interfere with string substitutions (in particular, 'tail' stopped at line break)
        if x.text: x.text = x.text.replace('\n', ' ')
        if x.tail: x.tail = x.tail.replace('\n', ' ')
        # Change all tags from TEI namespace to HTML namespace
        q = etree.QName(x)
        x.tag = '{' + ns['h'] + '}' + q.localname
    
    # Identify the <body> in the XML tree 
    alltext = tree.find('.//h:body', ns)




    #### Transformations shared by GL and AL ####
    
    # Transform <pb> and <cb>
    pcdict = {'pb': 'Charta ', 'cb': 'Column '}
    for tag in ['pb', 'cb']:
        for x in alltext.findall('.//h:' + tag, ns):
            pbcbn = x.attrib.pop('n') # Removes the attribute "n" and stores its content to variable pbcbn
            x.text = '[' + pcdict[tag] + pbcbn + ']'
            x.set('title', pbcbn)
    
    # Transform some TEI tags to HTML <span class="xml-tag-name"> or <span class="meta xml-tag-name">
    for tag in ['rs', 'choice', 'abbr', 'expan', 'pb', 'cb', 'note', 'title', 'orig', 'reg', 'sic', 'corr', 'said', 'del']:
        for x in alltext.findall('.//h:' + tag, ns):
            l = etree.QName(x).localname
            if tag in myconst.metatextlist:     # Add class "metatext" to those tags that don't belong to the medieval text
                x.set('class', 'metatext %s' % l)
            else:
                x.set('class', l)
            x.tag = '{' + ns['h'] + '}' + 'span'

    for e in alltext.findall('.//h:p', ns):
    
        # Transform <p xml:id="abc"> to <p id="abc"> (CSS doesn't like xml:id) 
        eid = xml_ns + 'id'
        parId = e.attrib.pop(eid)   # Removes the attribute "xml:id" and stores its content to variable parId
        e.set('id', parId)
    
        # Show Garufi page/lines at the beginning of each paragraph
        garufiString = '[Garufi %s] ' % e.get('id')[1:].replace('.', ',').replace('-', ' - ') # Remove initial 'g'
        garufiSpan = etree.Element('span')
        garufiSpan.set('class', 'metatext garufi')
        if len(e) == 0 and not e.text:    # If the paragraph was completely empty (no text, no child elements)
            garufiString = garufiString.replace(']', ' missing in the manuscript]')
        garufiSpan.text = garufiString
        e.insert(0, garufiSpan)
        if e.text:  # If the paragraph is not empty and starts with e.text, move e.text to the end of garufiSpan
            garufiSpan.tail = e.text 
            e.text = ''
    
    # Add a line break after full stops (for better alignment in AL/GL two-columns view) (man, that was hard to code!)
    for e in alltext.findall('.//*'):
        #print(p.xpath('normalize-space()'))     # Useful for debugging
        if e.text and '.' in e.text and not metatext(e):
            ch = e.text.split('.')  # ch = chunks
            l = len(ch)
            e.text = ch[0] + '.'
            for x in range(1, l):
                br1 = etree.SubElement(e, 'br')
                br1.tail = ch[x]
        if e.tail and '.' in e.tail and not metatext(e):
            ch = e.tail.split('.')  # ch = chunks
            l = len(ch)
            eparent = e.getparent()
            ei = eparent.index(e)
            e.tail = ch[0] + '.'
            for r in range (l):
                s = r + 1
                if s < len(ch):
                    br = etree.Element('br')
                    eparent.insert(ei+s, br)
                    br.tail = ch[s]
                    if s < l-1:
                        br.tail = br.tail + '.'




    #### Transformations specific to GL ####
    
    g_alltext = deepcopy(alltext)    # This is the XML <body>, that will become <div xml:id="GLdiv"> in HTML
    
    # At GL, get rid of AL (modern) punctuation
    alpString = ''.join(myconst.alp)
    translator = str.maketrans('', '', alpString)
    for e in g_alltext.findall('.//*'):
        if e.text and not metatext(e):
            e.text = e.text.translate(translator)
        if e.tail:
            e.tail = e.tail.translate(translator)
        # Alternative: change "," to "<span class="punct">,</span>" (but how to do it with lxml? google it)

    if not baretext:
        # When the user hovers an abbreviation, a black recttangle will show up with its expansion
        for e in g_alltext.findall('.//h:span[@class="abbr"]', ns):
            he = e.getparent().find('h:span[@class="expan"]', ns) # Hover Expansion
            e.set('title', he.text)

    # Remove  <expan> tags completely
    for e in g_alltext.findall('.//h:span[@class="expan"]', ns):
        if e.tail and e.tail.strip() != '':
            print('Beware! Element <span class="expan> has text «' + e.tail +'»')
        else:
            e.getparent().remove(e) # This should be safe b/c abbr never has a tail (otherwise, e.tail would be removed too)

    if baretext:
        baretextize(g_alltext)

    # Substitute grapheme encoding characters with their visualization characters
    for row in tos:
        myReplaceAll(row[0], row[2], g_alltext)
    




    #### Transformations specific to AL ####
    
    a_alltext = deepcopy(alltext)    # This is the XML <body>, that will become <div xml:id="ALdiv"> in HTML

    # Remove  <abbr> tags completely
    for e in a_alltext.findall('.//h:span[@class="abbr"]', ns):
        if e.tail and e.tail.strip() != '':
            print('Beware! Element <span class="abbr"> has text «' + e.tail +'»')
        else:
            e.getparent().remove(e) # This should be safe b/c abbr never has a tail (otherwise, e.tail would be removed too)
    
    # First, expand common abbreviation combinations applying only to independent/whole words
    for row in combi:
        if re.match('<.*>', row[0]):
            wwgraph = row[0][1:-1]  # This changes "<qd->" to "qd-"
            myReplaceAll(wwgraph, row[1], a_alltext, wholeWord=True)
    
    # ... then expand specific combinations such as 'q3' (this allows me to create abbr. strings such as 'gnaw'='genera':
    #       the 'aw' part also matches [aeiouy]w and could be expanded as 'am', but this does not happen b/c the specific
    #       abbreviation combination 'gnaw' is expanded before the more generic combination '[aeiouy]w'
    for row in combi:
        if not re.match('<.*>', row[0]) and not re.match('\[.*', row[0]):
            myReplaceAll(row[0], row[1], a_alltext)

    # ...  then expand more generic common abbreviation combinations such as '[aeiouy]0'
        if re.match('\[.*', row[0]):
            genericBaseReplaceAll(row, a_alltext)
    

    # ... finally, translate every grapheme (except those into 'metatext' elements) into their standard alphabetic meaning
    for row in tos:
        if row[3] in ['Alphabetic', 'Brevigraph']:
            myReplaceAll(row[0], row[1], a_alltext)
    
    # Capitalize <rs> words and get rid of <rs> tag (this could have been done via CSS; but it would have been less interoperable)
    for e in a_alltext.findall('.//h:span[@class="rs"]', ns):
        if e.text:  # If the content of <rs> starts with a text node, capitalize it
            e.text = e.text.capitalize()
        else:   # If not, get the text of <rs>'s first child and capitalize it
            rschild = e[0]
            rschild.text = rschild.text.capitalize()

    if baretext:
        baretextize(a_alltext)






    #### Change output elements from <body> to <div> ####

    # Change 'g_alltext' root from (XML) <body> to (HTML) <div>
    qg_alltext = etree.QName(g_alltext)
    g_alltext.tag = html_ns + 'div'
    g_alltext.set('id', 'GLdiv')    # Output: (HTML) <div id="GLdiv"> 

    # Change 'a_alltext' root from (XML) <body> to (HTML) <div>
    qa_alltext = etree.QName(a_alltext)
    a_alltext.tag = html_ns + 'div'
    a_alltext.set('id', 'ALdiv')    # Output: (HTML) <div id="ALdiv"> 

    return [g_alltext, a_alltext]
