#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module manages <app> elements from a TEI XML file '''


import my_database_import
import variant_type
import operator
from lxml import etree
from myconst import ns, xmlpath, dbpath

debug = False


class treeWithAppElements:

    def __init__(self, juxtaSiglum, printSiglum, msSiglum, quiet=False):
        ''' - juxtaSiglum is the siglum (e.g. 'm1' or 'm2')
                of the file with the <app> elements;
            - printSiglum is the siglum (e.g. 'g' or 'bonetti')
                of the first witness (that's normally the print edition)
                of the first witness (that's normally the print edition)
            - msSiglum is the siglum (e.g. 'a' or 'o') of the 2nd witness
                (normally a MS).
            - if quiet is True: suppress basic messages '''
        self.juxtaSiglum = juxtaSiglum
        self.myJuxtaXmlFile = '%s%s.xml' % (xmlpath, juxtaSiglum)
        self.outputXmlFile = self.myJuxtaXmlFile.replace('.xml', '-out.xml')
        self.printSiglum, self.msSiglum = printSiglum, msSiglum
        self.juxtaTree = etree.parse(self.myJuxtaXmlFile)
        self.apps = self.juxtaTree.findall('.//t:app', ns)
        self.quiet = quiet
        # Import tables from DB
        self.decision_table = my_database_import.import_table(
            dbpath,
            'romualdus.sqlite3',
            'decision_variant_types')
        self.decisions = my_database_import.import_table(
            dbpath,
            'priscianus.sqlite3',
            'decisions')

    def appDict(self):
        ''' Arguments:
            The function parses file myJuxtaXmlFile, finds all <app> elements,
            then creates and populates 'comparisons', a list of dictionaries
            (one dict for each <app> in the TEI XML file).
            Each dict in the list is the result of the comparison of two
            <app> TEI XML elements, and has those keys (examples are for
            variants "sillaba" vs "syllaba"):
                'r1' = the variant characters in myString1 ('y'),
                    inherited from function variantComparison
                'r2' = the variant characters in myString2 ('i'),
                    inherited from function variantComparison
                'type' = the variant type ('y-type'),
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
                      (self.myJuxtaXmlFile,
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
            myComp = variant_type.variantComparison(printText, msText)
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
            {'missing-in-ms-type': 124,
            'missing-in-print-vs-punct-in-ms-type': 252 etc.}
            counting in how many <app> elements in the juxtaTree each
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
        if not self.quiet:
            print(('\n[set_variant_types_in_appcrit_tei_file / '
                   'variantTypesCountPrint]: '
                   'In file {} there are:').format(self.juxtaSiglum))
            for x in self.variantTypesCount():
                print('{:5} {:12}'.format(x[1], x[0]))

    def setTypeAttributesForApps(self):
        '''Set @type attributes in <app> elements in the input TEI XML file '''
        if debug:
            myTypesDebug = [c['type'] for c in self.appDict()]
            print('[Debug 07.03.2020] %s' % (set(myTypesDebug)))
        for c in self.appDict():
            c['app'].set('type', c['type'])
            if debug:
                print('\n')
                print('«%s» | «%s» %15s @type="%s"' %
                      (c['printText'], c['msText'], '·', c['type']))
                for k in c:
                    print('%s: «%s»' % (k, c[k]))

    def setLemsBasedOnSicCorr(self):
        # self.juxtaSiglum, self.printSiglum, self.msSiglum
        if self.printSiglum == 'g':
            myPrintXmlFile = '%s%s.xml' % (xmlpath, self.printSiglum)
        elif self.printSiglum == 'b':
            # Cope with the fact that the xml file for Bonetti currently
            # is not b.xml but bonetti.xml:
            myPrintXmlFile = '%s%s.xml' % (xmlpath, 'bonetti')
        printTree = etree.parse(myPrintXmlFile)
        corrs = printTree.findall('.//t:corr', ns)
        # choices = [corr.getparent() for corr in corrs]
        # sics = [choice.find('.//t:sic', ns) for choice in choices]

        # Create a list of dictionaries, like:
        # {'choice' = <choice> element, 'corr' = <corr>, 'sic' = <sic>}
        corrections = []
        for c in corrs:
            myDict = {'corr': c}    # A dictionary
            myDict['choice'] = c.getparent()
            myDict['sic'] = myDict['choice'].find('.//t:sic', ns)
            corrections.append(myDict)

        # Manage case in which <choice><orig>+<reg> is in <corr>:
        for c in corrections:
            for e in [c['corr'], c['sic']]:
                # If <sic> or <corr> has a <choice> child:
                innerchoice = e.find('.//t:choice', ns)
                if innerchoice is not None:
                    # If <choice> has <reg> and <orig> as children:
                    innerreg = innerchoice.find('.//t:reg', ns)
                    innerorig = innerchoice.find('.//t:orig', ns)
                    if innerreg is not None and innerorig is not None:
                        # Remove <orig> and keep <reg>:
                        innerchoice.remove(innerorig)

        # Get (iter)text of <corr> and of <sic>
        for c in corrections:
            c['corrText'] = ''.join(c['corr'].itertext())
            c['sicText'] = ''.join(c['sic'].itertext())

        # Locate the corrections in m1 or m2
        count = 0
        for c in corrections:
            for a in self.appDict():
                # ...but I guess that it should only be
                # if a[sicText] == a[printText] (not also corrText)
                '''if c['corrText'].lower() == a['printText'].lower() or \
                   c['sicText'].lower() == a['printText'].lower():'''
                if c['sicText'].lower() == a['printText'].lower():
                    count += 1
                    if not self.quiet:
                        print(('[set lems based on sic/corr], '
                               'file {}: '
                               'Matching correction «{}» for «{}» '
                               'with app print «{}»/ms «{}»'
                               'in par. {}.').format(
                                   self.juxtaSiglum,
                                   c['corrText'],
                                   c['sicText'],
                                   a['printText'],
                                   a['msText'],
                                   a['app'].getparent().get('{%s}id' %
                                                            ns['xml'])
                             ))
        if not self.quiet:
            print(('[set lems based on sic/corr], file {}: '
                   'I located {} corrections').format(
                       self.juxtaSiglum,
                       count))

    def setLemsBasedOnType(self, setCert=True):
        '''For some @type(s) of <app>, decide the <lem> automatically '''

        # Decide <lem> and set @cert based on decision_table:
        if debug:
            print(self.appDict())
        for c in self.appDict():
            for myRow in self.decision_table:
                myType = myRow['type']
                if c['type'] == myType:
                    # It can be 'printReading' or 'msReading':
                    myPreferredRdg = myRow['preferredRdg']
                    # c[myPreferredRdg] is a TEI element, either <rdg wit="#a">
                    # or <rdg wit="#g">:
                    c[myPreferredRdg].tag = 'lem'
                    if setCert is True:
                        # myCert can be 'low', 'middle' or 'high':
                        myCert = myRow['cert']
                        c['app'].set('cert', myCert)

    def setLemsBasedOnDB(self):
        '''Read DB table and decide <lem> for some <app>s '''
        for record in self.decisions:
            pass

    def write(self):
        ''' Write my XML juxtaTree to an external file '''
        self.juxtaTree.write(self.outputXmlFile,
                             encoding='UTF-8', method='xml',
                             pretty_print=True, xml_declaration=True)
