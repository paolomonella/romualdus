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

import constants
from constants import ns, tei_ns, xml_ns, html_ns 
'''
from other import metatext 
from other import baretextize 
from replace import myReplaceAll
from replace import genericBaseReplaceAll
'''

class msTree:

    def __init__ (self, siglum):
        self.siglum = siglum
        self.xmlfile = '%s/%s.xml' % (constants.xmlpath, siglum)
        # Source of next, commented, line: https://stackoverflow.com/questions/14731633/
        # how-to-resolve-external-entities-with-xml-etree-like-lxml-etree#19400397
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        #parser = etree.XMLParser(resolve_entities=True)
        self.tree = etree.parse(self.xmlfile, parser=parser)
        self.outputXmlFile = '%s/%s%s.xml' % (constants.xmlpath, siglum, '_juxta')

    def remove_comments (self):
        ''' Remove XML comments such as <!-- comment --> '''
        els = []
        commentElements = self.tree.xpath('//comment()')
        for element in commentElements:
            parent = element.getparent()
            parent.remove(element)

    def list_elements (self):
        ''' Print a set of element names in the XML file '''
        for element in self.tree.iter():
            if etree.iselement:
                tag = element.tag
                #print(element.tag.split('}')[1])
                els.append( element.tag.split('}')[1] )
        print(set(els))

    def list_entities (self):
        for entity in doc.docinfo.internalDTD.iterentities():
            msg_fmt = "{entity.name!r}, {entity.content!r}, {entity.orig!r}"
            print(msg_fmt.format(entity=entity))

    def reg_orig (self, regtype, form = 'reg'):
        ''' Remove all <reg> or (default) all <orig> in structures such as
            '<choice><orig>j</orig><reg type="j">i</reg></choice>':
                If form = 'reg',  remove all 'orig' (default);
                if form = 'orig', remove all 'reg'.
            Argument 'regtype' should be
                'numeral' for <reg type="numeral">,
                'j' for <reg type="j"> etc.
            '''
        '''
        #for reg in self.tree.findall('.//t:reg[@type="j"]', constants.ns):
        for xy in self.tree.findall('.//t:app', constants.ns):
            print(reg.get('type'))
        '''

        for reg in self.tree.findall('.//t:reg[@type="%s"]' % (regtype), constants.ns):
            orig = reg.getparent().find('.//t:orig', constants.ns)

            # The following 'remove' functions should be safe b/c <orig> or <reg> never have a tail
            # b/c <orig> and <reg> are the only children of <choice>
            # (otherwise, the tail would be removed too)
            if form == 'reg':
                orig.getparent().remove(orig)
            if form == 'orig':
                reg.getparent().remove(reg)

    def recapitalize (self):
        ''' Re-capitalize words included in <rs> or in <hi> '''
        for mytagname in ['rs', 'hi']:
            for e in self.tree.findall('.//t:%s' % (mytagname), constants.ns):
                if e.text:  # If the content of <rs>/<hi> starts with a text node, capitalize it
                    e.text = e.text.capitalize()
                else:   # If the content of <rs>/<hi> starts with an element...
                    echild = e[0]
                    if echild.tag == constants.tei_ns + 'choice': # In case <rs><choice>etc. or <hi><choice>etc.
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
                etree.strip_tags(p, constants.tei_ns + t)
        if removepar:
            body = self.tree.find('.//t:body', ns)
            for p in body.findall('.//t:p', ns):   # Replace <p xml:id="g163.8-163.10" decls="#ocr"> with 163.8-163.10
                xmlid = p.get(constants.xml_ns + 'id')
                try:
                    p.text = ''.join([xmlid, p.text])
                except:
                    print(p.text)
                #etree.strip_tags(p, '*')
            etree.strip_tags(body, constants.tei_ns + 'p')

    def write (self):
        self.tree.write(self.outputXmlFile, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)

'''
atree = msTree('a')
atree.reg_orig('numeral', form='reg') 
atree.write()

gtree = msTree('g')
gtree.reg_orig('numeral', form='reg') 
gtree.reg_orig('j', form='reg') 
gtree.recapitalize() 
gtree.write()

gtree = msTree('B')
gtree.reg_orig('numeral', form='reg') 
gtree.reg_orig('j', form='reg') 
gtree.recapitalize() 
gtree.write()
'''

btree = msTree('bonetti')
btree.recapitalize() 
btree.simplify_to_scanlike_text(['rs', 'hi', 'note'], removepar=True)
btree.write()
