#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module manages <app> elements from a TEI XML file '''


import roman
from lxml import etree
from myconst import ns
from variant_type import variantComparison

debug = False



def appComparisonList (myXmlFile, printSiglum, msSiglum):
    ''' Arguments:  printSiglum is the siglum (e.g. 'g' or 'bonetti') of the first witness (that's normally the print edition)
                    msSiglum is the siglum (e.g. 'a' or 'o') of the 2nd witness (normally a MS)
        The function parses file myXmlFile, finds all <app> elements, then
        creates and populates 'comparisons', a list of dictionaries (one dict for each <app> in the TEI XML file).
        Each dict in the list is the result of the comparison of two <app> TEI XML elements, and
        has those keys (examples are for variants "sillaba" vs "syllaba"):
            "r1" = the variant characters in myString1 ("y"), inherited from function variantComparison
            "r2" = the variant characters in myString2 ("i"), inherited from function variantComparison
            "type" = the variant type ("yType"), inherited from function variantComparison
            plus new additional keys:
            "app" = the <app> XML element
            "printReading" = the <rdg> or <lem> XML element of the 1st witness (corresp. to printSiglum)
            "msReading" = the <rdg> or <lem> XML element of the 2nd witness (corresp. to msSiglum)
            "printText" = the text (string) of the variant of the 1st witness (corresp. to printSiglum)
            "msText" = the text (string) of the variant of the 2nd witness (corresp. to printSiglum)
    '''

    tree = etree.parse(myXmlFile)
    apps = tree.findall('.//t:app', ns)

    comparisons = []    
    for app in apps:
        printReading = app.find('.//t:*[@wit="#%s"]' % (printSiglum), ns)
        msReading = app.find('.//t:*[@wit="#%s"]' % (msSiglum), ns)
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

def countVariantTypes(myXmlFile, printSiglum, msSiglum, countedType):
    '''Count types of variants in a comparisonList. The 1st two arguments are two sigla (put print witness first).
        The 3rd arguments is the type of variant (e.g. "yType") one particularly wants to count '''
    typedList = []
    untypedList = []
    countedTypeList = []
    for c in appComparisonList(myXmlFile, printSiglum, msSiglum):
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

    print('typed:', len(typedList))
    print('untyped:', len(untypedList))
    print('%s:' % (countedType), len(countedTypeList))


countVariantTypes('../xml/m.xml', 'g', 'a', 'num-numType')
