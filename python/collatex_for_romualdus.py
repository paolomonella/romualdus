#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module uses CollateX to collate witnesses, based on the tutorial in
    http://collatex.obdurodon.org/
    '''

import json,re,myconst,roman
from lxml import etree
from collatex import *
from myconst import ns, tei_ns, xml_ns, html_ns 
from variant_type import variantComparison
#from itertools import combinations
#from simplify_romualdus_for_collatex import myWitness

#############################
# INPUT FILES AND VARIABLES #
#############################

debug = False

#afile = '../../xml/a_juxta.xml'
#afile = '../../xml/a.xml'
##afile = '../../xml/simplified/afoo_juxta.xml'
#afile = '../../xml/chronicon.xml'
#afile = '../../xml/ripostiglio/g-collation.xml' # g-collation.xml is just a shorter version of g.xml (otherwise it is identical)
afile = '../xml/gs-short.xml'
#bfile = '../../xml/bonetti_juxta.xml'
#bfile = '../../xml/g.xml'
#bfile = '../../xml/simplified/bfoo_juxta.xml'
##bfile = '../../xml/simplified/gfoo_juxta.xml'
#bfile = '../../xml/a.xml'
#bfile = '../../xml/ripostiglio/a-collation.xml' # a-collation.xml is just a shorter version of a.xml (otherwise it is identical)
bfile = '../xml/a1s-short.xml'

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
        Each element of list jsonOutputList has the (JSON-formatted) output of the collation of two
        corresponding paragraphs (one from file A, the other from file B).
        '''
        # § To-do: If paragraph does not exist (= is empty, no text and no children) in one witness, don't collate but return a message
    jsonOutputList = []
    for par in aParagraphList:
        print('Collating pagragraph ' + par.get('{%s}id' % ('http://www.w3.org/XML/1998/namespace')))  # debug
        pi = aParagraphList.index(par)   # Get the index, so it can use the same index for A and B in next line
        jsonOutputList.append(collateElements(aParagraphList[pi], bParagraphList[pi]))
    #print(jsonOutputList) #debug
    return jsonOutputList

def visualizeVariantsInBrackets(jsonOutputList, onlyOutputVariants = False):
    ''' Print to screen each word of the original text if there is no variant.
        If a word has two variants, show this in brackets:
        - the two variants with the siglum of their witness
        - the variant characters
        - the variant type.
        If onlyOutputVariants = True, only output places in which there are differences

        '''
        # § To-do: rimuovi file name suffix (_simplified o simili; è in una variabile in myconst) dalla vers. in maiuscolo
    
    for jout in jsonOutputList:
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
                        myComparison = variantComparison(wordMsA['t'], wordMsB['t'])

                        if myComparison['type'] is 'unknown':
                            typeDeclaration = ''
                        else:
                            typeDeclaration = ' type="' + myComparison['type'] + '"'

                        print('\n\n <app' + 
                                ' ana="' + myComparison['r1'] + '/' + myComparison['r2'] + '"' +
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


####################################
# Extract paragraphs from XML file #
####################################

def strip_ns_prefix(myTree):
    # Source: https://stackoverflow.com/questions/30232031/how-can-i-strip-namespaces-out-of-an-lxml-tree#30233635
    # Iterate through only element nodes (skip comment node, text node, etc) :
    for element in myTree.xpath('descendant-or-self::*'):
        # If element has prefix...
        if element.prefix:
            # Replace element name with its local name
            element.tag = etree.QName(element).localname
    return myTree

class myWitness:
    ''' A witness xmlfile is the TEI XML file with the witness transcription (relative path).
        I took this class from script simplify_romualdus_for_collatex.py, which I am no longer using
        (I am using simplify_markup_for_collation.py instead, to simplify the markup).
        '''

    def __init__(self, xmlfile, teiHasXmlns = False):
        self.teiHasXmlns = teiHasXmlns
        # Source of next line: https://stackoverflow.com/questions/14731633/
        # how-to-resolve-external-entities-with-xml-etree-like-lxml-etree#19400397
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        self.tree = etree.parse(xmlfile, parser=parser)
        #strip_ns_prefix(self.tree)
    
    def body(self):
        ''' Find the <body> element of the XML tree of the witness '''
        if self.teiHasXmlns:
            # If <TEI> *has* @xmlns: <TEI xmlns="http://www.tei-c.org/ns/1.0">
            myBody = self.tree.find('.//t:body', ns)
        else:
            # If <TEI> does *not* have @xmlns: <TEI>
            myBody = self.tree.find('.//body')
        return myBody

    def paragraphs(self):
        ''' Create a list of <p> elements in the <body> of the witness '''
        myBody = self.body()
        if self.teiHasXmlns:
            myParagraphs = self.body().findall('.//t:p', ns)  # This is a list of lxml elements
        else:
            myParagraphs = self.body().findall('.//p')  # This is a list of lxml elements
        for p in myParagraphs:
            if p.text and p.text[-1:] == '\n':
                p.text = p.text[:-1]    # Remove the final linebreak because it breaks collateX (for some reason)
                #print(p.get('{%s}id' % ('http://www.w3.org/XML/1998/namespace')))  # debug
        return myParagraphs

###################################
# Instantiate classes and collate #
###################################


a = myWitness(afile, teiHasXmlns = True)
b = myWitness(bfile, teiHasXmlns = True)

visualizeVariantsInBrackets(
    jsonCollationsList( a.paragraphs(), b.paragraphs() ),
    onlyOutputVariants = False)
