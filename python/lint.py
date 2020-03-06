#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import csv
from copy import deepcopy
from lxml import etree

import myconst
from myconst import ns, tei_ns


def tosLint(lintSiglum):
    ''' This checks if the characters used for GL and AL in the manuscript XML
        are listed in the relevant table of signs file for the relevant layer.
        For the GL, all elements except <expan> are checked.
        For the AL, only <expan> elements will be checked, since the rest of
        the AL will be automatically generated starting from the 'Abbreviation
        combinations' csv, and I assume that the latter only includes legal
        Alphabemes chars.
        '''

    # Import table of signs
    # csvpath might look like "../csv/":


    if lintSiglum in ['a1', 'a2', 'a-1and2unified']:
        mySiglum = 'a'
    else:
        mySiglum = lintSiglum
    csvfile = '%s%s-tos.csv' % (myconst.csvpath, mySiglum)

    with open(csvfile) as mtf:  # My Tables of signs File
        # Reads csv into a list of lists:
        myTos = list(list(rec) for rec in csv.reader(mtf, delimiter='\t'))

    # Check
    glegal = deepcopy(myconst.legal)    # glegal: list of chars legal at GL
    alegal = deepcopy(myconst.legal)    # alegal: list of chars legal at AL
    for row in myTos:
        if myTos.index(row) > 0:
            glegal.append(row[0])
            if True and row[1] != '':
                alegal.append(row[1])
    # It's possible that two graphemes (e.g. 'e' and 'æ') have
    # the same alphabetical meaning (e.g.: 'e'):
    # so the same char in column 'Alphabeme(s)' might be repeated.
    # This is to avoid duplicates.
    alegalset = set(alegal)
    # gfz = GL Free Zone (elements that won't be checked):
    gfz = [tei_ns + x for x in ['interp', 'expan', 'note']]
    # xmlpath might look like "../xml/":
    xmlfile = '%s%s.xml' % (myconst.xmlpath, lintSiglum)
    lintTree = etree.parse(xmlfile)
    lintBody = lintTree.find('.//t:text', ns)
    for e in lintBody.findall('.//t:*', ns):
        mytl = []
        if e.text:
            mytl.append(e.text)
        if e.tail:
            mytl.append(e.tail)
        for myt in mytl:
            if e.tag == tei_ns + 'expan':
                for c in myt:  # Check keyed-in AL (i.e. <expan> elements)
                    if c not in alegalset:
                        print('[RomualdusLint] Illegal Unicode character \
                              «%s» at Alphabetic Layer in MS %s, \
                              string «%s»' %
                              (c, lintSiglum.upper(), myt))
            if e.tag not in gfz:
                for c in myt:           # Check GL
                    # The following 'if 'is necessary because of cases such as
                    # <note><hi>i</hi> was <rs>joyful</rs></note>,
                    # in which 'was' is not skipped by the lint b/c it's
                    # <hi>.tail and 'joyful' is not b/c it's <rs>.text
                    if c not in glegal and e.getparent().tag not in gfz \
                       and e.getparent().getparent().tag not in gfz:
                        print('[RomualdusLint] Illegal Unicode character «%s» \
                              at Graphematic Layer in MS %s, string «%s»' %
                              (c, lintSiglum.upper(), myt))
