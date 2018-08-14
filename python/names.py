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


def sorted_nicely(l): 
    ''' Sort the given iterable in the way that humans expect.''' 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)


def write_to_output_file (myiterable):
    datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
    with open ('%s_output.txt' % (datetime), 'w') as outfile:
        for x in myiterable:
            print(x, file=outfile)

class Names():

    def __init__(self, namefile):
        self.namefile = namefile
        self.nametree = etree.parse(namefile)
        self.okwords = {
                # Words that are OK to be marked both as <hi> and as <rs> in a specific file
                '../xml/bonetti.xml': ['domine', 'dominus'],
                '../xml/a.xml': [],
                '../xml/g.xml': ['domine', 'dominus'],
                '../xml/foo.xml': ['domine', 'dominus', 'dominum', 'augusti', 'augustus', 'justo', 'quinto', 'pius',
                    'augusto', ],
                }


    def namedict (self, mydicttag='rs'):
        ''' Return a dictionary in which:
            * each key is an lxml Element object with tag name = mydicttag (typipcally <rs> or <hi>);
            * each value is the itertext() of that element in normalized form, i.e. the name included in it and
                in its child elements.
            All names are in lowercase.
            '''
        ond = {}    # (output names dictionary) 
        mynames = self.nametree.findall('.//t:%s' % (mydicttag), constants.ns)

        # Case 1: <rs> without child elements
        ond = {rs:rs.text.lower() for rs in mynames if len(list(rs)) == 0 }   

        # Case 2: <rs> with child elements
        for m in mynames:   # 
            if len(list(m)) > 0:
                for outcast in ['abbr', 'orig', 'sic', 'del']:  # Remove 'orig' and company
                                                                # (i.e. only leave 'reg' & co.: 'jovem' becomes 'iouem') 
                    if m.find('.//t:%s' % (outcast), constants.ns) is not None:   
                        outcastelem = m.find('.//t:%s' % (outcast), constants.ns)
                        outcastelem.getparent().remove(outcastelem)
                ond[m] = ''.join(m.itertext()).replace('\n', '')

        return ond 

    def nameset (self, mysettag='rs'):
        ''' Return a set (not list) of names marked
            with mysettag (typipcally <rs> or <hi>) in that file. All names in the set are in lowercase.
            The set is in alphabetical order.
            '''
        mynamesdict = self.namedict(mydicttag=mysettag)          # Get a dict of all elements with their itertext()
        namelist = [mynamesdict[n] for n in mynamesdict]    # Get only the itertext() of each element
        return sorted_nicely(set(namelist))


    def checkrs (self, outputmethod='returnset'):
        ''' [WARNING: slow function]
            Get a set of names marked with <rs>. Then perform a textual search on the XML file for each proper name
            listed in file myProperNamesFile, and check that each of the occurrences of each name
            in the XML files is marked with a <rs> tag.
            1. If outputmethod='screen', for each wrong case, print out (to screen) the XML file name,
                the parent element that includes the name, and that element's text.
            2. If outputmethod='returnset', don't show each occurrence of the unmarked word, but return a set in which
                each word only occurs once.
            '''
        rsset = self.nameset(mysettag='rs')
        mybody = self.nametree.find('.//t:body', constants.ns)
        regexpNS = 'http://exslt.org/regular-expressions'
        print('\n---\n\nNames marked with <rs> at some point of the text, but not marked in other points:')
        unmarked = []
        for myname in rsset:
            if myname not in self.okwords[self.namefile]:
                find = etree.XPath('//text()[re:match(., "\W%s\W", "i")]/parent::*' % (myname), namespaces={'re':regexpNS})
                # Doc: http://exslt.org/regexp/ e http://exslt.org/regexp/functions/test/index.html
                #for r in find(self.nametree):
                for r in find(mybody):
                    if r.tag != constants.tei_ns + 'rs':    # If the proper name is not marked with <rs>
                        if outputmethod == 'returnset':
                            unmarked.append(myname)
                        elif outputmethod == 'screen':
                            simpletag = r.tag.split('}')[1]
                            print('%10s %s %10s %s %10s %s' % ('File:', self.namefile, 'Name:', myname, 'Parent tag:', simpletag))
                        else:
                            print('outputmethod should be "returnset" or "screen"')
        if outputmethod == 'returnset':
            print(set(unmarked))
            return set(unmarked)


    def checkrsandhi (self, outmethod = 'screen'):
        '''Create a set of words currently marked with <rs> and another list of words
            currently marked with <hi>. Check that words marked <rs> are never marked as <hi>
            in other points of the text.
            1. If outmethod = 'screen', write output to screen in the verbose form:
                «Word "apollinis" is marked with <rs>, but elsewhere also with <hi>"»
            2. If outmethod includes a filename (e.g. outfile='filename.txt'), write a non-verbse output to that file, as
                a simple list of names.
            3. If outmethod= xml' , overwrite the original .xml file (after creating a backup of it)
                and add @type="wrong" and @subtype="[the name]" to the element (e.g. <rs type="wrong" subtype="caesar">
            '''

        rsdict = self.namedict(mydicttag='rs')
        hidict = self.namedict(mydicttag='hi')
        rsset = self.nameset(mysettag='rs')
        hiset = self.nameset(mysettag='hi')
        issues_list = []

        if outmethod == 'xml':
            
            #for r in rsdict:   # debug
                #r.set('n', 'foo')
            
            # Check for words in <rs> that are also marked with <hi>
            for r in rsdict:
                if rsdict[r] in hiset and not rsdict[r] in self.okwords[self.namefile]:
                    r.set('type', 'wrong')
                    r.set('subtype', rsdict[r])

            # Check for words in <hi> that are also marked with <rs>
            for h in hidict:
                if hidict[h] in rsset and not hidict[h] in self.okwords[self.namefile]:
                    h.set('type', 'wrong')
                    h.set('subtype', hidict[h])

            # Output

            # Create backup
            datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
            backup_filename = '_'.join([self.namefile, 'backup', datetime])
            os.system('cp %s %s' % (self.namefile, backup_filename))
            # Write to output XML file 
            self.nametree.write(self.namefile.replace('.xml', '_with_wrong_rs.xml'), encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)


        else:   # If outmethod is 'screen' or is a filename (e.g. outmethod='outfile.txt')

            for r in rsset:
                if r in hiset and not r in self.okwords[self.namefile]:
                    issues_list.append(r)

            # Output
            if outmethod == 'screen':   # If there's no 'outmethod' argument, print to screen
                print('\n\nThe following words are marked sometimes with <rs>, sometimes with <hi>:\n')
                for i in sorted(issues_list):
                    print(i)
            elif outmethod is not None and outmethod != 'screen' and outmethod != 'xml':
                # If it's a filename, print to the filename
                with  open(outmethod, 'w') as OUT:
                    for i in sorted(issues_list):
                        print(i, file=OUT)
            else:
                print('Argument outmethod must be "screen", "xml", or a filename')






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


