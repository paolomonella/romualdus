#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module manages strings (e.g. "syllaba" vs "sillaba"), not <app> or other TEI XML elements'''

import roman
from lxml import etree
from myconst import ns

debug = False

def numeralCheck(myStringOrig):
    '''Check if a string is a numeral. If it is, return a dict including
        a list of possible Latin words representing the numeral. E.g.: 'III' (and 'iii', case insensitive) should return:
        {'isNumeral': True, 'words': ['tres', 'tribus', 'tria', 'trium']}
        The list can be incomplete'''
    numeralWordDict = {
            1: ['unus', 'unum'], 2: ['duo', 'due', 'duobus'],
            4: ['quattuor', 'quatuor'], 6: ['sex'], # I am not including quinta (ordinal)
            8: ['octo'], 10: ['decem'], # not including octauo (ordinal)
            17: ['decem et septem'],
            40: ['quadraginta'],
            47: ['quadraginta et septem'],
            30: ['triginta'],
            100: ['centum'],
            # not including 164: ['centesimo sexagesimo quarto'] (ordinal)
            200: ['ducentos'],
            # not including 302: ['tricesimus secundus'] (ordinal)
            310: ['trecentum decem'],
            342: ['trecentum quadraginta duos'],
            532: ['quingentorum triginta duorum'],
            1000: ['mille'],
            }
    myString = myStringOrig.upper()
    numeralCheckDict = { 'words': [] }
    try:
        if debug: print('String %s is a Roman numeral, corresponding to %d' % (myStringOrig, myArabic))
        myArabic = roman.fromRoman(myString)
        numeralCheckDict['isNumeral'] = True
        try:
            numeralCheckDict['words'] = numeralWordDict[myArabic]
        except KeyError:
            if debug:
                print('String %s is a Roman numeral, corresponding to %d, but I have no Latin words for it' % (myStringOrig, myArabic))
            numeralCheckDict['words'] = ['noWord']
    except roman.InvalidRomanNumeralError:
        if debug: print('Ho beccato un errore roman.InvalidRomanNumeralError per la stringa «%s»' % (myString))
        numeralCheckDict['isNumeral'] = False
        numeralCheckDict['words'] = []
    return numeralCheckDict


def getVariantTypeBasedOnWholeVariant (myString1, myString2):
    ''' Take two strings (two variants) and try to detect the variant type based on the whole variant
        '''

    myType = 'unknown'
    if numeralCheck(myString1.strip())['isNumeral'] and numeralCheck(myString2.strip())['isNumeral']:
        # Detect case 'VIII' / 'IX' (case-insensitive)
        if debug: print('\n«%s»     «%s»' % (myString1, myString2))
        myType = 'num-numType'
    elif numeralCheck(myString1.strip())['isNumeral']:
        # Detect case 'VIII' / 'octo' (case-insensitive)
        if debug: print('\n«%s»     «%s»      «%s»' %
                    (myString1, myString2, numeralCheck(myString1.strip())['words']))
        for myWord in numeralCheck(myString1.strip())['words']: # Check the corresponding words, e.g.: ['octo', 'octauo']
            if myWord == myString2.strip().lower(): # If the other variant corresponds to one of those words
                if debug: print('EUREKA! This is a word/non-word numeral variant!')
                myType = 'num-WordType'
    elif numeralCheck(myString2.strip())['isNumeral']:
        # Detect case 'octo' / 'VIII' (case-insensitive)
        if debug: print('\n«%s»     «%s»      «%s»' % 
                (myString1, myString2, numeralCheck(myString1.strip())['words']))
        for myWord in numeralCheck(myString2.strip())['words']: # Check the corresponding words, e.g.: ['octo', 'octauo']
            if myWord == myString1.strip().lower(): # If the other variant corresponds to one of those words
                if debug: print('EUREKA! This is a word/non-word numeral variant!')
                myType = 'num-WordType'

    return myType


def getDiff (myString1, myString2):
    ''' Take two strings (e.g. sillaba, syllaba) and get the diff (e.g. y, i). Return a list with the diff, e.g. ['y', 'i']
        '''

    result1 = ''
    result2 = ''

    #handle the case where one string is longer than the other
    maxlen=len(myString2) if len(myString1)<len(myString2) else len(myString1)

    #loop through the characters
    for i in range(maxlen):
      #use a slice rather than index in case one string longer than other
      letter1=myString1[i:i+1]
      letter2=myString2[i:i+1]
      #create string with differences
      if letter1 != letter2:
        result1+=letter1
        result2+=letter2
    return [result1, result2]


