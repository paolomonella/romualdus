#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import myconst
from lxml import etree
import time
import os


def compare_two_id_lists (wit1, wit2, D, orderMatters):
    ''' The first two arguments are the sigla of the two witnesses.
         What matters is the order in which the two args are given.
         Argument D is the dictionary created in function compare_ids'''
    for xmlid1 in D[wit1]:
        index = D[wit1].index(xmlid1)
        try:
            xmlid2 = D[wit2][index]
            if xmlid1 != xmlid2:
                if orderMatters:
                    print('%s → %20s: %15s %10s: %15s' % ('Previous IDs', wit1, previousId1, wit2, previousId2) )
                print('%s → %11s: %15s %10s: %15s' % ('Non-corresponding IDs', wit1, xmlid1, wit2, xmlid2) )
                break
        except IndexError:
            print('List index %d out of range. Witness %s.xml has xml:id %s, while witness %s doesn\'t' % (index, wit1, xmlid1, wit2))
            break
        if orderMatters:
            previousId1, previousId2 = xmlid1, xmlid2

def compare_ids (witOne, witTwo, orderMatters = True):
    ''' This function takes xml:id's from XML file "witOne" and
        compares them those of file "witTwo"
        '''
    myDict = {}
    for wit in [witOne, witTwo]:
        tree = etree.parse('../xml/%s.xml' % wit)
        body = tree.find('.//t:body', myconst.ns)
        pp = body.findall('.//t:p', myconst.ns)
        myDict[wit] = [p.get(myconst.xml_ns + 'id') for p in pp]
        if not orderMatters:
            myDict[wit] = sorted(myDict[wit])
    print('%s → %14s: %15s %10s: %15s' % ('Number of xml:id\'s', witOne, len(myDict[witOne]), witTwo, len(myDict[witTwo])) )
    compare_two_id_lists(witOne, witTwo, myDict, orderMatters)
    compare_two_id_lists(witTwo, witOne, myDict, orderMatters)


def spread_ids (get_p_ids_from, append_p_ids_to):
    ''' This function takes xml:id's from XML file "get_p_ids_from"
        checks which <p>'s are present in XML file "get_p_ids_from" but
        missing from XML files listed in "append_p_ids_to", then
        appends new <p>'s to those XML files.
        It creates backup files in the same 'xml' directory as the
        original XML files.
        '''
    #get_p_ids_from = 'g'
    #append_p_ids_to = ['a-1and2unified', 'b', 'c']
    
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


spread_ids ('a-1and2unified', 'b')
spread_ids ('a-1and2unified', 'c')
#compare_ids ('a-1and2unified', 'geb', orderMatters = False) # Quindi g + bonetti corrisponde ad a
#compare_ids ('a1', 'g', orderMatters = True)   # OK prima-parte-a / g (non ci sono trasposizioni)
#compare_ids ('a2', 'bonetti', orderMatters = False) # OK seconda-parte-a / bonetti (ci sono trasposizioni, però)
#compare_ids ('o', 'bonetti', orderMatters = True) # OK seconda-parte-a / bonetti (ci sono trasposizioni, però)
