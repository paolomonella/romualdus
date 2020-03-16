#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' Post-process the output of JuxtaCommons before inspecting variant types:
    see documentations of module(s) below '''

import myconst
from simplify_markup_for_collation import msTree

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
        print('xmlfile, outSiglum, xmlOutFile', xmlfile, outSiglum, xmlOutFile)
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


def replaceSigla(siglum, printEdition, printSiglum,
                 msaSiglum='a', msoSiglum='o',
                 quiet=False):
    ''' Substitute JuxtaCommons sigla with my sigla ('g', 'a', 'b' etc.)
        printEdition may be 'garufi' or 'bonetti';
        printSiglum may be 'g' or 'b' accordingly '''

    outSiglum = siglum + myconst.juxta_par_and_sigla_suffix
    xmlOutFile = '%s%s.xml' % (myconst.xmlpath, outSiglum)

    # Parse XML tree and find <witness> elements
    mytree = msTree(outSiglum)
    witnesses = mytree.tree.findall('.//t:%s' % ('witness'), myconst.ns)

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
        if printEdition in myWitness['element'].text.lower():
            # juxtaPrintSiglum = myWitness['juxtaSiglum']  # §
            # Associate my print siglum (e.g. 'g') to the JuxtaCommons siglum
            # (e.g. 'wit-41657'):
            myWitness['mySiglum'] = printSiglum
        # Identify the MS A siglum
        # (When I 'prepare' the witness in JuxtaCommons, the
        #  description must be exactly 'a')
        elif myWitness['element'].text.lower() == 'a':
            # Associate 'a' to the JuxtaCommons siglum
            # (e.g. 'wit-41658'):
            myWitness['mySiglum'] = msaSiglum
        # Identify the MS O siglum
        # (When I 'prepare' the witness in JuxtaCommons, the
        #  description must be exactly 'o')
        elif myWitness['element'].text.lower() == 'o':
            # Associate 'o' to the JuxtaCommons siglum
            # (e.g. 'wit-41659'):
            myWitness['mySiglum'] = msoSiglum
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
    for rdg in mytree.tree.findall('.//t:%s' % ('rdg'), myconst.ns):
        rdgSiglum = rdg.get('wit')
        for s in juxtaSigla:
            rdgSiglum = rdgSiglum.replace(s['juxtaSiglum'], s['mySiglum'])
        rdg.set('wit', rdgSiglum)

    # Replace file
    mytree.tree.write(xmlOutFile, encoding='UTF-8', method='xml',
                      pretty_print=True, xml_declaration=True)


def removeEmptyParWrappingAllText(siglum):
    ''' Remove empty <p> wrapping all text in JuxtaCommons-generated
        TEI XML file '''

    outSiglum = siglum + myconst.juxta_par_and_sigla_suffix
    xmlOutFile = '%s%s.xml' % (myconst.xmlpath, outSiglum)

    # Parse XML tree and find <witness> elements
    mytree = msTree(outSiglum)
    body = mytree.tree.find('.//{http://www.tei-c.org/ns/1.0}body')
    par = body.find('.//{http://www.tei-c.org/ns/1.0}p')
    for child in par:
        body.append(child)
    body.remove(par)

    if debug:
        print('[Debug 07.03.2020 10.41] siglum %s, including %s paragraphs' %
              (mytree.siglum, len(par)))

    # Replace file
    mytree.tree.write(xmlOutFile, encoding='UTF-8', method='xml',
                      pretty_print=True, xml_declaration=True)
