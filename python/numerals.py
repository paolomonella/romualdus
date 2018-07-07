#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


''' Take Roman numerals in the text (encoded with <num>)
    and insert a @value attribute with its arabic value
    '''

#import re
#import time
import constants
from lxml import etree
import roman

siglum = 'g' # XML filename to parse ('a' for 'a.xml'; 'bonetti' for 'bonetti.xml')

def romanContent(num):
    r = ''
    if num.get('value') is None:
        if num.find('.//t:choice', n) is not None:
            #if num.find('.//t:choice', n).find('.//t:reg[@type="numeral"]', n) is not None:
            if num.find('.//t:choice', n).find('.//t:reg', n) is not None:
                if num.text is not None:
                    directtext = num.text
                    r = r + directtext
                choices = num.findall('.//t:choice', n)
                for c in choices:
                    #reg = c.find('.//t:reg[@type="numeral"]', n)
                    reg = c.find('.//t:reg', n)
                    # for x in reg:
                        # print(x)  # debug
                    r = r + reg.text
                    try:
                        r = r + c.tail
                    except:
                        pass
        else:   # Not needing normalization
            if len(num) > 0:
                print('Occhio: l\'elemento', num, ' con contenuto', \
                        num.text, 'ha elementi figli che mi disturbano. I suoi figli sono:')
                #for x in num:
                    # print(x)  # debug
            else:
                r = num.text
        if r == '':
            print('L\'elemento non ha contenuto:', r)
    return(r)

n = constants.ns
tree = etree.parse('../xml/%s.xml' % siglum)
#numbers = tree.findall('.//t:seg[@type="num"]', constants.ns)
numbers = tree.findall('.//t:num', n)
for number in numbers:
    if number.get('value') is None:
        content = romanContent(number)
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

