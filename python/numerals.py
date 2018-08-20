#!/usr/bin/python3.6
# -*- coding: utf-8 -*-



import constants
from lxml import etree
import roman
import re

siglum = 'foo' # XML filename to parse ('a' for 'a.xml'; 'bonetti' for 'bonetti.xml')

def getRomanContent(num, checkallnumbers=True, debug=False):
    ''' Return the roman content (e.g. XIII, CCXVI) of <num> elements.
        Ignore <orig> and only include <reg>.
        If checkallnumbers=False, only work on <num>s not having a @value attribute (legacy feature, but it's safer
        not to modify it now, since I don't remember why I had put this option in the function).
    '''
    r = ''
    n = constants.ns
    if checkallnumbers or num.get('value') is None:
        if num.find('.//t:choice', n) is not None:  # If <num> has <choice>/<reg>+<orig> inside (e.g. IIJ/iii or VI/ui)
            if num.find('.//t:choice', n).find('.//t:reg', n) is not None:
                if num.text is not None:
                    directtext = num.text
                    r = r + directtext
                choices = num.findall('.//t:choice', n)
                for c in choices:
                    reg = c.find('.//t:reg', n)
                    # for x in reg:
                        # print(x)  # debug
                    r = r + reg.text
                    try:
                        r = r + c.tail
                    except:
                        pass
        else:   # Not needing normalization
            if len(num) > 0 and debug:
                print('Occhio: l\'elemento', num, ' con contenuto', \
                        num.text, 'ha elementi figli che mi disturbano. I suoi figli sono:')
                for x in num:
                     print(x)  # debug
                print('La sua coda è: ', num.tail, '\n\n')
            else:
                r = num.text # Better way, but an overkill here: r = ''.join(num.itertext()).replace('\n', '')
        if r == '' and debug:
            print('L\'elemento <num> con coda ', num.tail, ' non ha contenuto:', r)
    return(r)

def setValues(siglum):
    ''' Take Roman numerals in the text (already marked up with <num>)
        and insert a @value attribute with its arabic value.
        The 'siglum' is the XML filename to parse ('a' for 'a.xml'; 'bonetti' for 'bonetti.xml' etc.).
        Then write the modified tree to another XML file ('numerals-a.xml'; 'numerals-bonetti.xml' etc.).
        '''
    n = constants.ns
    tree = etree.parse('../xml/%s.xml' % siglum)
    numbers = tree.findall('.//t:num', n)
    for number in numbers:
        if number.get('value') is None:
            content = getRomanContent(number, checkallnumbers=False)
            if content == '':
                print('foo', number.text)
            # print(content.upper(), end='\t')  # debug
            try:
                myvalue = roman.fromRoman(content.upper())
                #print(roman.fromRoman(content.upper()))    # debug
                number.set('value', str(myvalue))
                number.set('type', 'guessedvalue')
            except roman.InvalidRomanNumeralError:
                print('Numero romano non parsabile:', content.upper())
                number.set('type', 'foo')
        else:
            #print('Il valore di @value era già settato a', number.get('value'))
            pass

    tree.write('../xml/numerals-%s.xml' % (siglum), encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)

def checkNumerals(siglum):
    tree = etree.parse('../xml/%s.xml' % siglum)
    numbers = tree.findall('.//t:num', constants.ns)
    rd = {'VIIII': 'IX', 'IIII': 'IV', 'LXXXX': 'XC', 'XXXX': 'XL', 'DCCCC': 'CM', 'CCCC': 'CD'}
    for n in numbers:
        if n.get('value') is None:  # <num>s with no @value attribute
            print(n, 'has no @value attribute')
        else:
            c = getRomanContent(n)
            c = c.replace('j', 'i').upper()
            if len(c) > 0:
                xa = int(n.get('value'))
                for r in rd: # Do the usual normalizations (IIII → IV etc.)
                    c = c.replace(r, rd[r])
                if c.startswith('IIID') or c.startswith('IIIC'):    # Normalization for initial thousands
                    c = c.replace('IIID', 'MMMD').replace('IIIC', 'MMMC')

                try:
                    pa = roman.fromRoman(c)
                    if pa != xa and len(n) == 0:    # If @value does *not* correspond with the Arabic value calculated
                                                    # by the script and <num> has no 'desturbing' children elements
                        print('%5s %3d %20s %3d' % ('XML:', xa, 'Python:', pa))
                except roman.InvalidRomanNumeralError:
                    if len(n) > 0:    
                        print('Invalid numeral with children:', c)
                    else:
                        print('Invalid numeral:', c, 'with value:', xa, 'and tail: «' + n.tail + '»')



def wrapNumerals(siglum, maxnum):
    ''' Identify Roman numerals in the text and wrap them with <num></num>, without setting their @value, based
        on text files in the 'romanranges' folder. I had previously generated those text files
        with the 'roman' Python module. The 'romanranges/univocal.txt' file has each Roman numeral, in its different
        spellings (IV, IIII, IIIJ), taken one time only, from 1 to 4999, associated to its Arabic equivalent (4).
        Roman numerals with one letter only (I, V, X, L, C, D, M) are not in the file.
        Argument 'maxnum' is the maximum number to be imported from file univocal.txt
        '''
    # Create dictionary of correspondences, taken from univocal.txt (only numbers until 1300)
    # I'll take care of numbers higher than 1300 manually later
    with open('romanranges/univocal.txt', 'r') as IND:
        C = [line.strip().split('-') for line in IND]
        #D = {c[1]: c[0] for c in C if int(c[0])}    # Import all numerals until 4999
        #D = {c[1]: c[0] for c in C if int(c[0]) < 1301} # Import only numerals until 1300
        D = {c[1]: c[0] for c in C if int(c[0]) < int(maxnum)} # Import only numerals until manxum
        print('I imported a dictionary of ', str(len(D)), 'Roman numeral spellings')

    with open('../xml/%s.xml' % siglum, 'r') as INX:
        with open('../xml/wrappednumerals-%s.xml' % siglum, 'w') as OUT:
            c = 0
            for l in INX:
                c = c + 1

                for d in D:

                    if d in ['ID', 'II', 'VI', 'LI', 'DI', 'DII', 'MI', 'IL', 'VIX', 'CVI', 'DIV']:
                        patt = re.compile(r'\b'+d+r'\b')    # In these cases, do a case-sensitive search
                    else:
                        patt = re.compile(r'\b'+d+r'\b', re.IGNORECASE) # Otherwise, case-insensitive

                    if re.search(patt, l):
                        print('Line %d of 6331: found %s.' % (c, d))
                        print('Prima:\n' + l)
                        l = re.sub(patt,   '<num value="' + D[d] + '">' + d.lower() + '</num>', l)
                        print('Dopo:\n' + l + '\n\n')
                print(l, end='', file=OUT)
