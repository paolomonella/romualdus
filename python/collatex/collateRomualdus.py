#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module uses CollateX to collate witnesses, based on the tutorial in
    http://collatex.obdurodon.org/
    '''

import json,re,myconst
from lxml import etree
from collatex import *
from myconst import ns, tei_ns, xml_ns, html_ns 
from simplifyRomualdus import myWitness

#############################
# INPUT FILES AND VARIABLES #
#############################

debug = False

#afile = '../../xml/a_juxta.xml'
#afile = '../../xml/a.xml'
##afile = '../../xml/simplified/afoo_juxta.xml'
#afile = '../../xml/chronicon.xml'
#afile = '../../xml/ripostiglio/g-collation.xml' # g-collation.xml is just a shorter version of g.xml (otherwise it is identical)
afile = '../../xml/ripostiglio/g-collation5.xml' # see file xml/ripostiglio/version_history.txt
#bfile = '../../xml/bonetti_juxta.xml'
#bfile = '../../xml/g.xml'
#bfile = '../../xml/simplified/bfoo_juxta.xml'
##bfile = '../../xml/simplified/gfoo_juxta.xml'
#bfile = '../../xml/a.xml'
#bfile = '../../xml/ripostiglio/a-collation.xml' # a-collation.xml is just a shorter version of a.xml (otherwise it is identical)
bfile = '../../xml/ripostiglio/a-collation5.xml' # see file xml/ripostiglio/version_history.txt

aSiglum = afile.split('/')[-1].split('.')[0].upper()
bSiglum = bfile.split('/')[-1].split('.')[0].upper()


########
# XSLT #
########

addWMilestones = etree.XML("""
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="no" encoding="UTF-8" omit-xml-declaration="yes"/>
    <xsl:template match="*|@*">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="/*">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <!-- insert a <w/> milestone before the first word -->
            <w/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    <!-- convert <add>, <sic>, and <crease> to milestones (and leave them that way)
         CUSTOMIZE HERE: add other elements that may span multiple word tokens
    -->
    <xsl:template match="add | sic | crease | p">
        <xsl:element name="{name()}">
            <xsl:attribute name="n">start</xsl:attribute>
        </xsl:element>
        <xsl:apply-templates/>
        <xsl:element name="{name()}">
            <xsl:attribute name="n">end</xsl:attribute>
        </xsl:element>
    </xsl:template>
    <xsl:template match="note"/>
    <xsl:template match="text()">
        <xsl:call-template name="whiteSpace">
            <xsl:with-param name="input" select="translate(.,'&#x0a;',' ')"/>
        </xsl:call-template>
    </xsl:template>
    <xsl:template name="whiteSpace">
        <xsl:param name="input"/>
        <xsl:choose>
            <xsl:when test="not(contains($input, ' '))">
                <xsl:value-of select="$input"/>
            </xsl:when>
            <xsl:when test="starts-with($input,' ')">
                <xsl:call-template name="whiteSpace">
                    <xsl:with-param name="input" select="substring($input,2)"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="substring-before($input, ' ')"/>
                <w/>
                <xsl:call-template name="whiteSpace">
                    <xsl:with-param name="input" select="substring-after($input,' ')"/>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>

""")

transformAddW = etree.XSLT(addWMilestones)
                           
xsltWrapW = etree.XML('''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" indent="no" omit-xml-declaration="yes"/>
    <xsl:template match="/*">
        <xsl:copy>
            <xsl:apply-templates select="w"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="w">
        <!-- faking <xsl:for-each-group> as well as the "<<" and except" operators -->
        <xsl:variable name="tooFar" select="following-sibling::w[1] | following-sibling::w[1]/following::node()"/>
        <w>
            <xsl:copy-of select="following-sibling::node()[count(. | $tooFar) != count($tooFar)]"/>
        </w>
    </xsl:template>
