#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


''' Examples on how to run the functions in this module: 

    listnames('../xml/g.xml', constants.tei_ns) 
    updatenamesfile('../xml/a.xml')
    print('\n-----------------------\n\nNEW SEARCH: \n')
    for myf in ['../xml/a.xml', '../xml/g.xml']:
    for myf in ['../xml/a.xml']:
        checkrs(myf)
        '''

import os
import re
import constants
from lxml import etree
import time

def nameset (properNamesInputXmlFile, mytag='rs', addrstxt=True):
    ''' Parse an xml file and return a set (not list) of names marked
        with mytag (typipcally <rs> or <hi>) in that file. All names in the set are in lowercase.
        If addrstxt=True, add to that set the proper names in file rs.txt
        '''
    names_tree = etree.parse(properNamesInputXmlFile)
    #rss = names_tree.findall('.//t:rs', constants.ns)  # Old version
    mynames = names_tree.findall('.//t:%s' % (mytag), constants.ns)
    namelist = [rs.text.lower() for rs in mynames if len(list(rs)) == 0 ]   # The 'if' excludes <rs>'s with element children
    for m in mynames:   # This takes care of <rs>'s with element children
        if len(list(m)) > 0:
            if m.find('.//t:orig', constants.ns) is not None:   # Remove 'orig' (i.e. only leave 'reg': 'jovem' becomes 'iouem')
                orig = m.find('.//t:orig', constants.ns)
                orig.getparent().remove(orig)
            namelist.append(''.join(m.itertext()).replace('\n', ''))
    if addrstxt:
        with open ('rs.txt', 'r') as rstxt: # Add the names stored in file 'rs.txt'
            for l in rstxt:
                namelist.append(l.strip().lower())
    return set(namelist)

def write_to_output_file (myiterable):
    datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
    with open ('%s_output.txt' % (datetime), 'w') as outfile:
        for x in myiterable:
            print(x, file=outfile)


def listnames (properNamesInputXmlFile, myNamespace):
    ''' This script parses the ../xml/temp_g.xml file and lists
        the textual content of all its <rs> elements.
        All names in the list are in lowercase.
        '''
    names_tree = etree.parse(properNamesInputXmlFile)
    rss = names_tree.findall('.//%srs' % myNamespace)
    for rs in rss:
        print(rs.text, end=',')
    print('\n---\n')

def sorted_nicely(l): 
    ''' Sort the given iterable in the way that humans expect.''' 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def updatenamesfile (updateProperNamesInputXmlFile):
    ''' Update the rs.txt file, merging names in <rs> elements in
        file updateProperNamesInputXmlFile (e.g. a.xml) and names
        in the original rs.txt file. Backup the original file.
        ISSUE: This fills the rs.txt file with 'names' that are not
        necessarily such (like 'urbem' etc.).
        '''

    # Get updated set of names from XML file and rs.txt
    newNamesSet = nameset(updateProperNamesInputXmlFile)

    # Backup old rs.txt
    datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
    backup_filename = '_'.join([datetime, 'rs_backup.txt'])
    os.system('cp rs.txt %s' % (backup_filename))

    with open ('non_rs.txt', 'r') as nonrsfile:
        nn = [n.strip() for n in nonrsfile] # This is a list of tokens that shouldn't be systematically marked with <rs>

    with open ('rs.txt', 'w') as f:
        for n in sorted_nicely(newNamesSet):
            if n.strip() not in nn:
                print(n.strip(), file=f)

def checkrs_old (myInputXmlFile, myProperNamesFile):
    ''' Update file rs.txt based on the <rs>'s in the XML file 'myInputXmlFile'.
        Then parse 'myInputXmlFile'
        perform a textual search on the XML file for each proper name
        listed in file myProperNamesFile, and check that each of the occurrences of each name
        in the XML files is marked with a <rs> tag.
        If this is not the case, then print out the XML file name,
        the parent element that includes the name, and that element's text. '''
    updatenamesfile(myInputXmlFile)
    names_tree = etree.parse(myInputXmlFile)
    regexpNS = 'http://exslt.org/regular-expressions'
    with open (myProperNamesFile, 'r') as rsfile:
        for l in rsfile:
            myname = l.strip().lower()
            find = etree.XPath('//text()[re:match(., "\W%s\W", "i")]/parent::*' % (myname), namespaces={'re':regexpNS})
            # Doc: http://exslt.org/regexp/ e http://exslt.org/regexp/functions/test/index.html
            for r in find(names_tree):
                if r.tag != constants.tei_ns + 'rs':    # If the proper name is not marked with <rs>
                    print('%10s %s %10s %s %10s %s' % ('File:', myInputXmlFile, 'Name:', myname, 'Tag:', r.tag))

def checkrs (myInputXmlFile, setonly=True):
    ''' Parse 'myInputXmlFile' and get a set of names marked with <rs>. Then
        perform a textual search on the XML file for each proper name
        listed in file myProperNamesFile, and check that each of the occurrences of each name
        in the XML files is marked with a <rs> tag.
        If this is not the case, then print out the XML file name,
        the parent element that includes the name, and that element's text.
        If setonly=True, don't show each occurrence of the unmarked word, but a set in which
        each word only occurs once.
        '''
    rsset = nameset(myInputXmlFile, mytag='rs', addrstxt=False)
    names_tree = etree.parse(myInputXmlFile)
    mybody = names_tree.find('.//t:body', constants.ns)
    regexpNS = 'http://exslt.org/regular-expressions'
    if not setonly:
        print('\n---\n\nNames marked with <rs> at some point of the text, but not marked in other points:')
    unmarked = []
    for myname in rsset:
        #myname = l.strip().lower()
        find = etree.XPath('//text()[re:match(., "\W%s\W", "i")]/parent::*' % (myname), namespaces={'re':regexpNS})
        # Doc: http://exslt.org/regexp/ e http://exslt.org/regexp/functions/test/index.html
        #for r in find(names_tree):
        for r in find(mybody):
            if r.tag != constants.tei_ns + 'rs':    # If the proper name is not marked with <rs>
                if setonly:
                    unmarked.append(myname)
                else:
                    simpletag = r.tag.split('}')[1]
                    print('%10s %s %10s %s %10s %s' % ('File:', myInputXmlFile, 'Name:', myname, 'Parent tag:', simpletag))
    if setonly:
        print(set(unmarked))

def checkrsandhi (myInputXmlFile):
    '''Create a set of words currently marked with <rs> and another list of words
        currently marked with <hi>. Check that words marked <rs> are never marked as <hi>
        in other points of the text, and the other way around.
        '''
    okwords = {
            # Words that are OK to be marked both as <hi> and as <rs> in a specific file
            '../xml/bonetti.xml': ['domine', 'dominus'],
            '../xml/a.xml': [],
            '../xml/g.xml': []
            }
    rsset = nameset(myInputXmlFile, mytag='rs', addrstxt=False)
    hiset = nameset(myInputXmlFile, mytag='hi', addrstxt=False)
    for r in rsset:
        if r in hiset and not r in okwords[myInputXmlFile]:
            print('Word "' + r + '" is marked with <rs>, but elsewhere also with <hi>')
