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
from lxml import etree

import myconst
from myconst import ns, tei_ns, xml_ns, html_ns 


def strip_ns_prefix(myTree):
    # Source: https://stackoverflow.com/questions/30232031/how-can-i-strip-namespaces-out-of-an-lxml-tree#30233635
    # Iterate through only element nodes (skip comment node, text node, etc) :
    for element in myTree.xpath('descendant-or-self::*'):
        # If element has prefix...
        if element.prefix:
            # Replace element name with its local name
            element.tag = etree.QName(element).localname
    return myTree


class myWitness:
    '''A witness.
        xmlfile is the TEI XML file with the witness transcription.
        '''

    def __init__(self, xmlfile, teiHasXmlns = False):
        self.teiHasXmlns = teiHasXmlns
        # Source of next line: https://stackoverflow.com/questions/14731633/
        # how-to-resolve-external-entities-with-xml-etree-like-lxml-etree#19400397
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        self.tree = etree.parse(xmlfile, parser=parser)
        #self.tree = etree.XML('<l><abbrev>Et</abbrev>cil i partent seulement</l>')
        #self.tree = etree.parse('../../xml/foo.xml')
        #self.outputXmlFile = '%s/%s%s' % (myconst.xmlpath, 'simplified_', xmlfile)
        self.outputXmlFile = xmlfile.replace('.xml', '_simplified.xml')
        strip_ns_prefix(self.tree)
    
    def body(self):
        ''' Find the <body> element of the XML tree of the witness '''
        if self.teiHasXmlns:
            # If <TEI> *has* @xmlns: <TEI xmlns="http://www.tei-c.org/ns/1.0">
            myBody = self.tree.find('.//t:body', ns)
        else:
            # If <TEI> does *not* have @xmlns: <TEI>
            myBody = self.tree.find('.//body')
        return myBody

    def paragraphs(self):
        ''' Create a list of <p> elements in the <body> of the witness '''
        myBody = self.body()
        if self.teiHasXmlns:
            myParagraphs = self.body().findall('.//t:p', ns)  # This is a list of lxml elements
        else:
            myParagraphs = self.body().findall('.//p')  # This is a list of lxml elements
        for p in myParagraphs:
            if p.text and p.text[-1:] == '\n':
                p.text = p.text[:-1]    # Remove the final linebreak because it breaks collateX (for some reason)
                #print(p.get('{%s}id' % ('http://www.w3.org/XML/1998/namespace')))  # debug
        return myParagraphs

    def remove_comments (self):
        ''' Remove XML comments such as <!-- comment --> '''
        commentElements = self.tree.xpath('//comment()')
        for element in commentElements:
            parent = element.getparent()
            parent.remove(element)

    def list_elements (self, onlybody=True, attributes=False):
        ''' Print to screen a set of element names in the XML file.
            It can be sued to know that markup is used in the file. '''
        els = []
        if onlybody:
            mybody = self.tree.find('.//t:body', ns)
            allelements = mybody.iter()
        else:
            allelements = self.tree.iter()
        #for element in self.tree.iter():
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
        for k in self.tree.findall('.//t:%s[@type="%s"]' % (keeptag, keeptype), myconst.ns):
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
        ER = ER + self.tree.findall('.//t:num', myconst.ns)
        for e in ER:
            if e.text is not None: e.text = e.text.upper()
            for c in e.findall('.//t:*', myconst.ns):
                if c.text is not None: c.text = c.text.upper()
                if c.tail is not None: c.tail = c.tail.upper() 

        '''
        # Old version of the code:
        for e in self.tree.findall('.//t:p[@type="ghead1"]', myconst.ns):
            for c in e.findall('.//t:*', myconst.ns):
                if c.text is not None: c.text = c.text.upper()
                if c.tail is not None: c.tail = c.tail.upper() 
        for e in self.tree.findall('.//t:p[@type="ghead2"]', myconst.ns): #In fact, this should be small-caps, but well...
            for c in e.findall('.//t:*', myconst.ns):
                if c.text is not None: c.text = c.text.upper()
                if c.tail is not None: c.tail = c.tail.upper() 
                '''



    def simplify_to_scanlike_text (self, tagslist, removepar=False):
        ''' Strip all tags included in list tagslist within paragraphs.
            If removepar='True':
                Replace <p xml:id="g163.8-163.10" decls="#ocr"> with 163.8-163.10 and
                remove also <p>s;
                if 'False', leave them.
            Finally, re-insert the "-" dashes at the end of line and remove all <lb>s?? (not implemented so far)
            All tags are assuming to belong to the TEI XML namespace.
            '''
        for p in self.tree.findall('.//t:p', ns):   # Strip markup inside <p>s
            for t in tagslist:
                '''
                # No longer necessary b/c there's a 'choose' method now for this:
                for reg in p.findall('.//t:reg', ns):   # Remove all regularizations, i.e. all <reg> elements
                    regparent = reg.getparent()
                    regparent.remove(reg)   # This is safe because <reg> never has a tail
                    '''
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
        '''Remove start and end tag; remove text; keep tail if my_with_tail=False (default)'''
        etree.strip_elements(self.tree, myconst.tei_ns + tagname, with_tail=my_with_tail)

    def write (self):
        print('The output XML file will be:', self.outputXmlFile)
        self.tree.write(self.outputXmlFile, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)
        #self.tree.write('foo.xml', encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)


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


#EDL = ['afoo', 'bfoo']
EDL = [
        #'../../xml/simplified/afoo_juxta.xml',
        #'../../xml/simplified/gfoo_juxta.xml'
        '../../xml/a.xml',
        '../../xml/g.xml'
        #'afoo', 'bfoo'
        ]

for fileInList in EDL:
    #mytree = msTree(fileInList)
    wit = myWitness(fileInList)
    wit.choose('choice', 'corr', 'typo', 'sic')
    wit.choose('choice', 'reg', 'numeral', 'orig')
    wit.choose('choice', 'reg', 'j', 'orig')
    wit.choose('choice', 'reg', 'v', 'orig')
    wit.choose('subst', 'add', 'correction', 'del')
    wit.recapitalize() 
    wit.simplify_to_scanlike_text(['rs', 'hi', 'note', 'choice', 'orig', 'reg', 'num', 'add', 'seg', 'lb', 'pb'], \
            removepar=False)
    wit.write()

    # Temporarily needed for CollateX (in order to remove @xmlns)
    #with open('../xml/simplified/%s_juxta.xml' % (fileInList), 'r') as infile:
    with open(fileInList, 'r') as infile:
        data = infile.read()
    #with open('../xml/simplified/%s_juxta.xml' % (fileInList), 'w') as outfile:
    with open(wit.outputXmlFile, 'w') as outfile:
        data = data.replace(' xmlns="http://www.tei-c.org/ns/1.0"', '')
        outfile.write(data)