##############################
# FUNCTIONS NO LONGER IN USE #
##############################

def old_checkrsandhi (myInputXmlFile, outfile = None):
    '''Create a set of words currently marked with <rs> and another list of words
        currently marked with <hi>. Check that words marked <rs> are never marked as <hi>
        in other points of the text.
        If outfile = None, write output to screen in the verbose form:
            «Word "apollinis" is marked with <rs>, but elsewhere also with <hi>"»
        If outfile includes a filename (e.g. outfile='filename.txt'), write a non-verbse output to that file, as
            a simple list of names.
        '''
    okwords = {
            # Words that are OK to be marked both as <hi> and as <rs> in a specific file
            '../xml/bonetti.xml': ['domine', 'dominus'],
            '../xml/a.xml': [],
            '../xml/g.xml': ['domine', 'dominus']
            }
    rsset = nameset(myInputXmlFile, mysettag='rs')
    hiset = nameset(myInputXmlFile, mysettag='hi')
    issues = []

    # Check for words repeated in the two lists
    for r in rsset:
        if r in hiset and not r in okwords[myInputXmlFile]:
            issues.append(r)
    
    # Output to file
    if outfile != 'xml' and outfile is not None:  # If it's a filename
        with  open(outfile, 'w') as OUT:
            for i in sorted(issues):
                print(i, file=OUT)
    elif outfile is None:   # If there's no 'outfile' argument
        for i in sorted(issues):
            print('Word "' + r + '" is marked with <rs>, but elsewhere also with <hi>')


def old_listnames (properNamesInputXmlFile, myNamespace):
    ''' This script parses the ../xml/temp_g.xml file and lists
        the textual content of all its <rs> elements.
        All names in the list are in lowercase.
        '''
    self.nametree = etree.parse(properNamesInputXmlFile)
    rss = self.nametree.findall('.//%srs' % myNamespace)
    for rs in rss:
        print(rs.text, end=',')
    print('\n---\n')


def old_nameset (properNamesInputXmlFile, mysettag='rs', addrstxt=False):
    ''' Parse an xml file and return a set (not list) of names marked
        with mysettag (typipcally <rs> or <hi>) in that file. All names in the set are in lowercase.
        If addrstxt=True, add to that set the proper names in file rs.txt
        '''
    self.nametree = etree.parse(properNamesInputXmlFile)
    #rss = self.nametree.findall('.//t:rs', constants.ns)  # Old version
    mynames = self.nametree.findall('.//t:%s' % (mysettag), constants.ns)
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


def old_checkrs (myInputXmlFile, myProperNamesFile):
    ''' Update file rs.txt based on the <rs>'s in the XML file 'myInputXmlFile'.
        Then parse 'myInputXmlFile'
        perform a textual search on the XML file for each proper name
        listed in file myProperNamesFile, and check that each of the occurrences of each name
        in the XML files is marked with a <rs> tag.
        If this is not the case, then print out the XML file name,
        the parent element that includes the name, and that element's text. '''
    updatenamesfile(myInputXmlFile)
    self.nametree = etree.parse(myInputXmlFile)
    regexpNS = 'http://exslt.org/regular-expressions'
    with open (myProperNamesFile, 'r') as rsfile:
        for l in rsfile:
            myname = l.strip().lower()
            find = etree.XPath('//text()[re:match(., "\W%s\W", "i")]/parent::*' % (myname), namespaces={'re':regexpNS})
            # Doc: http://exslt.org/regexp/ e http://exslt.org/regexp/functions/test/index.html
            for r in find(self.nametree):
                if r.tag != constants.tei_ns + 'rs':    # If the proper name is not marked with <rs>
                    print('%10s %s %10s %s %10s %s' % ('File:', myInputXmlFile, 'Name:', myname, 'Tag:', r.tag))




##################
# CALL FUNCTIONS #
##################

#N = Names('../xml/foo.xml')
#N.checkrs()

'''
for x in N.checkrs():
    print(
            x
            )



checkrsandhi ('../xml/foo.xml', outmethod='xml')


N = nameset ('../xml/g.xml')
for n in N:
    #print(n, '\t', N[n])
    print(n)
    '''
