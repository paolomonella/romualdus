#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module manages <app> elements from a TEI XML file '''


import roman, operator
from lxml import etree
from myconst import ns
from variant_type import variantComparison

debug = False

class treeWithAppElements:

    def __init__ (self, myXmlFile, printSiglum, msSiglum):
        self.printSiglum, self.msSiglum = printSiglum, msSiglum
        self.tree = etree.parse(myXmlFile)
        self.apps = self.tree.findall('.//t:app', ns)
        self.outputXmlFile = myXmlFile.replace('.xml', '-out.xml')

    def appComparisonList (self):
        ''' Arguments:  printSiglum is the siglum (e.g. 'g' or 'bonetti') of the first witness (that's normally the print edition)
                        msSiglum is the siglum (e.g. 'a' or 'o') of the 2nd witness (normally a MS)
            The function parses file myXmlFile, finds all <app> elements, then
            creates and populates 'comparisons', a list of dictionaries (one dict for each <app> in the TEI XML file).
            Each dict in the list is the result of the comparison of two <app> TEI XML elements, and
            has those keys (examples are for variants "sillaba" vs "syllaba"):
                'r1' = the variant characters in myString1 ('y'), inherited from function variantComparison
                'r2' = the variant characters in myString2 ('i'), inherited from function variantComparison
                'type' = the variant type ('yType'), inherited from function variantComparison
                plus new additional keys:
                'app' = the <app> XML element
                'printReading' = the <rdg> or <lem> XML element of the 1st witness (corresp. to printSiglum)
                'msReading' = the <rdg> or <lem> XML element of the 2nd witness (corresp. to msSiglum)
                'printText' = the text (string) of the variant of the 1st witness (corresp. to printSiglum)
                'msText' = the text (string) of the variant of the 2nd witness (corresp. to printSiglum)
        '''

        comparisons = []    
        for app in self.apps:
            printReading = app.find('.//t:*[@wit="#%s"]' % (self.printSiglum), ns)
            msReading = app.find('.//t:*[@wit="#%s"]' % (self.msSiglum), ns)
            if printReading is None:
                print(msReading.text)
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

            myComp = variantComparison(printText, msText) # A dict. Note that the 1st one is the Garufi text; the 2nd is MS A text
            myComp['app'] = app
            myComp['printReading'] = printReading
            myComp['msReading'] = msReading
            myComp['printText'] = printText
            myComp['msText'] = msText
            comparisons.append(myComp)
        return comparisons


    def variantTypesList (self):
        '''Return a list all variant types in <app> '''
        myList = [c['type'] for c in self.appComparisonList()]
        return myList

    def variantTypesCountSetList (self):
        '''Same as variantTypesList, but it returns a list in which each element only occurs once'''
        mySet = set(self.variantTypesList())
        mySetList  = [t for t in mySet] # This is still a list, but in which each element of myList occurs only once
        return mySetList

    def variantTypesCount (self):
        '''Return a dict like {'missingInMSType': 124, 'missingInPrint-PunctInMS-Type': 252 etc.}
            counting in how many <app> elements in the tree each variant type recurs '''
        myList = self.variantTypesList()
        myListCount = []    # A list (of tuples)
        for x in self.variantTypesCountSetList():
            myListCount.append((x, myList.count(x)))  # Add a new tuple to the list
        myListCount =  sorted(myListCount, key=operator.itemgetter(1), reverse=True)    # Ordered from highest number to lowest
        return myListCount

    def variantTypesCountPrint (self):
        '''Print variantTypesCountDict'''
        #sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)  # A list of tuples
        #sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)  # A list of tuples
        #print(len(self.variantTypesCount()))
        for x in self.variantTypesCount():
            print('{:5} {:12}'.format(x[1], x[0]))

    def setTypeAttributesForApps (self):
        '''Set @type attributes in <app> elements in the input TEI XML file '''
        for c in self.appComparisonList():
            c['app'].set('type', c['type'])
            if debug:
                print('\n')
                print('«%s» | «%s» %15s @type="%s"' % (c['printText'], c['msText'], '·', c['type']))
                for k in c:
                    print('%s: «%s»' % (k, c[k]))

    def setLems (self):
        '''For some @type(s) of <app>, decide the <lem> automatically '''

        decisionTable = {
                'num-WordType':
                    {'preferredRdg': 'printReading', 'cert': 'high'},
                'differentPunctType':
                    {'preferredRdg': 'msReading', 'cert': 'high'},
                'unknown':
                    {'preferredRdg': 'printReading', 'cert': 'medium'},
                'missingInPrintType':
                    {'preferredRdg': 'printReading', 'cert': 'medium'},
                'num-numType':
                    {'preferredRdg': 'printReading', 'cert': 'medium'},
                'punctInPrint-punctAndLettersInMS-Type':    # Only 4 occurrences in a1/Garufi
                    {'preferredRdg': 'printReading'},
                'caseType':
                    {'preferredRdg': 'msReading', 'cert': 'high'},
                'missingInMSType':
                    {'preferredRdg': 'printReading', 'cert': 'medium'},
                'missingInPrint-PunctInMS-Type':
                    {'preferredRdg': 'msReading', 'cert': 'high'},
                'punctInPrint-missingInMS-Type':
                    {'preferredRdg': 'msReading', 'cert': 'high'},
                'nichilType':
                    {'preferredRdg': 'printReading', 'cert': 'medium'},
                }

        for c in self.appComparisonList():  # Decide <lem> and set @cert based on decisionTable
            for myType in decisionTable:
                if c['type'] == myType:
                    myPreferredRdg = decisionTable[myType]['preferredRdg']    # It can be 'printReading' or 'msReading'
                    c[myPreferredRdg].tag = 'lem' # c[myPreferredRdg] is a TEI element, either <rdg wit="#a"> or <rdg wit="#g">
                    myCert = decisionTable[myType]['cert']    # It can be 'low', 'middle' or 'high'
                    c['app'].set('cert', myCert)


    def countVariantTypes (self, countedType):
        '''Count types of variants in a comparisonList. The 1st two arguments are two sigla (put print witness first).
            The 3rd arguments is the type of variant (e.g. "yType") one particularly wants to count '''
        typedList = []
        untypedList = []
        countedTypeList = []
        for c in self.appComparisonList():
            if c['type'] != 'unknown':
                typedList.append(c)
            else:
                untypedList.append(c)
                if debug:
                    print('\n')
                    for k in c:
                        print('%s: «%s»' % (k, c[k]))

            if c['type'] == countedType:
                countedTypeList.append(c)

        print('\nTyped:', len(typedList))
        print('Untyped:', len(untypedList))
        print('Type "%s":' % (countedType), len(countedTypeList))

    def write (self):
        self.tree.write(self.outputXmlFile, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)

myTree = treeWithAppElements('../xml/m.xml', 'g', 'a')
myTree.variantTypesCountPrint()
myTree.setLems()
myTree.write()
