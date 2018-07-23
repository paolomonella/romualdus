#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
example2.py

Author: David J. Birnbaum (djbpitt@gmail.com; http://www.obdurodon.org)
Acknowledgements: Revised with the help of Ronald Dekker
First version: 2015-06-25
Collates TEI input <l> elements with token-internal markup
Based on example1.py
"""

from collatex import *
from lxml import etree
import re, json, string


class Witness:
    """An instance of Witness is the etree representation of a witness"""
    def __init__(self,xml):
        self.xml = etree.XML(xml)

    def ids(self):
        return [int(i) for i in self.xml.xpath('//@id')]

    def minId(self):
        return min(self.ids())

    def maxId(self):
        return max(self.ids())

    def lById(self,id):
        """word-tokenized <l> of a witness by @id

        not called directly; used by words(), below
        """
        self.id = str(id)
        line = Line(self.xml,self.id)
        return line.tokenized()

    def words(self,id):
        """word tokens with <w> wrappers removed"""
        self.id = str(id)
        wrappedWords = self.lById(self.id).xpath('//w')
        for w in wrappedWords:
            yield Word(w)

    def siglum(self):
        # xpath() returns a list, even if there's just one object
        return str(self.xml.xpath('//lg/@wit')[0])

    def generate_tokens(self, lineId):
        words = self.words(lineId)
        currentTokens = []
        for word in words:
            wordToken = {}
            wordToken['t'] = word.unwrap()
            wordToken['n'] = word.normalizeToken()
            currentTokens.append(wordToken)
        return currentTokens


class Line:
    """An instance of Line is an <l> in a witness with a specified @id"""
    # The two XSLT transformations are class properties
    # The first replaces whitespace in the input with <w/> milestone tags
    # The second transforms the milestones to wrappers
    xsltAddW = etree.XML('''
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
        <xsl:template match="add | sic | crease ">
            <xsl:element name="{name()}">
                <xsl:attribute name="n">start</xsl:attribute>
            </xsl:element>
            <xsl:apply-templates/>
            <xsl:element name="{name()}">
                <xsl:attribute name="n">end</xsl:attribute>
            </xsl:element>
        </xsl:template>
        <xsl:template match="text()">
            <xsl:call-template name="whiteSpace">
                <xsl:with-param name="input" select="translate(.,'&amp;#x0a;',' ')"/>
            </xsl:call-template>
        </xsl:template>
        <xsl:template name="whiteSpace">
            <xsl:param name="input"/>
            <xsl:choose>
                <xsl:when test="not(contains($input, ' '))">
                    <xsl:value-of select="$input"/>
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
    ''')
    transformAddW = etree.XSLT(xsltAddW)

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

    def __init__(self,witness,id):
        self.witness = witness
        self.id = id

    def fullLine(self):
        # xpath() returns a list, even if there's just one object
        return self.witness.xpath('//l[@id =' + self.id + ']')[0]

    def lineString(self):
        # lineString() is for diagnosis, and is not used in production
        return etree.tostring(self.fullLine(), encoding='unicode')

    def tokenized(self):
        self.withMilestones = Line.transformAddW(self.fullLine())
        self.withWrappers = Line.transformWrapW(self.withMilestones)
        return self.withWrappers


class Word:
    """An instance of Word is a word token in a line"""
    unwrapRegex = re.compile('<.*?>\s*(.*)\s*</.*?>')
    puncRegex = re.compile('[' + string.punctuation + ']+')
    tagRegex = re.compile('<.*?>')
    def __init__(self,w):
        self.w = w
        self.stringified = etree.tostring(self.w,encoding='unicode')

    def unwrap(self):
        """Remove <w> tags from around word token"""
        return Word.unwrapRegex.match(self.stringified).group(1)

    def normalizeToken(self):
        """Create shadow 'n' property"""
        return Word.tagRegex.sub('',Word.tagRegex.sub('',self.stringified.lower()))


class WitnessSet:
    """An instance of WitnessSet is the set of witnesses being collated

    In these examples, the witnesses are individual <l> elements, not entire mss
    """

    def __init__(self, witnesses):
        self.witnesses = witnesses

    def get_line_ids(self):
        witnessMin = min([witness.minId() for witness in self.witnesses])
        witnessMax = max([witness.maxId() for witness in self.witnesses])
        return range(witnessMin,witnessMax + 1)

    def generate_block(self, lineId):
        block = {}
        witnesses = []
        for witness in self.witnesses:
            currentWitness = {}
            currentWitness['id'] = witness.siglum()
            currentWitness['tokens'] = witness.generate_tokens(lineId)
            witnesses.append(currentWitness)
        block['witnesses'] = witnesses
        return block

    def generate_blocks_by_line(self):
        for lineId in self.get_line_ids():
            block = self.generate_block(lineId)
            yield block

def main():
    witnessA = """
    <lg wit="A">
        <l id="8" n="8">Ki maint <abbrev>et</abbrev> el pere et el fis</l>
        <l id="9" n="9">Ki ma doune soie merci</l>
    </lg>
    """
    witnessB = """
    <lg wit="B">
        <l id="8" n="8">Q<abbrev>ui</abbrev> mai<abbrev>n</abbrev>t <abbrev>et</abbrev> el pere <abbrev>et</abbrev> el fis</l>
        <l id="9" n="9">Q<abbrev>ui</abbrev> ma done soie merci</l>
    </lg>
    """
    # get the numeric range of @id values as witnessMin and witnessMax
    witnessATree = Witness(witnessA)
    witnessBTree = Witness(witnessB)
    witnessSet = WitnessSet([witnessATree, witnessBTree])

    # treat each <l> (by @id) as a separate collation block
    for block in witnessSet.generate_blocks_by_line():
        # Uncomment the following line to see the JSON input to CollateX
        # print(json.dumps(block,indent=2))
        collation = collate_pretokenized_json(block)
        print(collation)

if __name__ == "__main__": main()
