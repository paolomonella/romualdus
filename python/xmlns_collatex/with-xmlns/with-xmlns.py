#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module uses CollateX to collate witnesses, based on the tutorial in
    http://collatex.obdurodon.org/
    '''

from collatex import *
from lxml import etree
import json, re

# XML/HTML namespaces
ns = {'t': 'http://www.tei-c.org/ns/1.0',               # for TEI XML
        'xml': 'http://www.w3.org/XML/1998/namespace',  # for attributes like xml:id
        'h': 'http://www.w3.org/1999/xhtml'}            # for (X)HTML output  

tei_ns  = "{%s}" % ns['t']
xml_ns  = "{%s}" % ns['xml']
html_ns = "{%s}" % ns['h']

# Input files

firstfile = 'afoo-with-xmlns.xml'
secondfile = 'bfoo-with-xmlns.xml'

# XSLT

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


# Apply transformations 

ATree = etree.parse(firstfile)
BTree = etree.parse(secondfile)

'''
# If <TEI> does *not* have @xmlns: <TEI>
ABody = ATree.find('.//body')
BBody = BTree.find('.//body')
'''
# If <TEI> *has* @xmlns: <TEI xmlns="http://www.tei-c.org/ns/1.0">
ABody = ATree.find('.//t:body', ns)
BBody = BTree.find('.//t:body', ns)

print('I found the following <body> elements (so the lxml find works):')
print(ABody)    # debug
print(BBody)    # debug


ATokenized = transformWrapW(transformAddW(ABody))
BTokenized = transformWrapW(transformAddW(BBody))

print('Tokenized:', ATokenized, end='\n\n')

'''
ATokenized = transformWrapW(transformAddW(ATree))
BTokenized = transformWrapW(transformAddW(BTree))
'''


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

# Use the function to create JSON input for CollateX, and examine it

json_input = {}
json_input['witnesses'] = []
json_input['witnesses'].append(XMLtoJSON('A',ATokenized))
json_input['witnesses'].append(XMLtoJSON('B',BTokenized))

# Collate the witnesses and view the output as JSON, in a table, and as colored HTML

#collationText = collate_pretokenized_json(json_input,output='table',layout='vertical')
collationText = collate(json_input,output='table',layout='vertical')
print(collationText)
#collationJSON = collate_pretokenized_json(json_input,output='json')
collationJSON = collate(json_input,output='json')
print(collationJSON)
#collationHTML2 = collate_pretokenized_json(json_input,output='html2')
collationHTML2 = collate(json_input,output='html2')
