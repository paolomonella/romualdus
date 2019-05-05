#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module uses CollateX to collate witnesses, based on the tutorial in
    http://collatex.obdurodon.org/
    '''

from collatex import *
from lxml import etree
import json,re,myconst
from myconst import ns, tei_ns, xml_ns, html_ns 

# Mode

# mymode = 'wholebody'
mymode = 'paragraphs'

# Input files

#firstfile = '../xml/a_juxta.xml'
#firstfile = '../xml/a.xml'
firstfile = '../xml/juxtacommons/afoo_juxta.xml'
#secondfile = '../xml/bonetti_juxta.xml'
#secondfile = '../xml/g.xml'
secondfile = '../xml/juxtacommons/bfoo_juxta.xml'



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


####################
# Define functions #
####################

def XMLtoJSON(id,XMLInput):
    ''' Function to convert the word-tokenized witness line into JSON '''
    unwrapRegex = re.compile('<w>(.*)</w>')
    stripTagsRegex = re.compile('<.*?>')
    words = XMLInput.xpath('//w')
    witness = {}
    witness['id'] = id
    witness['tokens'] = []
    for word in words:
        unwrapped = unwrapRegex.match(etree.tostring(word,encoding='unicode')).group(1)
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

    #return collationJSON
    return myCollationOutput

def getVariantType(myDiff1, myDiff2):
    ''' Input two strings constituting the differences b/w two strings
        and evaluate the type of type of variant. '''
    if sorted([myDiff1, myDiff2]) == sorted(['ae', 'e']): # sorted() makes the order of diffs in the MSS irrelevant
        myType = 'aeType'
    elif sorted([myDiff1, myDiff2]) == sorted(['i', 'y']): # sorted() makes the order of diffs in the MSS irrelevant
        myType = 'yType'
    else:
        myType = 'unknown'
    return(myType)


def compareStrings(myString1, myString2):
    ''' Compare two strings and return the differences.
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

    #print out result
    #print ('Letters different in string 1: "' + result1 + '"')
    #print ('Letters different in string 2: "' + result2 + '"')

    return({'type': getVariantType(result1, result2), 'r1': result1, 'r2': result2})  # Return a dictionary


################################
# Parse file and identify body #
################################

ATree = etree.parse(firstfile)
#ATree = etree.XML('<l><abbrev>Et</abbrev>cil i partent seulement</l>')
#ATree = etree.parse('../xml/foo.xml')
BTree = etree.parse(secondfile)

teiHasXmlsn = False

if teiHasXmlsn == False:
    # If <TEI> does *not* have @xmlns: <TEI>
    ABody = ATree.find('.//body')
    BBody = BTree.find('.//body')
else:
    # If <TEI> *has* @xmlns: <TEI xmlns="http://www.tei-c.org/ns/1.0">
    ABody = ATree.find('.//t:body', ns)
    BBody = BTree.find('.//t:body', ns)

#print(ABody)    # debug
#print(BBody)    # debug


#jout = collateElements(ABody, BBody) # Collate whole <body> of each file



#############################################
# Create lists of <p> elements of each file #
#############################################

APars = ABody.findall('p')
BPars = BBody.findall('p')


##################################################
# Create list of collations b/w those paragraphs #
##################################################

JL = []
for par in APars:
    pi = APars.index(par)   # Get the index, so it can use the same index for A and B in next line
    JL.append(collateElements(APars[pi], BPars[pi]))    # Collate paragraph in A w/ corresp. par. in B
    # Each element of list JL has the (JSON-formatted) output of the collation of two
    # corresponding paragraphs (one from file A, the other from file B)


#############################
# Output text with variants # 
#############################

for jout in JL:
    j = json.loads(jout)
    #print(json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))  )

    cola = j['table'][0]    # Column of witness A
    colb = j['table'][1]    # Column of witness B

    for row in cola:
        ci = cola.index(row)

        # NEW CODE
        rowMsA = cola[ci]   # = row
        rowMsB = colb[ci]


        for word in row:
            wi = row.index(word)
            wordMsA = rowMsA[wi] # = word
            wordMsB = rowMsB[wi]
            if wordMsA['n'] == wordMsB['n']:
                '''Previous line: if normalized ('n') forms of
                    corresponding words in MS A and MS B are the same'''
                print(wordMsA['t'], end = ' ')  # Print the non-normalized ('t') form only once
            else:
                myDiff = compareStrings(wordMsA['t'], wordMsB['t'])

                if myDiff['type'] is 'unknown':
                    typeDeclaration = ''
                else:
                    typeDeclaration = '; Type: ' + myDiff['type']

                print('[A: ' + wordMsA['t'] +
                        '; B: ' + wordMsB['t'] +
                        '; Diff: ⸤' + myDiff['r1'] + '/' + myDiff['r2'] + '⸥' +
                        typeDeclaration +
                        #'; Type: ' + myDiff['type'] +
                        '] ', end = '')
        
        
        
        
        '''
        # OLD CODE

        #print('\n\nWitness A, row %d:' % (ci), end=' ')
        LA = [word['n'] for word in cola[ci]]   # This is a list
        ja = ' '.join(LA)  # The textual portion is transformed to a string (with spaces b/w words)

        #print('\nWitness B, row %d:' % (ci), end=' ')
        LB = [word['n'] for word in colb[ci]]   # This is a list
        jb = ' '.join(LB)  # The textual portion is transformed to a string (with spaces b/w words)


        if LA != LB:
            # I'm comparing the two lists of tokens (LA/LB) based on their normalized ('n')
            # form ('n', i.e. lowercase and w/o XML tags), but I'm then printing them out
            # based on their non-normalized ('t') form.
            LAt = [word['t'] for word in cola[ci]]   # 't': Not normalized-'n' tokens
            jat = ' '.join(LAt)  # The textual portion is transformed to a string (with spaces b/w words)
            LBt = [word['t'] for word in colb[ci]]   # 't': Not normalized-'n' tokens
            jbt = ' '.join(LBt)  # The textual portion is transformed to a string (with spaces b/w words)
            print(' [A: ' + jat + '; B: ' + jbt + '] ', end = '')
        else:
            print(ja, end = '') # ja = jb, so I'm printing it only once. No need to ask: print(ja); print(jb)
        '''
