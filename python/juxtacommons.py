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
        #for reg in self.tree.findall('.//t:reg[@type="j"]', ns):
        for xy in self.tree.findall('.//t:app', ns):
            print(reg.get('type'))
        '''

        for reg in self.tree.findall('.//t:reg[@type="%s"]' % (regtype), ns):
            orig = reg.getparent().find('.//t:orig', ns)

            # The following 'remove' functions should be safe b/c <orig> or <reg> never have a tail
            # (otherwise, the tail would d be removed too)
            if form == 'reg':
                #print('Orig:', orig.text, '\tReg:', reg.text) # debug
                orig.getparent().remove(orig)
            if form == 'orig':
                reg.getparent().remove(reg)

    def write (self):
        self.tree.write(self.outputXmlFile, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)

atree = msTree('a')
atree.reg_orig('numeral', form='reg') 
atree.write()

gtree = msTree('g')
gtree.reg_orig('numeral', form='reg') 
gtree.reg_orig('j', form='reg') 
gtree.write()
