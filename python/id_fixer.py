#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import myconst
from lxml import etree
import time
import os

def compare_ids (wit1, wit2):
    ''' This function takes xml:id's from XML file "wit1" and
        compares them those of file "wit2"
        '''
    D = {}
    for wit in [wit1, wit2]:
        tree = etree.parse('../xml/%s.xml' % wit)
        body = tree.find('.//t:body', myconst.ns)
        pp = body.findall('.//t:p', myconst.ns)
        D[wit] = [p.get(myconst.xml_ns + 'id') for p in pp]
    for xmlid1 in D[wit1]:
        index = D[wit1].index(xmlid1)
        try:
            xmlid2 = D[wit2][index]
            if xmlid1 != xmlid2:
                print('%s: %15s %10s: %15s' % (wit1, xmlid1, wit2, xmlid2) )
                break
        except IndexError:
            print('List index %d out of range. Witness "%s.xml" has xml:id %s' % (index, wit1, xmlid1)  )
            break
    

def spread_ids (get_p_ids_from, append_p_ids_to):
    ''' This function takes xml:id's from XML file "get_p_ids_from"
        checks which <p>'s are present in XML file "get_p_ids_from" but
        missing from XML files listed in "append_p_ids_to", then
        appends new <p>'s to those XML files.
        It creates backup files in the same 'xml' directory as the
        original XML files.
        '''
    #get_p_ids_from = 'g'
    #append_p_ids_to = ['a', 'b', 'c']
    
    input_tree = etree.parse('../xml/%s.xml' % get_p_ids_from)
    input_body = input_tree.find('.//t:body', myconst.ns)
    pp = input_body.findall('.//t:p', myconst.ns)
    ids = [p.get(myconst.xml_ns + 'id') for p in pp]
    
    for ms in append_p_ids_to:
        datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
        input_filename = '.'.join([ms, 'xml'])
        backup_filename = '_'.join([datetime, ms, 'id-spreading-backup.xml'])
        os.system('cp ../xml/%s ../xml/%s' % (input_filename, backup_filename)) # Create backup of old file
        output_tree = etree.parse('../xml/%s.xml' % ms)
        output_body = output_tree.find('.//t:body', myconst.ns)
        pp = output_body.findall('.//t:p', myconst.ns)
        outids = [p.get(myconst.xml_ns + 'id') for p in pp]
        for ii in ids:
            if ii.strip() not in outids:
                newp = etree.Element(myconst.tei_ns + 'p')
                newp.set(myconst.xml_ns + 'id', ii)
                output_body.append(newp)
                #print('Nel MS %s NON c\'era %s' % (ms, ii))
        output_tree.write('../xml/%s.xml' % (ms), encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)


#spread_ids ('a', 'b')
#spread_ids ('a', 'c')
#compare_ids ('a-tagliato', 'g')    # tutto OK
compare_ids ('a-bonetti', 'bonetti')
