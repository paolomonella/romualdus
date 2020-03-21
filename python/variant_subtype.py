#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module manages strings (e.g. "syllaba" vs "sillaba"), not <app> or
    other TEI XML elements'''

import roman
# import sqlite3
import my_database_import
from myconst import dbpath

debug = False

# Import table of diff subtypes and subtypes from DB #
diff_subtypes = my_database_import.import_table(dbpath,
                                                'romualdus.sqlite3',
                                                'diff_subtypes')

#######################
# All other functions #
#######################


def numeralCheck(myStringOrig):
    '''Check if a string is a numeral. If it is, return a dict including
        a list of possible Latin words representing the numeral. E.g.: 'III'
        (and 'iii', case insensitive) should return:
        {'isNumeral': True, 'words': ['tres', 'tribus', 'tria', 'trium']}
        The list can be incomplete'''
    numeralWordDict = {
            1: ['unus', 'unum'], 2: ['duo', 'due', 'duobus'],
            4: ['quattuor', 'quatuor'], 6: ['sex'],
            # I am not including quinta (ordinal)
            8: ['octo'], 10: ['decem'],  # not including octauo (ordinal)
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
    numeralCheckDict = {'words': []}
    try:
        myArabic = roman.fromRoman(myString)
        if debug:
            print('String %s is a Roman numeral, corresponding to %d' %
                  (myStringOrig, myArabic))
        numeralCheckDict['isNumeral'] = True
        try:
            numeralCheckDict['words'] = numeralWordDict[myArabic]
        except KeyError:
            if debug:
                print('String %s is a Roman numeral, corresponding to %d, but \
                      I have no Latin words for it' % (myStringOrig, myArabic))
            numeralCheckDict['words'] = ['noWord']
    except roman.InvalidRomanNumeralError:
        if debug:
            print('Ho beccato un errore roman.InvalidRomanNumeralError per \
                    la stringa «%s»' % (myString))
        numeralCheckDict['isNumeral'] = False
        numeralCheckDict['words'] = []
    return numeralCheckDict


def getVariantSubTypeBasedOnWholeVariant(myString1, myString2):
    ''' Take two strings (two variants) and try to detect the variant subtype
        based on the whole variant
        '''
    # Create my list of punctuation characters
    # long version; it generates 210 combinations:
    myPunctString = '!"()*+,-.:;=?^_`{|}~' + "'"

    myPunctList = [p for p in myPunctString]  # transform the string to a list
    # punctCombList = [ [c[0], c[1], 'punct']
    #           for c in combinations(myPunctList, 2)]  # it is a list of lists

    # Detect case 'VIII' / 'IX' (case-insensitive)
    if numeralCheck(myString1.strip())['isNumeral'] \
       and numeralCheck(myString2.strip())['isNumeral']:
        if debug:
            print('\n«%s»     «%s»' % (myString1, myString2))
        my_subtype = 'num-num-subtype'
    elif numeralCheck(myString1.strip())['isNumeral']:
        # Detect case 'VIII' / 'octo' (case-insensitive)
        if debug:
            print('\n«%s»     «%s»      «%s»'
                  % (myString1, myString2,
                     numeralCheck(myString1.strip())['words']))
        # Check the corresponding words, e.g.: ['octo', 'octauo']:
        for myWord in numeralCheck(myString1.strip())['words']:
            # If the other variant corresponds to one of those words
            if myWord == myString2.strip().lower():
                if debug:
                    print('EUREKA! This is a word/non-word numeral variant!')
                my_subtype = 'num-word-subtype'
            else:
                my_subtype = 'unknown-subtype'

    # Detect case 'octo' / 'VIII' (case-insensitive):
    elif numeralCheck(myString2.strip())['isNumeral']:
        if debug:
            print('\n«%s»     «%s»      «%s»' %
                  (myString1, myString2,
                   numeralCheck(myString1.strip())['words']))
            # Check the corresponding words, e.g.: ['octo', 'octauo']:
        for myWord in numeralCheck(myString2.strip())['words']:
            # If the other variant corresponds to one of those words
            if myWord == myString1.strip().lower():
                if debug:
                        print('EUREKA! This is a word/non-word \
                              numeral variant!')
                my_subtype = 'num-word-subtype'
            else:
                my_subtype = 'unknown-subtype'

    elif myString1 != myString2 and myString1.lower() == myString2.lower():
        if debug:
            print(myString1.strip(), myString2.strip())
        my_subtype = 'case-subtype'

    elif myString1.strip() == '' and myString2.strip() in myPunctList:
        my_subtype = 'missing-in-print-vs-punct-in-ms-subtype'

    elif myString1.strip() in myPunctList and myString2.strip() == '':
        my_subtype = 'punct-in-print-vs-missing-in-ms-subtype'

    elif myString1.strip() == '' and myString2.strip() not in myPunctList \
            and myString2.strip() != '':
        my_subtype = 'missing-in-print-subtype'

    elif myString1.strip() not in myPunctList and myString1.strip() != '' \
            and myString2.strip() == '':
        my_subtype = 'missing-in-ms-subtype'

    elif myString1.strip() in myPunctList and myString2.strip() \
            in myPunctList:
        my_subtype = 'different-punct-subtype'

    # If first variant is only a punctuation sign and the second variant
    # has a punct plus at least one letter
    elif myString1.strip() in myPunctList \
            and any((j in myPunctString) for j in myString2.strip()) \
            and any(j.isalpha() for j in myString2.strip()):
        my_subtype = 'punct-in-print-vs-punct-and-letters-in-ms-subtype'

    # The same, the other way around
    elif myString2.strip() in myPunctList \
            and any((j in myPunctString) for j in myString1.strip()) \
            and any(j.isalpha() for j in myString1.strip()):
        my_subtype = 'punct-in-print-vs-missing-in-ms-subtype'

    elif \
            any((j in myPunctString) for j in myString1) \
            and any(j.isalpha() for j in myString1) \
            \
            and any((j in myPunctString) for j in myString2) \
            and any(j.isalpha() for j in myString2):
            # If both variants include a punct plus at least one letter. But
            # I'm only interested in the sub-case described by the next 'if'

        # Case «. Qui» | «, qui»    or    «, qui» ! «. Qui»
        # (i.e.: if both variants start with a punctuation char
        # followed by a space and the two punct chars are different)
        if myString1[0] in myPunctString and myString2[0] in myPunctString \
                and myString1[1] == myString2[1] == ' ' \
                and myString1[0] != myString2[0] \
                and myString1[2:].lower() == myString2[2:].lower():
            if debug:
                print('%s «%s» | «%s» %30s «%s» | «%s»' %
                      ('Strings:', myString1, myString2, 'Stripped strings:',
                       myString1.strip(), myString2.strip()))
            my_subtype = 'different-punct-subtype'
        else:
            my_subtype = 'unknown-subtype'

    else:
        my_subtype = 'unknown-subtype'

    return my_subtype


def getDiff(myString1, myString2):
    ''' Take two strings (e.g. sillaba, syllaba) and get the diff (e.g. y, i).
        Return a list with the diff, e.g. ['y', 'i']
        '''

    result1 = ''
    result2 = ''

    # Handle the case where one string is longer than the other
    maxlen = len(myString2) if len(myString1) < len(myString2) \
        else len(myString1)

    # Loop through the characters:
    # Use a slice rather than index in case one string longer than other:
    for i in range(maxlen):
        letter1 = myString1[i:i+1]
        letter2 = myString2[i:i+1]
        # Create string with differences:
        if letter1 != letter2:
            result1 += letter1
            result2 += letter2
    return [result1, result2]


def getVariantSubTypeBasedOnDiff(myDiffList, myString1, myString2):
    ''' Input a list with two strings constituting the differences b/w two
        variants, e.g. input ['i', 'y'] (from variants ille/ylle) and evaluate
        the subtype of variant. I am also adding two more arguments
        (myString1, myString2) for some checks on the function. '''

    myDiff1, myDiff2 = myDiffList[0], myDiffList[1]

    my_subtype = 'unknown-subtype'
    for t in diff_subtypes:
        # sorted() makes the order of diffs in the MSS irrelevant:
        # if sorted([myDiff1, myDiff2]) == sorted([t[0], t[1]]):
        if sorted([myDiff1, myDiff2]) == sorted([t['diff1'], t['diff2']]):
            if my_subtype == 'unknown-subtype':
                my_subtype = t['subtype']
                if debug:
                    print('[getVariantSubTypeBasedOnDiff] The diff\
                          between strings %s/%s is %s/%s,\
                          so the variant subtype is %s' %
                          (myString1, myString2, myDiff1, myDiff2, my_subtype))
            else:
                print(('Error! Diff «%s»/«%s» matched two different'
                       'subtypes: {} and {}-subtype').format(
                           myDiff1, myDiff2, my_subtype, t[2]))

    if debug:
            print('Trovato %s\n' % my_subtype)
    return(my_subtype)


def variantComparison(myString1, myString2):
    ''' Compare two strings and return the differences. Example:
        "sillaba" vs "syllaba".
        This function returns a dictionary (whose values are all strings):
            "r1" = the variant characters in myString1 ("y")
            "r2" = the variant characters in myString2 ("i")
            "subtype" is the subtype of variant (a string: e.g. "y-subtype"
                in this example, or "j-subtype" etc., that will become
                the @subtype value of element <app>)
        Source:
        https://stackoverflow.com/questions/30683463/comparing-two-strings-and-returning-the-difference-python-3#30683513
    '''

    myDiff = getDiff(myString1, myString2)

    if getVariantSubTypeBasedOnWholeVariant(myString1,
                                            myString2) != 'unknown-subtype':
        # Function getVariantSubTypeBasedOnWholeVariant
        # returns 'unknown-subtype' if it
        # doesn't detect a variant subtype
        myVariantSubType = getVariantSubTypeBasedOnWholeVariant(
            myString1, myString2)
    else:
        ''' If function getVariantSubTypeBasedOnWholeVariant doesn't detect
        a variant subtype, try detecting one based on diff:
        print('Diffs: «%s» -- Strings: «%s» / «%s»'   %
        (myDiff, myString1, myString1)  )'''
        myVariantSubType = getVariantSubTypeBasedOnDiff(
            myDiff, myString1, myString2)

    return({'r1': myDiff[0], 'r2': myDiff[1], 'subtype': myVariantSubType})
