#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' Post-process the output of JuxtaCommons before inspecting variant types:
    See documentations of methods below '''


#########################
# Plain text processing #
#########################

import myconst
from lxml import etree

debug = False


def replacePointyBrackets(siglum):
    ''' Replace <> with [], i.e. change
            - [tag attr="value"] to \n<tag attr="value">
            - [/tag] to \n</tag>
        '''

    xmlfile = '%s%s.xml' % (myconst.xmlpath, siglum)
    outSiglum = siglum + myconst.juxta_par_and_sigla_suffix
    xmlOutFile = '%s%s.xml' % (myconst.xmlpath, outSiglum)
    if debug:
        print('xmlfile: {}\noutSiglum: {}\nxmlOutFile: {}'.format(
            xmlfile, outSiglum, xmlOutFile))
    with open(xmlfile, 'r') as IN:
        myLines = []
        for line in IN:
            line = line.replace(']\n', ']')
            line = line.replace('[', '\n<').replace(']', '>\n')
            line = line.replace('&quot;', '"')
            myLines.append(line)
    with open(xmlOutFile, 'w') as OUT:
        for line in myLines:
            print(line, file=OUT, end='')


#########################
# XML tree manipulation #
#########################

class msTree:

    def __init__(self, siglum, printEdition, printSiglum,
                 msaSiglum='a', msa2Siglum='a2', msoSiglum='o'):
        self.siglum = siglum
        self.printEdition = printEdition
        self.printSiglum = printSiglum
        self.msaSiglum = msaSiglum
        self.msoSiglum = msoSiglum
        # Something like m1-par or m2-par:
        self.xmlInBaseFileName = \
            self.siglum + myconst.juxta_par_and_sigla_suffix
        self.xmlInFile = '%s%s.xml' % (myconst.xmlpath, self.xmlInBaseFileName)
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        self.tree = etree.parse(self.xmlInFile, parser=parser)
        self.root = self.tree.getroot()
        self.body = self.tree.find('.//{http://www.tei-c.org/ns/1.0}body')
        # Input m1-par.xml, output m1-par.xml (same file)
        self.xmlOutFile = self.xmlInFile

    def replaceSigla(self):
        ''' Substitute JuxtaCommons sigla with my sigla ('g', 'a', 'b' etc.)
            printEdition may be 'garufi' or 'bonetti';
            printSiglum may be 'g' or 'b' accordingly '''

        # Parse XML tree and find <witness> elements
        witnesses = self.tree.findall('.//t:%s' % ('witness'), myconst.ns)

        # A list of dictionaries (from the <witList> list in the teiHeader
        # of m1.xml or m2.xml. Later, the value of 'mySiglum' will be
        # set to 'g', 'b', 'a' or 'o'.
        juxtaSigla = [
            {'juxtaSiglum': witness.get(myconst.xml_ns + 'id'),
             'mySiglum': '',
             'element': witness}
            for witness in witnesses
        ]

        # Search which <witness> represents the print edition
        # ('bonetti' or 'garufi'):
        # juxtaPrintSiglum = 'unknown_siglum'  # §
        for myWitness in juxtaSigla:
            # Identify the print (garufi/bonetti) siglum
            # If 'garufi' in... or if 'bonetti' in...
            # (When I 'prepare' the witness in JuxtaCommons, the
            #  description for this must include the whole word
            #  'garufi' or 'bonetti', case-insensitive)
            if self.printEdition in myWitness['element'].text.lower():
                # juxtaPrintSiglum = myWitness['juxtaSiglum']  # §
                # Associate my print siglum (e.g. 'g') to the
                # JuxtaCommons siglum (e.g. 'wit-41657'):
                myWitness['mySiglum'] = self.printSiglum
            # Identify the MS A siglum
            # (When I 'prepare' the witness in JuxtaCommons, the
            #  description must be exactly 'a')
            elif myWitness['element'].text.lower() == 'a':
                # Associate 'a' to the JuxtaCommons siglum
                # (e.g. 'wit-41658'):
                myWitness['mySiglum'] = self.msaSiglum
            # Identify the MS O siglum
            # (When I 'prepare' the witness in JuxtaCommons, the
            #  description must be exactly 'o')
            elif myWitness['element'].text.lower() == 'o':
                # Associate 'o' to the JuxtaCommons siglum
                # (e.g. 'wit-41659'):
                myWitness['mySiglum'] = self.msoSiglum
            else:
                print(('[replaceSigla] I didn\'t understand '
                       'to which actual witness '
                       'siglum {} corresponds to. '
                       'In the witness description in JuxtaCommons website, '
                       'the print edition description must include '
                       '"garufi" or "bonetti", and the MS descriptions must '
                       'be exactly "a" or "o"').format(
                           myWitness['juxtaSiglum']
                       ))

        # Replace value in <witness xml:id...>
        for witness in witnesses:
            witXmlId = witness.get(myconst.xml_ns + 'id')
            for s in juxtaSigla:
                witXmlId = witXmlId.replace(s['juxtaSiglum'], s['mySiglum'])
            witness.set(myconst.xml_ns + 'id', witXmlId)

        # Replace value in <rdg wit=...>
        for rdg in self.tree.findall('.//t:%s' % ('rdg'), myconst.ns):
            rdgSiglum = rdg.get('wit')
            for s in juxtaSigla:
                rdgSiglum = rdgSiglum.replace(s['juxtaSiglum'], s['mySiglum'])
            rdg.set('wit', rdgSiglum)

        # Replace file
        self.tree.write(self.xmlOutFile, encoding='UTF-8', method='xml',
                        pretty_print=True, xml_declaration=True)

    def removeEmptyParWrappingAllText(self):
        ''' Remove empty <p> wrapping all text in JuxtaCommons-generated
            TEI XML file '''

        # Parse XML tree and find <witness> elements
        par = self.body.find('.//{http://www.tei-c.org/ns/1.0}p')
        for child in par:
            self.body.append(child)
        self.body.remove(par)

        if debug:
            print(('[Debug 07.03.2020 10.41] siglum {}, '
                   'including {} paragraphs').format(
                       self.siglum,
                       len(par)))

        # Replace file
        self.tree.write(self.xmlOutFile, encoding='UTF-8', method='xml',
                        pretty_print=True, xml_declaration=True)
