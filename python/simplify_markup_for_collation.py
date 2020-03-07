#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module extracts/divides the layers from the TEI XML source file,
    thus generating files with simplified (or no) markup that can be fed
    to collation software such as Juxta or CollateX.
    It also includes other methods that help you to inspect what entities
    and elements are in the original XML file.
    See the documentation of the methods below for details.
    '''

import csv
import re
from collections import Counter
import operator
from lxml import etree

import myconst
from myconst import ns, tei_ns
from replace import myReplaceAll
from replace import genericBaseReplaceAll
'''
from other import metatext
from other import baretextize
'''


class msTree:

    def __init__(self, siglum):
        self.siglum = siglum
        self.xmlfile = '%s/%s.xml' % (myconst.xmlpath, siglum)
        # Source of next, commented, line:
        # https://stackoverflow.com/questions/14731633/
        # how-to-resolve-external-entities-with-xml-etree-like-lxml-etree#19400397
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        # parser = etree.XMLParser(resolve_entities=True)
        self.tree = etree.parse(self.xmlfile, parser=parser)
        self.root = self.tree.getroot()
        self.outputXmlFile = '%s%s%s.xml' % (myconst.simplifiedpath, siglum,
                                             myconst.simplifiedsuffix)

    def remove_comments(self):
        ''' Remove XML comments such as <!-- comment --> '''
        commentElements = self.tree.xpath('//comment()')
        for element in commentElements:
            if element.getparent() is not None:
                parent = element.getparent()
                parent.remove(element)
            else:
                print('The following comment is not in the root element so I \
                      can\'t delete it:\n\t' % (element), end='\n\n')

    def list_elements(self, onlybody=True, attributes=False):
        ''' Print a set of element names in the XML file '''
        els = []
        if onlybody:
            mybody = self.tree.find('.//t:body', ns)
            allelements = mybody.iter()
        else:
            allelements = self.tree.iter()
        for element in allelements:
            if etree.iselement:
                tag = element.tag
                # print(element.tag.split('}')[1])
                els.append(element.tag.split('}')[1])
        elset = set(els)
        print(set(els))
        for tag in elset:
            A = {}
            print('\n\n<' + tag + '>: ')
            if onlybody:
                E = mybody.findall('.//t:%s' % (tag), ns)
            else:
                E = self.tree.findall('.//t:%s' % (tag), ns)
            for e in E:
                for attr in e.attrib:
                    val = e.get(attr)
                    if attr not in A:
                        A[attr] = [val]
                    else:
                        A[attr].append(val)
            # print(A, end='')
            for a in A:
                if len(set(A[a])) > 5:
                    print('\t' + a + '=', set(A[a][:3]), '(etc.)')
                else:
                    print('\t' + a + '=', set(A[a]))

    def list_and_count_elements(self, onlybody=True, attributes=False):
        ''' Print a set of element names in the XML file and count them'''
        els = []
        if onlybody:
            mybody = self.tree.find('.//t:body', ns)
            allelements = mybody.iter()
        else:
            allelements = self.tree.iter()
        for element in allelements:
            if etree.iselement(element):
                try:
                    els.append(element.tag.split('}')[1])
                except Exception as e:
                    els.append(element.tag)
        elcount = Counter(els)
        sorted_elcount = sorted(elcount.items(), key=operator.itemgetter(1))
        print('\n', 'Witness:', self.siglum)
        for e in sorted_elcount:
            print(e)
            # print(sorted_elcount[0], sorted_elcount[1])

    def list_entities(self):
        for entity in self.tree.docinfo.internalDTD.iterentities():
            msg_fmt = "{entity.name!r}, {entity.content!r}, {entity.orig!r}"
            print(msg_fmt.format(entity=entity))

    def choose(self, parenttag, keeptag, keeptype, removetag):
        ''' Keep all elements with tag name 'keeptag' and remove those with
            name 'removetag' in structures such as
            '<choice><orig>j</orig><reg type="j">i</reg></choice>'
            or
            <choice><sic>dimicarum</sic>
            <corr type="typo">dimicarunt</corr></choice>
            In the examples above, "parenttag" is "choice"i
            (it may be something else, such as "app" or "subst").
            Note that the element to keep (<reg> or <corr>) always has a @type,
            whose value goes to argument "keeptype".
            '''
        # If no @type value is provided when calling the method
        if keeptype == '':
            myElements = self.tree.findall('.//t:%s' % (keeptag), myconst.ns)
        # If a @type value is provided when calling the method
        else:
            myElements = self.tree.findall('.//t:%s[@type="%s"]' %
                                           (keeptag, keeptype), myconst.ns)
        for k in myElements:
            # If parenttag is the parent and keeptag is the sibling:
            parent = k.getparent()
            if parent.tag == myconst.tei_ns + parenttag and parent.find(
                    './/t:%s' % (removetag), myconst.ns) is not None:
                # The following 'remove' functions should be safe b/c <orig>,
                # <reg> and the other children of <choice>,
                # as wella as <add> / <del> children of <subst>
                # never have a tail b/c <orig> and <reg> are the only children
                # of <choice>
                # (otherwise, the tail would be removed too)
                #
                # Element to remove:
                r = k.getparent().find('.//t:%s' % (removetag), myconst.ns)
                if r.tail is not None:
                    print('Warning: element', r.tag, 'has tail text «' +
                          r.tail + '» that is also being removed')
                r.getparent().remove(r)

    def handle_add_del(self):
        ''' Management of <add> and <del>:
                - if <add> and <del> have no @hand,
                    this means that the addition/deletion has been made by the
                    main hand of the MS, so I'll respect it:
                    - delete <del>
                    - keep the content of <add>
                - else (if @hand is provided), this means that the
                    addition/deletion has been made by a later hand,
                    so ignore them:
                    - keep the content of <del> (the later scribe's
                        deletion is ignored)
                    - delete <add> (don't keep the later addition)
            '''
        for e in self.tree.findall('.//t:%s' % ('add'), myconst.ns):
            # If @hand is provided, then the
            # addition is my a later hand: ignore it (remove <add>)
            if e.get('hand') is not None:
                e.getparent().remove(e)
        for e in self.tree.findall('.//t:%s' % ('del'), myconst.ns):
            # If no @hand is provided, then
            # the addition is by the MS's main hand: delete <del>
            if e.get('hand') is None:
                e.getparent().remove(e)

    def handle_gaps(self):
        ''' Replace <gap> with text in {curly brackets} '''
        for e in self.tree.findall('.//t:%s' % ('gap'), myconst.ns):
            gapReason = e.get('reason')
            gapQuantity = e.get('quantity')
            gapQuantityNum = int(gapQuantity)
            gapUnit = e.get('unit')
            if gapUnit == 'words' and gapQuantityNum == 1:
                gapUnit = 'word'
            e.text = '{%s_%s_%s}' % (gapQuantity, gapReason, gapUnit)

    def ecaudatum(self, monophthongize=True):
        ''' If monophthongize is True, transform <seg ana="#ae">ae</seg>
            to <seg ana="#ae">e</seg>.
            If it is False, it remains <seg ana="#ae">ae</seg>
            '''
        if monophthongize:
            for e in self.tree.findall('.//t:%s' % ('seg[@ana="#ae"]'),
                                       myconst.ns):
                e.text = 'e'
            for e in self.tree.findall('.//t:%s' % ('seg[@ana="#doubleae"]'),
                                       myconst.ns):
                e.text = 'ee'

    def recapitalize(self):
        ''' Re-capitalize words included in <rs> or in <hi>.
            Then, transform text marked as <p type="ghead1"> or "ghead2"
            to all uppercase,
            because it was in G(arufi) head(s) '''
        for mytagname in ['rs', 'hi']:
            for e in self.tree.findall('.//t:%s' % (mytagname), myconst.ns):
                # If the content of <rs>/<hi> starts with a text node,
                # capitalize it
                if e.text:
                    e.text = e.text.capitalize()
                # If the content of <rs>/<hi> starts with an element...
                else:
                    echild = e[0]
                    # In case <rs><choice>etc. or <hi><choice>etc.
                    if echild.tag == myconst.tei_ns + 'choice':
                        # ...capitalize text of all children of <choice>
                        for alternative in echild:
                            alternative.text = alternative.text.capitalize()
                    # If first child of <rs>/<hi> is not <choice>
                    # ...get the text of <rs>/<hi>'s first child and
                    # capitalize it
                    else:
                        if echild.text:
                            echild.text = echild.text.capitalize()
                        # ... or capitalize the first child of the first
                        # child of <rs>/</hi>
                        else:
                            echild[0].text = echild[0].text.capitalize()
        # Elements to transform in all uppercase:
        ER = []
        ER = ER + self.tree.findall('.//t:p[@type="ghead1"]', myconst.ns)
        ER = ER + self.tree.findall('.//t:p[@type="ghead2"]', myconst.ns)
        for e in ER:
            if e.text is not None:
                e.text = e.text.upper()
            for c in e.findall('.//t:*', myconst.ns):
                if c.text is not None:
                    c.text = c.text.upper()
                if c.tail is not None:
                    c.tail = c.tail.upper()

    def simplify_to_scanlike_text(self, tagslist):
        ''' Strip all tags included in list tagslist within paragraphs
            (while keeping their text and tail).
            So "bla <rs>foo</rs> bar" becomes "bla foo bar".
            All tags are assumed to belong to the TEI XML namespace.
            '''
        for p in self.tree.findall('.//t:p', ns):   # Strip markup inside <p>s
            for t in tagslist:
                etree.strip_tags(p, myconst.tei_ns + t)

    def handle_paragraph_tags(self, action='keep'):
        ''' If action == 'keep':
                Leave them as TEI XML tags (in this case, it's useless to call
                this method)
            if action == 'text':
                Replace <p xml:id="g163.8-163.10" decls="#ocr">
                with 163.8-163.10 and remove <p> XML tags;
                If action == 'bracketsOnly',
                Replace <p xml:id="g163.8-163.10" decls="#ocr">  with
                [p xml:id="g163.8-163.10"] (good for collation)
            If action == 'bracketsToo',
                Keep <p xml:id="g163.8-163.10" decls="#ocr"> and add with
                [p xml:id="g163.8-163.10"]...[/p] (also good for collation)
                Example: transform
                    <p xml:id="g163.8-163.10">
                    bla bla
                    </p>
                to
                    <p xml:id="g163.8-163.10">
                    [p xml:id="g163.8-163.10"]
                    bla bla
                    [/p]
                    </p>
            '''
        body = self.tree.find('.//t:body', ns)
        for p in body.findall('.//t:p', ns):
            try:
                # Replace <p xml:id="g163.8-163.10" decls="#ocr">
                # with 163.8-163.10
                xmlid = p.get(myconst.xml_ns + 'id')
            except Exception as e:
                print('I am trying handling <par> tags, but the I can\'t get \
                      the xml:id of this <par>')
            try:
                if p.text is None:
                    p.text = ''
            except Exception as e:
                print('I am handling <par> tags, but the I can\'t get \
                      the text of this <par>. All I get is «%s»' % (p.text))
            if action == 'text':
                p.text = ''.join([xmlid, ' ', p.text])
            elif action == 'bracketsOnly' or action == 'bracketsToo':
                bracketOpenTag = '[p xml:id="%s"] ' % xmlid
                bracketCloseTag = '[/p] '
                p.text = ''.join([bracketOpenTag, p.text, bracketCloseTag])
        if action == 'text' or action == 'bracketsOnly':
            etree.strip_tags(body, myconst.tei_ns + 'p')

    def tags_to_brackets(self, tagslist):
        ''' For each tag in list tagslist, transform
            <> to [].  E.g.: with list ['anchor', 'l'],
            <anchor xml:id="g187.11-187.14garufiandbonetticollocation"
            type="transposition" subtype="garufiandbonetticollocation"/>
            becomes
            [anchor xml:id="g187.11-187.14garufiandbonetticollocation"
            type="transposition" subtype="garufiandbonetticollocation"/]
            '''

        emptyElements = ['milestone', 'link', 'anchor']
        body = self.tree.find('.//t:body', ns)
        for tag in tagslist:
            bracketCloseTag = '[/%s] ' % (tag)   # e.g.: [/anchor]
            for e in body.findall('.//t:%s' % (tag), ns):
                tagName = e.tag.split('}')[1]   # Remove initial namespace
                # {http://www.w3.org/XML/1998/namespace}
                tagAttributesDict = e.attrib    # This is a dict
                # This transforms the dict to a string like
                # ['type="bonetti-paragraph-break"', 'unit="paragraph"',
                # 'ed="#b"']:
                tagAttributesList = ['%s="%s"' %
                                     (attr, tagAttributesDict[attr])
                                     for attr in tagAttributesDict]
                # This is the same, but in a string:
                tagAttributesString = ' '.join(tagAttributesList)
                tagAttributesString = tagAttributesString.replace(
                    '{http://www.w3.org/XML/1998/namespace}', 'xml:')
                if len(tagAttributesString) > 0:
                    bracketOpenTag = ' '.join([tagName, tagAttributesString])
                else:
                    bracketOpenTag = tagName
                bracketOpenTag = '[%s] ' % bracketOpenTag
                try:
                    if e.text is None:
                        e.text = ''
                except Exception as e:
                    print('I am handling <%s> tags, but \
                          I can\'t get the\
                          text of this <%s>. All I get is «%s»' %
                          (tagName, tagName, e.text))
                # If it is an empty element, e.g. <anchor/>:
                if tagName in emptyElements:
                    bracketOpenTag = bracketOpenTag.replace(']', '/]')
                    e.text = ''.join([bracketOpenTag, e.text])
                    # print('Tag <%s> is empty. Its open tag is «%s» and its
                    # text is now «%s»' % (tagName, bracketOpenTag, e.text))
                else:   # If it is no empty element, e.g. <l>
                    e.text = ''.join([bracketOpenTag, e.text, bracketCloseTag])
            etree.strip_tags(body, myconst.tei_ns + tag)

    def my_strip_tags(self, tagname):
        '''Remove start and end tag but keep text and tail'''
        etree.strip_tags(self.tree, tagname)

    def my_strip_elements(self, tagname, my_with_tail=False):
        '''Remove start and end tag; remove textual content; keep tail if
            my_with_tail=False (default)'''
        etree.strip_elements(self.tree, myconst.tei_ns + tagname,
                             with_tail=my_with_tail)

    def handle_numerals(self):
        '''Replace 'u' with 'v' in the textual content of <num> elements,
            and make them all uppercase'''
        for num in self.tree.findall('.//t:num', ns):

            # Replace 'u' with 'v' is @type is not 'words'

            if num.get('type') != 'words':
                if num.text:
                    # Direct textual content of <num>:
                    num.text = num.text.replace('u', 'v')
                for x in num.findall('.//t:*', ns):     # Children
                    # elements of <num>
                    if x.text:
                        x.text = x.text.replace('u', 'v')
                    if x.tail:
                        x.tail = x.tail.replace('u', 'v')

            # Make uppercase if @type is not 'words'
            if num.get('type') != 'words':
                if num.text is not None:
                    num.text = num.text.upper()
                for c in num.findall('.//t:*', myconst.ns):
                    if c.text is not None:
                        c.text = c.text.upper()
                    if c.tail is not None:
                        c.tail = c.tail.upper()

    def reduce_layers_to_alph_only(self):
        ''' This big function inputs a TEI XML paragraph encoded at two layers
            (GL and AL)
            and returns the same XML paragraph, but with one layer only (AL).
            Argument 'self' is a LMXL XML Element object <p>
        '''

        # Read ToS
        if self.siglum in ['a1', 'a2', 'a-1and2unified']:
            mySiglum = 'a'
        else:
            mySiglum = self.siglum
        toscsvfile = '%s/%s-tos.csv' % (myconst.csvpath, mySiglum)
        with open(toscsvfile) as atosfile:
            # Read csv into a list of lists:
            tos = list(list(rec) for rec in csv.reader(
                atosfile, delimiter='\t'))
            # Columns: 0=Grapheme  1=Alphabeme(s)    2=Grapheme visualization
            # 3=Type    4=Notes    5=Image(s)

        # Read Abbreviation Combinations file
        combicsvfile = '%s/%s-combi.csv' % (myconst.csvpath, mySiglum)
        with open(combicsvfile) as combifile:
            combi = list(list(rec) for rec in csv.reader(
                combifile, delimiter='\t'))  # reads csv into a list of lists
            # Columns: 0=Grapheme  1=Alphabeme(s)    2=Notes

        for par in self.tree.findall('.//t:p[@decls="#algl"]', ns):

            for x in par.findall('.//t:*', ns):
                # Remove line breaks that seem to interfere with string
                # substitutions (in particular, 'tail' stopped at line break)
                if x.text:
                    x.text = x.text.replace('\n', ' ')
                if x.tail:
                    x.tail = x.tail.replace('\n', ' ')

            # Remove  <abbr> tags entirely (including their textual content,
            # but not their tail)
            etree.strip_elements(par, myconst.tei_ns + 'abbr', with_tail=False)

            # First, expand common abbreviation combinations applying only to
            # independent/whole words
            for row in combi:
                if re.match('<.*>', row[0]):
                    wwgraph = row[0][1:-1]  # This changes "<qd->" to "qd-"
                    # I replaced alltext with par:
                    myReplaceAll(wwgraph, row[1], par, wholeWord=True)

            # ... then expand specific combinations such as 'q3'
            # (this allows me
            # to create abbr. strings such as 'gnaw'='genera':
            #       the 'aw' part also matches [aeiouy]w and could be expanded
            #       as 'am', but this does not happen b/c the specific
            #       abbreviation combination 'gnaw' is expanded before the
            #       more generic combination '[aeiouy]w'
            for row in combi:
                if not re.match('<.*>', row[0]) \
                   and not re.match('\[.*', row[0]):
                    # I replaced alltext with par:
                    myReplaceAll(row[0], row[1], par)

                # ...  then expand more generic common
                # abbreviation combinations such as '[aeiouy]0'
                if re.match('\[.*', row[0]):
                    # I replaced alltext with par:
                    genericBaseReplaceAll(row, par)

            # ... eventually, translate every grapheme into their standard
            # alphabetic meaning:
            for row in tos:
                if row[3] in ['Alphabetic', 'Brevigraph']:
                    myReplaceAll(row[0], row[1], par)

            # Create a temporary <lb/> (that will later be stripped) with
            # tail '\n' and append it to <p>
            # in order to add a line break at the very end of <p>
            # because in other TEI XML files </p> is in its own line (so: "bla
            # bla\n</p>", not "bla bla</p>"
            tempLb = etree.SubElement(par, tei_ns + 'lb')
            tempLb.tail = '\n'
            '''
            if len(par) == 0 and par.text is None:
                print(par.get(xml_ns + 'id'))
            elif len(par) == 0 and par.text is not None:
                par.text = par.text + '\n'
            elif len(par) > 0 and par.text is not None:
            else:
                print(len(par))
                # print('foo')
                if par.text is not None:
                    par.text = par.text + '\n\n'  # Add a line break because in
                    other TEI XML files </p> is in its own line
                    '''

    def write(self):
        self.tree.write(self.outputXmlFile, encoding='UTF-8', method='xml',
                        pretty_print=True, xml_declaration=True)


def finalProcessingBeforeJuxta(siglaList, siglaToShortenList):
    '''In simplified TEI XML files,
        - change [p xml:id="g3.1-3.1"][/p] to [p xml:id="g3.1-3.1"]\n[/p]
        - remove empty lines
        - create «a1s-short.xml», «gs-short.xml» etc. versions '''

    for mySiglum in siglaList:
        edition = mySiglum + myconst.simplifiedsuffix
        xmlfile = '%s/%s.xml' % (myconst.xmlpath, edition)
        shortxmlfile = xmlfile.replace('.xml', '-short.xml')
        myLines = []
        with open(xmlfile, 'r') as IN:
            for line in IN:  # Change [p xml:id="g3.1-3.1"][/p] to
                # [p xml:id="g3.1-3.1"]\n[/p]'''
                if line.startswith('[p xml:id="') \
                   and line.strip().endswith('"][/p]'):
                    line = line.replace('"][/p]', '"]\n[/p]')
                if line.strip():  # Remove empty lines
                    # If line doesn't end with a trailing space, add the space:
                    if line[-2:-1] != ' ':
                        line = line.replace('\n', ' \n')
                    # If line doesn't end with two spaces, remove one:
                    if line[-3:-1] == '  ':
                        line = line.replace('  \n', ' \n')
                    myLines.append(line)
        with open(xmlfile, 'w') as OUT:
            # Write back long files (e.g. a1s.xml)
            for line in myLines:
                print(line, file=OUT, end='')
        # create «a1s-short.xml» versions:
        if mySiglum in siglaToShortenList:
            if mySiglum in ['g', 'a1']:
                # It was 'milestone type="garufi-one-layer-from-here-on"
                # unit="collation"':
                stopLine = 'p xml:id="g6.26-6.34"'
            elif mySiglum in ['bonetti', 'a2-sorted']:
                stopLine = 'p xml:id="g169.5-170.14"'
            else:
                print('I don\'t know where to cut file {}'.format(mySiglum))
            with open(xmlfile, 'r') as IN:
                with open(shortxmlfile, 'w') as OUT:
                    for line in IN:
                        if re.search(stopLine, line):
                            print('</body>\n</text>\n</TEI>', file=OUT, end='')
                            break
                        else:
                            print(line, file=OUT, end='')
