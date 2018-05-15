#!/usr/python3.6
# -*- coding: utf-8 -*-

import constants
from constants import ns, tei_ns, xml_ns, html_ns 

import csv
import re
from lxml import etree

def detectCommonAbbrCombinations (siglum, quiet=True):
    ''' It opens the XML file and shows abbreviations and expansions side by side.
        It will help me to decide which common abbreviation combinations to insert
        in the csv file.
        '''
    ot = []     # This will become a list of lists. Cols: 0=abbr 1=XMLexpan 2=CSVexpan 3=note
    xmlfile = '%s%s.xml' % (constants.xmlpath, siglum)
    tree = etree.parse(xmlfile)
    csvcombifile = '%s%s-combi.csv' % (constants.csvpath, siglum)   # The CSV file with the common abbreviation combinations
    with open(csvcombifile) as combifile:
        combi = list(list(rec) for rec in csv.reader(combifile, delimiter='\t')) #reads csv into a list of lists
        # Columns: 0=Grapheme  1=Alphabeme(s)    2=Notes
    for ch in tree.findall('.//t:choice', ns):  # All <choice> elements in the original XML file
        ms = siglum.upper()
        ab = ch.find('t:abbr', ns).text     # Text content of the <abbr> child of <choice>
        ex = ch.find('t:expan', ns).text    # Text content of the <expan> child of <choice>
        note = ''
        for row in combi:
            abmatch = False
            rowexpan = row[1]   # Alphabemes column of the CSV file
            
            if (re.match('<.*>', row[0]) and ab == row[0][1:-1]) or (ab == row[0]):
                # If the abbreviation combination in the CSV file (row[0]) == the abbreviation in the XML (ab).
                # In detail:
                # If row[0] (the Grapheme column of the CSV file) has < > around it (=if it is an abbrev.
                # combination applying to entire words only)
                # and ab (the abbreviation in the XML) == row[0]
                # or, simply, ab (the XML abbrev.) == row[0] (the Grapheme column of the CSV file)
                abmatch = True

            elif re.match('(\[.*\])(.)', row[0]):
                # This applies to te CSV file abbrev. combinations in the form "[aeiouy]3" (any vowel + 3)
                firstcellmatch = re.match('(\[.*\])(.)',   row[0]) 
                myGenericBase = firstcellmatch.group(1)  # group(1) is like "[aeiouy]"
                myAbbrMark = firstcellmatch.group(2)     # group(2) is like "3" (abbreviation mark). It includes 1 char only
                gmatch = re.match('.*(' + myGenericBase + ')(' + myAbbrMark + ').*', ab)
                if gmatch:
                    abmatch = True
                    rowexpan = gmatch.group(1) + row[1][-1] # In this case, the expansion in the CSV file becomes: the base
                                                            # vowel in the XML (e.g. "e") + te abbreviation mark (e.g. "3")

            if abmatch   and ex == rowexpan: # Same abbreviation combination, same expansion (in the CSV and in the XML)
                note = 'Warning: you encoded this abbrev. in the XML, but there\'s an '
                note = note + 'identical abbr/expan pair in the combi file!'  
            elif abmatch   and ex != rowexpan:
                note = rowexpan       # Same abbreviation combination, different expansion
        ot.append([ms, ab, ex, note])
    sot = sorted(ot)
    pt = [['MS', 'XMLAbbr.', 'XMLExp.', 'CombiCSVExp.']]      # This is the 'header' of the output
    for x in sot:
        if (not quiet) or (quiet and x[3].startswith('Warning')):   
            pt.append(x)    # With the 'quiet' option, print only <abbr> cases unnecessary b/c the abbr is in the combi CSV file
    if len(pt) > 2:         # Write the 'table' only if it has more rows than just the 'header'
        print('\n\nAll abbreviations encoded in the XML source of MS "%s" explicitly with <choice>/<abbr>/<expan>:' % ms)
        print('  (A) If the "CombiCSVExp" column is empty, the abbrev. is not included in the common abbreviations CSV file;')
        print('  (B) If the "CombiCSVExp" column has a string, the abbrev. is included in that CSV file,')
        print('      but in this point of the MS it has a different expansion than the "standard" expans. in the CSV file.\n')
        for p in pt:
            print(p[0].ljust(6), p[1].ljust(9), p[2].ljust(9), p[3].ljust(10))
        if not quiet:
            print('%d abbreviations in MS %s' % (len(ot), ms))

