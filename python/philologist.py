#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module manages <app> elements from a TEI XML file '''


import operator
import json
from lxml import etree
from myconst import ns, jsonpath, xmlpath
from variant_type import variantComparison

debug = False


class treeWithAppElements:

    def __init__(self, siglum, printSiglum, msSiglum):
        self.siglum = siglum
        self.myXmlFile = '%s%s.xml' % (xmlpath, siglum)
        self.outputXmlFile = self.myXmlFile.replace('.xml', '-out.xml')
        self.printSiglum, self.msSiglum = printSiglum, msSiglum
        self.tree = etree.parse(self.myXmlFile)
        self.apps = self.tree.findall('.//t:app', ns)

    def appDict(self):
        ''' Arguments:
            - printSiglum is the siglum (e.g. 'g' or 'bonetti')
            of the first witness (that's normally the print edition)
            - msSiglum is the siglum (e.g. 'a' or 'o') of the 2nd witness
            (normally a MS).
            The function parses file myXmlFile, finds all <app> elements,
            then creates and populates 'comparisons', a list of dictionaries
            (one dict for each <app> in the TEI XML file).
            Each dict in the list is the result of the comparison of two
            <app> TEI XML elements, and has those keys (examples are for
            variants "sillaba" vs "syllaba"):
                'r1' = the variant characters in myString1 ('y'),
                    inherited from function variantComparison
                'r2' = the variant characters in myString2 ('i'),
                    inherited from function variantComparison
                'type' = the variant type ('yType'),
                    inherited from function variantComparison
                plus new additional keys:
                'app' = the <app> XML element
                'printReading' = the <rdg> or <lem> XML element of the
                    1st witness (corresp. to printSiglum)
                'msReading' = the <rdg> or <lem> XML element of the
                    2nd witness (corresp. to msSiglum)
                'printText' = the text (string) of the variant
                    of the 1st witness (corresp. to printSiglum)
                'msText' = the text (string) of the variant
                    of the 2nd witness (corresp. to printSiglum)
        '''

        comparisons = []
        for app in self.apps:
            printReading = app.find('.//t:*[@wit="#%s"]' %
                                    (self.printSiglum), ns)
            msReading = app.find('.//t:*[@wit="#%s"]' % (self.msSiglum), ns)

            # Debug tests: check if something went wrong
            if debug:
                print(msReading)
            if debug and printReading is None:
                print('[Debug 07.03.2020 10.29] In MS %s printReading \
                      is None in app with parent \
                      paragraph %s with attributes %s and grandparent %s' %
                      (self.myXmlFile,
                       app.getparent().tag,
                       app.getparent().attrib,
                       app.getparent().getparent().tag))
            if msReading is None:
                print(printReading.text)
            if printReading.text is not None:
                printText = printReading.text
            else:
                printText = ''
            if msReading.text is not None:
                msText = msReading.text
            else:
                msText = ''
            if debug:
                print('\n\nprintText: «%s»' % (printText))
                print('msText: «%s»' % (msText))

            # MyComp is a dictionary:
            myComp = variantComparison(printText, msText)
            myComp['app'] = app
            myComp['printReading'] = printReading
            myComp['msReading'] = msReading
            myComp['printText'] = printText
            myComp['msText'] = msText
            comparisons.append(myComp)
        return comparisons

    def variantTypesList(self):
        '''Return a list all variant types in <app> '''
        myList = [c['type'] for c in self.appDict()]
        return myList

    def variantTypesCountSetList(self):
        '''Same as variantTypesList, but it returns a list
            in which each element only occurs once'''
        mySet = set(self.variantTypesList())
        # mySetList is still a list, but in which each element
        # of myList occurs only once
        mySetList = [t for t in mySet]
        return mySetList

    def variantTypesCount(self):
        '''Return a dict like
            {'missingInMSType': 124, 'missingInPrint-PunctInMS-Type': 252 etc.}
            counting in how many <app> elements in the tree each
            variant type recurs '''
        myList = self.variantTypesList()
        myListCount = []    # A list (of tuples)
        for x in self.variantTypesCountSetList():
            # Add a new tuple to the list
            myListCount.append((x, myList.count(x)))
        # Ordered from highest number to lowest:
        myListCount = sorted(myListCount, key=operator.itemgetter(1),
                             reverse=True)
        return myListCount

    def variantTypesCountPrint(self):
        '''Print variantTypesCountDict'''
        print(('\n[set_variant_types_in_appcrit_tei_file / '
               'variantTypesCountPrint]: '
               'In file {} there are:').format(self.siglum))
        for x in self.variantTypesCount():
            print('{:5} {:12}'.format(x[1], x[0]))

    def setTypeAttributesForApps(self):
        '''Set @type attributes in <app> elements in the input TEI XML file '''
        if debug:
            myTypesDebug = [c['type'] for c in self.appDict()]
            print('[Debug 07.03.2020] %s' % (set(myTypesDebug)))
        for c in self.appDict():
            c['app'].set('type', c['type'])
            # if c['type'] == 'yType':
            if debug:
                print('\n')
                print('«%s» | «%s» %15s @type="%s"' %
                      (c['printText'], c['msText'], '·', c['type']))
                for k in c:
                    print('%s: «%s»' % (k, c[k]))

    def setLems(self, setCert=True):
        '''For some @type(s) of <app>, decide the <lem> automatically '''

        jfile = ('%sdecision_table.json' % (jsonpath))
        with open(jfile) as f:
            decisionTable = json.load(f)

        # Decide <lem> and set @cert based on decisionTable:
        if debug:
            print(self.appDict())
        for c in self.appDict():
            for myType in decisionTable:
                if c['type'] == myType:
                    # It can be 'printReading' or 'msReading':
                    myPreferredRdg = decisionTable[myType]['preferredRdg']
                    # c[myPreferredRdg] is a TEI element, either <rdg wit="#a">
                    # or <rdg wit="#g">:
                    c[myPreferredRdg].tag = 'lem'
                    if setCert is True:
                        # myCert can be 'low', 'middle' or 'high':
                        myCert = decisionTable[myType]['cert']
                        c['app'].set('cert', myCert)

    def write(self):
        ''' Write my XML tree to an external file '''
        self.tree.write(self.outputXmlFile, encoding='UTF-8', method='xml',
                        pretty_print=True, xml_declaration=True)