def getVariantTypeBasedOnDiff (myDiffList):
    ''' Input a list with two strings constituting the differences b/w two variants, e.g. input ['i', 'y']
        (from variants ille/ylle) and evaluate the type of variant. '''

    myDiff1, myDiff2 = myDiffList[0], myDiffList[1]

    typeList = [
            ['i', 'y', 'y'],
            ['u', 'v', 'v'],
            ['U', 'V', 'v'],
            ['i', 'j', 'j'],
            ['ae', 'e', 'ae'],
            ['hegium', 'egium', 'h'],
            ['Hostiensi', 'Ostiensi', 'h'],
            ['hlodoueus', 'lodoueus', 'h'],
            ['habentes', 'abentes', 'h'],
            ['hari', 'ari', 'h'],
            ['ha', 'a', 'h'],
            ['lia', 'ia', 'll'],
            ['lisario', 'isario', 'll'],
            ['lisarius', 'isarius', 'll'],
            ['np', 'mb', 'orth'],
            ['nati', 'pnati', 'orth'],
            ['historia', 'ystoria', 'hi-y-'],
            ['historiis', 'ystoriis', 'hi-y-'],
            ['hil', 'chil', 'nichil'],
            ]

    myPunctString = '!"()*+,-.:;=?^_`{|}~' + "'"     # long version: it generates 210 combinations
    #myPunctString = ',.:;?!"()-' + "'"     # it generates 55 combinations
    myPunctList = [p for p in myPunctString]  # transform the string to a list
    #punctCombList = [   [c[0], c[1], 'punct']   for c in combinations(myPunctList, 2)]  # it is a list of lists

    if myDiff1.strip() == '' and myDiff2.strip() in myPunctList:
        #print('«%s» | «%s» | «%s»'  % (myDiff1.strip(), myDiff2.strip(), myPunctString)  )
        myType = 'missingInG-PunctInA-Type'

    elif myDiff2.strip() == '' and myDiff1.strip() in myPunctList:
        myType = 'missingInA-PunctInG-Type'

    elif myDiff1.strip() == '' and myDiff2.strip() not in myPunctList and myDiff2.strip() != '':
        myType = 'missingInGType'

    elif myDiff2.strip() == '' and myDiff1.strip() not in myPunctList and myDiff1.strip() != '':
        myType = 'missingInAType'

    elif myDiff1.strip()in myPunctList and myDiff2.strip() in myPunctList:
        myType = 'differentPunctType'

    elif myDiff1.strip() in myPunctList and myDiff2.strip() not in myPunctList and myDiff2.strip() != '':
        myType = 'punctInG-lettersInA-Type'

    elif myDiff2.strip() in myPunctList and myDiff1.strip() not in myPunctList and myDiff1.strip() != '':
        myType = 'lettersInG-punctInA-Type'

    elif myDiff1.strip().lower() == myDiff2.strip().lower():
        myType = 'caseType'
    else:
        myType = 'unknown'

    for t in typeList:
        if sorted([myDiff1, myDiff2]) == sorted([t[0], t[1]]): # sorted() makes the order of diffs in the MSS irrelevant
            if myType == 'unknown':
                myType = '%sType' % (t[2])
            else:
                print('Error! Diff «%s»/«%s» matched two different types: %s and %sType' % (myDiff1, myDiff2, myType, t[2]))

    return(myType)


def variantComparison(myString1, myString2):
    ''' Compare two strings and return the differences. Example: "sillaba" vs "syllaba"
        This function returns a dictionary (whose values are all strings):
            "r1" = the variant characters in myString1 ("y")
            "r2" = the variant characters in myString2 ("i")
            "type" is the type of variant (a string: e.g. "yType" in this example, or "jType" etc.)
        Source:
        https://stackoverflow.com/questions/30683463/comparing-two-strings-and-returning-the-difference-python-3#30683513
    '''

    myDiff = getDiff(myString1, myString2)

    if getVariantTypeBasedOnWholeVariant(myString1, myString2) != 'unknown':
        # Function getVariantTypeBasedOnWholeVariant returns 'unknown' if it doesn't detect a variant type
        myVariantType = getVariantTypeBasedOnWholeVariant(myString1, myString2)
    else:
        # If function getVariantTypeBasedOnWholeVariant doesn't detect a variant type, try detecting one based on diff
        myVariantType = getVariantTypeBasedOnDiff(myDiff)

    return({'r1': myDiff[0], 'r2': myDiff[1], 'type': myVariantType})
