#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module extracts/divides the layers from the TEI XML source file,
    thus generating files with simplified (or no) markup that can be fed
    to collation software such as Juxta or CollateX.
    It also includes other methods that help you to inspect what entities
    and elements are in the original XML file.
    See the documentation of the methods below for details.
    '''

import csv
import re
from copy import deepcopy
from collections import Counter
import operator
from lxml import etree

import myconst
from myconst import ns, tei_ns, xml_ns, html_ns 
from replace import myReplaceAll
from replace import genericBaseReplaceAll
'''
from other import metatext 
from other import baretextize 
'''



class msTree:

    def __init__ (self, siglum):
        self.siglum = siglum
        self.xmlfile = '%s/%s.xml' % (myconst.xmlpath, siglum)
        # Source of next, commented, line: https://stackoverflow.com/questions/14731633/
        # how-to-resolve-external-entities-with-xml-etree-like-lxml-etree#19400397
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        #parser = etree.XMLParser(resolve_entities=True)
        self.tree = etree.parse(self.xmlfile, parser=parser)
        self.root = self.tree.getroot()
        self.outputXmlFile = '%s%s%s.xml' % (myconst.simplifiedpath, siglum, myconst.simplifiedsuffix)

    def remove_comments (self):
        ''' Remove XML comments such as <!-- comment --> '''
        commentElements = self.tree.xpath('//comment()')
        for element in commentElements:
            if element.getparent() is not None:
                parent = element.getparent()
                parent.remove(element)
            else:
                print('The following comment is not in the root element so I can\'t delete it:\n\t', element, end='\n\n')

    def list_elements (self, onlybody=True, attributes=False):
        ''' Print a set of element names in the XML file '''
        els = []
        if onlybody:
            mybody = self.tree.find('.//t:body', ns)
            allelements = mybody.iter()
        else:
            allelements = self.tree.iter()
        for element in allelements:
            if etree.iselement:
                tag = element.tag
                #print(element.tag.split('}')[1])
                els.append( element.tag.split('}')[1] )
        elset = set(els)
        print(set(els))
        for tag in elset:
            A = {}
            print('\n\n<' + tag + '>: ')
            if onlybody:
                E = mybody.findall('.//t:%s' % (tag), ns)
            else:
                E = self.tree.findall('.//t:%s' % (tag), ns)
            for e in E:
                for attr in e.attrib:
                    val = e.get(attr)
                    if attr not in A:
                        A[attr] = [val]
                    else:
                        A[attr].append(val)
            #print(A, end='')
            for a in A:
                if len(set(A[a])) > 5:
                    print('\t' + a + '=', set(A[a][:3]), '(etc.)')
                else:
                    print('\t' + a + '=', set(A[a]))

    def list_and_count_elements (self, onlybody=True, attributes=False):
        ''' Print a set of element names in the XML file and count them'''
        els = []
        if onlybody:
            mybody = self.tree.find('.//t:body', ns)
            allelements = mybody.iter()
        else:
            allelements = self.tree.iter()
        for element in allelements:
            if etree.iselement(element):
                tag = element.tag
                try:
                    els.append( element.tag.split('}')[1] )
                except:
                    els.append( element.tag )
        elcount = Counter(els)
        sorted_elcount = sorted(elcount.items(), key=operator.itemgetter(1))
        print('\n', 'Witness:', self.siglum)
        for e in sorted_elcount:
            print(e)
            #print(sorted_elcount[0], sorted_elcount[1])


    def list_entities (self):
        for entity in self.tree.docinfo.internalDTD.iterentities():
            msg_fmt = "{entity.name!r}, {entity.content!r}, {entity.orig!r}"
            print(msg_fmt.format(entity=entity))


    def choose (self, parenttag, keeptag, keeptype, removetag):
        ''' Keep all elements with tag name 'keeptag' and remove those with name 'removetag' in structures such as
            '<choice><orig>j</orig><reg type="j">i</reg></choice>'
            or
            <choice><sic>dimicarum</sic><corr type="typo">dimicarunt</corr></choice>
            In the examples above, "parenttag" is "choice" (it may be something else, such as "app" or "subst").
            Note that the element to keep (<reg> or <corr>) always has a @type, whose value goes to argument "keeptype".
            '''
        if keeptype == '':    # If no @type value is provided when calling the method
            myElements = self.tree.findall('.//t:%s' % (keeptag), myconst.ns)
        else:               # If a @type value is provided when calling the method
            myElements = self.tree.findall('.//t:%s[@type="%s"]' % (keeptag, keeptype), myconst.ns)
        #for k in self.tree.findall('.//t:%s[@type="%s"]' % (keeptag, keeptype), myconst.ns):
        for k in myElements:
            # If parenttag is the parent and keeptag is the sibling:
            parent = k.getparent()
            if parent.tag == myconst.tei_ns + parenttag and parent.find('.//t:%s' % (removetag), myconst.ns) is not None:   
                # The following 'remove' functions should be safe b/c <orig>, <reg> and the other children of <choice>,
                # as wella as <add> / <del> children of <subst>
                # never have a tail b/c <orig> and <reg> are the only children of <choice>
                # (otherwise, the tail would be removed too)
                r = k.getparent().find('.//t:%s' % (removetag), myconst.ns)   # The element to remove
                if r.tail is not None:
                    print('Warning: element', r.tag, 'has tail text «' + r.tail + '» that is also being removed')
                r.getparent().remove(r)

    def handle_add_del (self):
        ''' Management of <add> and <del>: 
                - if <add> and <del> have no @hand,
                    this means that the addition/deletion has been made by the main hand of the MS, so I'll respect it:
                    - delete <del>
                    - keep the content of <add>
                - else (if @hand is provided), this means that the addition/deletion has been made by a later hand, so ignore them:
                    - keep the content of <del> (the later scribe's deletion is ignored)
                    - delete <add> (don't keep the later addition)
            '''
        for e in self.tree.findall('.//t:%s' % ('add'), myconst.ns): 
            if e.get('hand') is not None:   # If @hand is provided, then the addition is my a later hand: ignore it (remove <add>)
                e.getparent().remove(e)
        for e in self.tree.findall('.//t:%s' % ('del'), myconst.ns): 
            if e.get('hand') is None:       # If no @hand is provided, then the addition is by the MS's main hand: delete <del>
                e.getparent().remove(e)

    def handle_gaps (self):
        ''' Replace <gap> with text in brackets '''
        for e in self.tree.findall('.//t:%s' % ('gap'), myconst.ns): 
            gapReason = e.get('reason')
            gapQuantity = e.get('quantity')
            gapQuantityNum = int(gapQuantity)
            gapUnit = e.get('unit')
            if gapUnit == 'words' and gapQuantityNum == 1:
                gapUnit = 'word'
            e.text = '[%s_%s_%s]' % (gapQuantity, gapReason, gapUnit)


    def ecaudatum (self, monophthongize=True):
        ''' If monophthongize is True, transform <seg ana="#ae">ae</seg> to <seg ana="#ae">e</seg>.
            If it is False, it remains <seg ana="#ae">ae</seg>
            '''
        if monophthongize:
            for e in self.tree.findall('.//t:%s' % ('seg[@ana="#ae"]'), myconst.ns):
                e.text = 'e'
            for e in self.tree.findall('.//t:%s' % ('seg[@ana="#doubleae"]'), myconst.ns):
                e.text = 'ee'
                


    def recapitalize (self):
        ''' Re-capitalize words included in <rs> or in <hi>.
            Then, transform text marked as <p type="ghead1"> or "ghead2" to all uppercase,
            because it was in G(arufi) head(s) '''
        for mytagname in ['rs', 'hi']:
            for e in self.tree.findall('.//t:%s' % (mytagname), myconst.ns):
                if e.text:  # If the content of <rs>/<hi> starts with a text node, capitalize it
                    e.text = e.text.capitalize()
                else:   # If the content of <rs>/<hi> starts with an element...
                    echild = e[0]
                    if echild.tag == myconst.tei_ns + 'choice': # In case <rs><choice>etc. or <hi><choice>etc.
                        # ...capitalize text of all children of <choice>
                        for alternative in echild:
                            alternative.text = alternative.text.capitalize()
                    else:   # If first child of <rs>/<hi> is not <choice>
                        # ...get the text of <rs>/<hi>'s first child and capitalize it
                        if echild.text:
                            echild.text = echild.text.capitalize()
                        else:
                            # ... or capitalize the first child of the first child of <rs>/</hi>
                            echild[0].text = echild[0].text.capitalize()
        ER =  []    # Elements to transform in all uppercase
        ER = ER + self.tree.findall('.//t:p[@type="ghead1"]', myconst.ns)
        ER = ER + self.tree.findall('.//t:p[@type="ghead2"]', myconst.ns)
        #ER = ER + self.tree.findall('.//t:num', myconst.ns)    # Numerals are now handles in a specific function (handle_numerals)
        for e in ER:
            if e.text is not None: e.text = e.text.upper()
            for c in e.findall('.//t:*', myconst.ns):
                if c.text is not None: c.text = c.text.upper()
                if c.tail is not None: c.tail = c.tail.upper() 



    def simplify_to_scanlike_text (self, tagslist, removepar=False):
        ''' Strip all tags included in list tagslist within paragraphs.
            If removepar='True':
                Replace <p xml:id="g163.8-163.10" decls="#ocr"> with 163.8-163.10 and
                remove also <p>s;
                if 'False', leave them.
            Finally, re-insert the "-" dashes at the end of line and remove all <lb>s?? (not implemented so far)
            All tags are assumed to belong to the TEI XML namespace.
            '''
        for p in self.tree.findall('.//t:p', ns):   # Strip markup inside <p>s
            for t in tagslist:
                etree.strip_tags(p, myconst.tei_ns + t)
        if removepar:
            body = self.tree.find('.//t:body', ns)
            for p in body.findall('.//t:p', ns):   # Replace <p xml:id="g163.8-163.10" decls="#ocr"> with 163.8-163.10
                xmlid = p.get(myconst.xml_ns + 'id')
                try:
                    p.text = ''.join([xmlid, p.text])
                except:
                    print(p.text)
            etree.strip_tags(body, myconst.tei_ns + 'p')

    def my_strip_tags (self, tagname):
        '''Remove start and end tag but keep text and tail'''
        etree.strip_tags(self.tree, tagname)

    def my_strip_elements (self, tagname, my_with_tail=False):
        '''Remove start and end tag; remove textual content; keep tail if my_with_tail=False (default)'''
        etree.strip_elements(self.tree, myconst.tei_ns + tagname, with_tail=my_with_tail)

    def handle_numerals (self):
        '''Replace 'u' with 'v' in the textual content of <num> elements, and make them all uppercase'''
        for num in self.tree.findall('.//t:num', ns):

            # Replace 'u' with 'v'
            if num.text:
                num.text = num.text.replace('u', 'v')   # Direct textual content of <num>
            for x in num.findall('.//t:*', ns):     # Children elements of <num>
                if x.text:
                    x.text = x.text.replace('u', 'v')
                if x.tail:
                    x.tail = x.tail.replace('u', 'v')

            # Make uppercase if @type is not 'words'
            if num.get('type') != 'words':
                if num.text is not None: num.text = num.text.upper()
                for c in num.findall('.//t:*', myconst.ns):
                    if c.text is not None: c.text = c.text.upper()
                    if c.tail is not None: c.tail = c.tail.upper() 


    def reduce_layers_to_alph_only (self):
        ''' This big function inputs a TEI XML paragraph encoded at two layers (GL and AL)
            and returns the same XML paragraph, but with one layer only (AL).
            Argument 'self' is a LMXL XML Element object <p>
        '''

        # Read ToS
        if self.siglum == 'a1':
            mySiglum = 'a'
        else:
            mySiglum = self.siglum
        toscsvfile = '%s/%s-tos.csv' % (myconst.csvpath, mySiglum)
        with open(toscsvfile) as atosfile:
            tos = list(list(rec) for rec in csv.reader(atosfile, delimiter='\t')) #reads csv into a list of lists
            # Columns: 0=Grapheme  1=Alphabeme(s)    2=Grapheme visualization  3=Type    4=Notes    5=Image(s)
        
        # Read Abbreviation Combinations file
        combicsvfile = '%s/%s-combi.csv' % (myconst.csvpath, mySiglum)
        with open(combicsvfile) as combifile:
            combi = list(list(rec) for rec in csv.reader(combifile, delimiter='\t')) #reads csv into a list of lists
            # Columns: 0=Grapheme  1=Alphabeme(s)    2=Notes
        
        for par in self.tree.findall('.//t:p[@decls="#algl"]', ns):

            #print(par.tag, par.get('decls'), par.get(myconst.xml_ns + 'id') ) # debug
            for x in par.findall('.//t:*', ns):
                # Remove line breaks that seem to interfere with string substitutions (in particular, 'tail' stopped at line break)
                if x.text:
                    x.text = x.text.replace('\n', ' ')
                if x.tail:
                    x.tail = x.tail.replace('\n', ' ')
            
            # Remove  <abbr> tags entirely (including their textual content, but not their tail)
            etree.strip_elements(par, myconst.tei_ns + 'abbr', with_tail=False)

            # First, expand common abbreviation combinations applying only to independent/whole words
            for row in combi:
                if re.match('<.*>', row[0]):
                    wwgraph = row[0][1:-1]  # This changes "<qd->" to "qd-"
                    myReplaceAll(wwgraph, row[1], par, wholeWord=True) # I replaced alltext with par
            
            # ... then expand specific combinations such as 'q3' (this allows me to create abbr. strings such as 'gnaw'='genera':
            #       the 'aw' part also matches [aeiouy]w and could be expanded as 'am', but this does not happen b/c the specific
            #       abbreviation combination 'gnaw' is expanded before the more generic combination '[aeiouy]w'
            for row in combi:
                if not re.match('<.*>', row[0]) and not re.match('\[.*', row[0]):
                    myReplaceAll(row[0], row[1], par)   # I replaced alltext with par

            # ...  then expand more generic common abbreviation combinations such as '[aeiouy]0'
                if re.match('\[.*', row[0]):
                    genericBaseReplaceAll(row, par) # I replaced alltext with par
            
            # ... eventually, translate every grapheme into their standard alphabetic meaning
            for row in tos:
                if row[3] in ['Alphabetic', 'Brevigraph']:
                    myReplaceAll(row[0], row[1], par)   # I replaced alltext with par

    def write (self):
        self.tree.write(self.outputXmlFile, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)





EDL = ['a1', 'a2', 'o', 'g', 'bonetti']
for edition in EDL:
    print('juxtacommons.py: I\'m working on %s' % (edition) )
    mytree = msTree(edition)
    if edition == 'a1':
        mytree.reduce_layers_to_alph_only()
    for tag_to_strip in ['interp', 'abbr', 'surplus', 'note']:
        mytree.my_strip_elements(tag_to_strip) 
    mytree.handle_numerals()
    mytree.handle_gaps()
    mytree.handle_add_del() # only needed for MS A
    mytree.choose('choice', 'sic', '', 'corr')  # check if this works §
    mytree.choose('choice', 'reg', 'numeral', 'orig')
    mytree.choose('choice', 'reg', 'j', 'orig')
    mytree.choose('choice', 'reg', 'v', 'orig')
    mytree.ecaudatum (monophthongize=True)  # only needed for MS A; with False, it stays 'ae'; with True, it becomes 'e'
    mytree.remove_comments()
    mytree.recapitalize() 
    mytree.simplify_to_scanlike_text(
            ['rs', 'hi', 'w', 'choice', 'orig', 'reg', 'num', 'subst', 'add', 'del', 'expan', 'sic',
                'seg', 'lb', 'pb', 'quote', 'title', 'said', 'soCalled', 'surplus', 'supplied', 'gap'], \
            removepar=False)
    mytree.write()
    # Temporarily needed for CollateX (remove @xmlns)
    with open('%s%s%s.xml' % (myconst.simplifiedpath, edition, myconst.simplifiedsuffix), 'r') as infile:
        data = infile.read()
    with open('%s%s%s.xml' % (myconst.simplifiedpath, edition, myconst.simplifiedsuffix), 'w') as outfile:
        data = data.replace(' xmlns="http://www.tei-c.org/ns/1.0"', '')
        outfile.write(data)


#for mySiglum in ['a1_juxta', 'a2_juxta', 'o_juxta', 'g_juxta', 'bonetti_juxta']:
for mySiglum in ['a1', 'a2', 'o', 'g', 'bonetti']:
    edition = mySiglum + myconst.simplifiedsuffix
    mytree = msTree(edition)
    mytree.list_and_count_elements()







'''

atree = msTree('a')
atree.reg_orig('numeral', form='reg') 
atree.write()

gtree = msTree('g')
gtree.reg_orig('numeral', form='reg') 
gtree.reg_orig('j', form='reg') 
gtree.recapitalize() 
gtree.write()

btree = msTree('bonetti')
btree.recapitalize() 
btree.simplify_to_scanlike_text(['rs', 'hi', 'note', 'choice', 'orig', 'num'], removepar=True)
btree.write()

atree = msTree('g')
#atree.list_elements()
atree.list_entities()

for edition in ['a', 'g', 'bonetti']:
    mytree = msTree(edition)
    mytree.choose('choice', 'corr', 'typo', 'sic')
    mytree.choose('choice', 'reg', 'numeral', 'orig')
    mytree.choose('choice', 'reg', 'j', 'orig')
    mytree.choose('choice', 'reg', 'v', 'orig')
    mytree.choose('subst', 'add', 'correction', 'del')
    mytree.my_strip_elements('del')
    mytree.recapitalize() 
    mytree.simplify_to_scanlike_text(['rs', 'hi', 'note', 'choice', 'orig', 'num', 'add', 'seg', 'lb'], removepar=False)
    mytree.write()
'''
