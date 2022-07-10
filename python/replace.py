#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import re
from string import punctuation

from other import metatext


def myReplaceAll(myGraph, myAlpha, myElement, wholeWord=False):
    ''' If wholeWord=False (default), this function replaces the simple string
        myGraph (e.g.: "q9") with the simple string myAlpha (e.g.: "que")
        in all text and tail strings of all children of element myElement.
        If wholeWord=True, it applies the substitution only to abbreviations
        that occupy an entire word (e.d.: "qd-" = "quod", but only if it is
        a whole word).
        In the ToS such cases are represented in the "grapheme" cells in the
        format "<qd->", where "<" and ">" represent word boundaries and
        the chars in the middle ("qd-") represent the abbreviation.
        '''
    if wholeWord:
        if myGraph[-1] in [p for p in punctuation]:
            myGraph = r'\b%s\b%s\B' % (myGraph[:-1], myGraph[-1])
            # Result is like   r'\bqd\b-\B'. Man, this was hard to code!
            # This 'if' block is necessary b/c "\bqd-\b"
            # does not match " qd- ", since "-" is a regex word-delimiter
            # If I'll use abbrev. marks that are word-delimiters,
            # I'll have to add them to this list. But as of now
            # I'm choosing to make things easier and only use
            # abbrev. marks that are no regex word-delimiters.
        else:
            myGraph = r'\b%s\b' % myGraph
    for e in myElement.findall('.//*'):
        if e.text and re.search(myGraph, e.text) and not metatext(e):
            e.text = re.sub(myGraph, myAlpha, e.text)
        if e.tail and re.search(myGraph, e.tail):
            e.tail = re.sub(myGraph, myAlpha, e.tail)


def genericBaseReplaceAll(myRow, myElement):
    ''' This applies to ToS 'grapheme' cells in the format '[aeiouy]3', where
        the brackets include
        a set of characters (e.g. any vowel). This function replaces
        the grapheme after the brackets (e.g.: '3')
        with its alphabetic expansion of one or more chars
        (e.g.: 'm', so 'homine3' becomes 'hominem')
        in all text and tail strings of all children of element myElement.
        '''
    firstcellmatch = re.match('(\[.*\])(.)',   myRow[0])
    myGenericBase = firstcellmatch.group(1)  # group(1) is like "[aeiouy]"
    myAbbrMark = firstcellmatch.group(2)
    # group(2) is like "3" (the abbreviation mark). It includes one char only
    secondcellmatch = re.match('\[.*\](.+)',   myRow[1])
    myExpansion = secondcellmatch.group(1)
    # group(1) is like "m" (the alphabetic expansion: "u3" becomes "um")
    for e in myElement.findall('.//*'):
        if e.text and re.match('.*' + myGenericBase + myAbbrMark + '.*', e.text) and not metatext(e):
            gmatch = re.match('.*(' + myGenericBase + ')(' + myAbbrMark + ').*', e.text)
            e.text = re.sub(gmatch.group(2), myExpansion, e.text)
        if e.tail and re.match('.*' + myGenericBase + myAbbrMark + '.*', e.tail):
            gmatch = re.match('.*(' + myGenericBase + ')(' + myAbbrMark + ').*', e.tail)
            e.tail = re.sub(gmatch.group(2), myExpansion, e.tail)