</xsl:stylesheet>
''')

transformWrapW = etree.XSLT(xsltWrapW)


#########################################
# Functions to be used in class methods #
#########################################


def XMLtoJSON(id,XMLInput):
    ''' Function to convert the word-tokenized witness line into JSON '''
    unwrapRegex = re.compile('<w>(.*)</w>')
    stripTagsRegex = re.compile('<.*?>')
    words = XMLInput.xpath('//w')
    if debug:
        for w in words:
            print('Text:', w.text)
            print('Tail:', w.tail)
            print('Itertext:')
            for x in w.itertext():
                print(x)
            print()
    witness = {}
    witness['id'] = id
    witness['tokens'] = []
    for word in words:
        newText = ''
        for chunk in word.itertext():   # Get the new text for word element
            newText = newText + chunk
        for child in word:
            word.remove(child)  # Empty the word element from all its children elements (e.g. <pb>, <lb>)
        word.text = newText     # Replace the text of the word element with the new text
        wordToString = etree.tostring(word,encoding='unicode')
        wordToString = wordToString.replace('xmlns=""', '')
        wordToString = wordToString.replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', '')
        wordToString = wordToString.replace(' ', '')
        if debug:
            print('\nMy word: ', '«' + wordToString + '»')    # debug
            print('My word\'s text: ', word.text)   # debug
            print('Regex: ', unwrapRegex)   # debug
            print('Il match è:',  unwrapRegex.match(etree.tostring(word,encoding='unicode'))  )
        #unwrapped = unwrapRegex.match(etree.tostring(word,encoding='unicode')).group(1)    # original
        unwrapped = unwrapRegex.match(wordToString).group(1)
        if debug:
            print('Unwrapped:', unwrapped)
        token = {}
        token['t'] = unwrapped
        token['n'] = stripTagsRegex.sub('',unwrapped.lower())
        witness['tokens'].append(token)
    return witness

def getVariantType(myDiff1, myDiff2):
    ''' Input two strings constituting the differences b/w two strings
        and evaluate the type of type of variant. '''
    if sorted([myDiff1, myDiff2]) == sorted(['ae', 'e']): # sorted() makes the order of diffs in the MSS irrelevant
        myType = 'aeType'
    elif sorted([myDiff1, myDiff2]) == sorted(['i', 'y']):
        myType = 'yType'
    elif sorted([myDiff1, myDiff2]) == sorted(['u', 'v']):
        myType = 'uvType'
    elif sorted([myDiff1, myDiff2]) == sorted(['U', 'V']):
        myType = 'uvType'
    elif sorted([myDiff1, myDiff2]) == sorted(['i', 'j']):
        myType = 'jType'
    else:
        myType = 'unknown'
    return(myType)


def compareStrings(myString1, myString2):
    ''' Compare two strings and return the differences. Example: "perfert" vs "profert"
        This function returns a dictionary (whose values are all strings):
            "r1" = the variant characters in myString1 ("pre")
            "r2" = the variant characters in myString2 ("pro")
            "type" is the type of variant (a string: e.g. "uvType", "jType" etc.)
        This function uses getVariantType() to assess the variant type.
        Source:
        https://stackoverflow.com/questions/30683463/comparing-two-strings-and-returning-the-difference-python-3#30683513
    '''
    #then creating a new variable to store the result after
    #comparing the strings. You note that I added result2 because
    #if string 2 is longer than string 1 then you have extra characters
    #in result 2, if string 1 is  longer then the result you want to take
    #a look at is result 2

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

    return({'r1': result1, 'r2': result2, 'type': getVariantType(result1, result2)})


def collateElements(xmlElementA, xmlElementB, myOutputType='json'):
    ''' Apply transformations to the content of two XML elements.
        Choose myOutputType='json' (default) or 'table'.
        '''

    ATokenized = transformWrapW(transformAddW(xmlElementA))
    BTokenized = transformWrapW(transformAddW(xmlElementB))

    #print('Tokenized element of witness A:', ATokenized, end='\n\n')  # debug
    #print('Tokenized element of witness B:', BTokenized, end='\n\n')  # debug


    # Use the function to create JSON input for CollateX, and examine it

    json_input = {}
    json_input['witnesses'] = []
    json_input['witnesses'].append(XMLtoJSON('A',ATokenized))
    json_input['witnesses'].append(XMLtoJSON('B',BTokenized))

    # Collate the witnesses and view the output as JSON, in a table, and as colored HTML

    # As JSON:
    #collationJSON = collate_pretokenized_json(json_input,output='json') # Probably this function no longer exists
    collationJSON = collate(json_input,output='json')
    #print(collationJSON)   # debug

    # In a table:
    # collationText = collate_pretokenized_json(json_input,output='table',layout='vertical')
    collationText = collate(json_input,output='table',layout='vertical')
    #print(collationText)   # debug

    # As colored HTML:
    # collationHtml = collate(json_input,output='html') # I'm not sure about this line
    #print(collationHtml)  # debug. Strange output

    # Probably outdated code:
    #collationHTML2 = collate_pretokenized_json(json_input,output='html2') # Probably this function no longer exists
    #collationHTML2 = collate(json_input,output='html2') # Probably this function no longer exists

    if myOutputType == 'json':
        myCollationOutput = collationJSON
    elif myOutputType == 'table':
        myCollationOutput = collationText

    return myCollationOutput


######################################
# Functions for output visualization # 
######################################

def jsonCollationsList(aParagraphList, bParagraphList):
    ''' Collate each paragraph in A with corresp. par. in B. Return a list.
        Each element of list jasonOutputList has the (JSON-formatted) output of the collation of two
        corresponding paragraphs (one from file A, the other from file B).
        '''
    jasonOutputList = []
    for par in aParagraphList:
        print('Collating pagragraph ' + par.get('{%s}id' % ('http://www.w3.org/XML/1998/namespace')))  # debug
        pi = aParagraphList.index(par)   # Get the index, so it can use the same index for A and B in next line
        jasonOutputList.append(collateElements(aParagraphList[pi], bParagraphList[pi]))
    #print(jasonOutputList) #debug
    return jasonOutputList

def visualizeVariantsInBrackets(jasonOutputList, onlyOutputVariants = False):
    ''' Print to screen each word of the original text if there is no variant.
        If a word has two variants, show this in brackets:
        - the two variants with the siglum of their witness
        - the variant characters
        - the variant type.
        If onlyOutputVariants = True, only output places in which there are differences

        '''
    
    for jout in jasonOutputList:
        j = json.loads(jout)
        #print(json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))  )    # debug

        cola = j['table'][0]    # Column of witness A
        colb = j['table'][1]    # Column of witness B

        for row in cola:
            ci = cola.index(row)

            rowMsA = cola[ci]   # = row
            rowMsB = colb[ci]

            if debug:
                print("rowMsA:", rowMsA)
                print("rowMsB:", rowMsB)

            missingA, missingB = False, False
            if rowMsA is None       and rowMsB is not None:
                #print('\n«%s» only present in %s, missing in %s\n' % (rowMsB, bSiglum, aSiglum) )
                missingA = True
            elif rowMsA is not None   and rowMsB is None:
                #print('\n«%s» only present in %s, missing in %s\n' % (rowMsA, aSiglum, bSiglum) )
                missingB = True
            elif rowMsA is None     and rowMsB is None:
                print('\nStrange case\n')

            missingStr = '[[[[MISSING]]]]'

            if not (missingA or missingB):
                for word in row:
                    wi = row.index(word)
                    wordMsA = rowMsA[wi] # = word
                    wordMsB = rowMsB[wi]
                    if wordMsA['n'] == wordMsB['n']:
                        '''Previous line: if normalized ('n') forms of
                            corresponding words in MS A and MS B are the same'''
                        if not onlyOutputVariants:
                            print(wordMsA['t'], end = ' ')  # Print the non-normalized ('t') form only once
                    else:
                        myDiff = compareStrings(wordMsA['t'], wordMsB['t'])

                        if myDiff['type'] is 'unknown':
                            typeDeclaration = ''
                        else:
                            typeDeclaration = ' type="' + myDiff['type'] + '"'

                        print('\n\n <app' + 
                                ' ana="' + myDiff['r1'] + '/' + myDiff['r2'] + '"' +
                                typeDeclaration + '>' +
                                '<rdg wit="' + aSiglum + '>' + wordMsA['t'] + '</rdg>' + 
                                '<rdg wit="' + bSiglum + '">' + wordMsB['t'] + '</rdg>' +
                                '</app> \n\n',
                                end = '')

            elif missingA:
                for word in colb[ci]:   # colb[ci] corresponds to cola[ci] (which is row)
                    wi = colb[ci].index(word)
                    wordMsA = missingStr # = word
                    wordMsB = rowMsB[wi]
                    print('\n\n <app type="missing">' +
                            '<rdg wit="' + aSiglum + '"/>' +
                            '<rdg wit="' + bSiglum + '">' + wordMsB['t'] + '</rdg>' +
                            '</app> \n\n', end = '')
            elif missingB:
                for word in row:
                    wi = row.index(word)
                    wordMsA = rowMsA[wi] # = word
                    wordMsB = missingStr
                    print('\n\n <app type="missing">' +
                            '<rdg wit="' + aSiglum + '">' + wordMsA['t'] + '</rdg>' +
                            '<rdg wit="' + bSiglum + '"/>' +
                            '</app> \n\n', end = '')
            
            
##################
# Define classes #
##################


class elementCollation:
    '''Collation between two XML elements belonging each to a different witness.
        The two arguments aElem and bElem are TEI XML elements (e.g. a <p>).
        '''
    def __init__(self, xmlElementA, xmlElementB):

        # Prepare elements for collation with collatex
        ATokenized = transformWrapW(transformAddW(xmlElementA))
        BTokenized = transformWrapW(transformAddW(xmlElementB))
        #print('Tokenized element of witness A:', ATokenized, end='\n\n')  # debug
        #print('Tokenized element of witness B:', BTokenized, end='\n\n')  # debug

        # Use the function to create JSON input for CollateX, and examine it
        json_input = {}
        json_input['witnesses'] = []
        json_input['witnesses'].append(XMLtoJSON('A',ATokenized))
        json_input['witnesses'].append(XMLtoJSON('B',BTokenized))

    def jsonOutput():
        ''' Collate the witnesses and return the output as JSON '''
        #collationJSON = collate_pretokenized_json(json_input,output='json') # Probably this function no longer exists
        return collate(json_input,output='json')

    def jsonOutput():
        ''' Collate the witnesses and return the output as a table '''
        # collationText = collate_pretokenized_json(json_input,output='table',layout='vertical')
        return collate(json_input,output='table',layout='vertical')


###################################
# Instantiate classes and collate #
###################################


a = myWitness(afile, teiHasXmlns = True)
b = myWitness(bfile, teiHasXmlns = True)

visualizeVariantsInBrackets(
    jsonCollationsList( a.paragraphs(), b.paragraphs() ),
    onlyOutputVariants = False)