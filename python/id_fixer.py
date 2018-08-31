#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import myconst
from lxml import etree
import time
import os

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


spread_ids ('a', 'b')
spread_ids ('a', 'c')
