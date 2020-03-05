#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' Post-process the output of JuxtaCommons before inspecting variant types:
    see documentations of module(s) below '''

import myconst
from simplify_markup_for_collation import msTree


def postProcessJuxtaCommonsFile(siglum, printEdition='garufi',
                                printSiglum='g', msSiglum='a'):
    ''' Change
            - [tag attr="value"] to \n<tag attr="value">
            - [/tag] to \n</tag>
        Substitute
            - JuxtaComons sigla with my sigla ('g', 'a', 'b' etc.)
        '''

    ###########################
    # REPLACE POINTY BRACKETS #
    ###########################

    xmlfile = '%s%s.xml' % (myconst.xmlpath, siglum)
    with open(xmlfile, 'r') as IN:
        myLines = []
        for line in IN:
            line = line.replace(']\n', ']')
            line = line.replace('[', '\n<').replace(']', '>\n')
            line = line.replace('&quot;', '"')
            myLines.append(line)
    with open(xmlfile, 'w') as OUT:
        for line in myLines:
            print(line, file=OUT, end='')

    #############
    # FIX SIGLA #
    #############

    # Parse XML tree and find <witness> elements
    mytree = msTree(siglum)
    witnesses = mytree.tree.findall('.//t:%s' % ('witness'), myconst.ns)
    juxtaSigla = [
        {'juxtaSiglum': witness.get(myconst.xml_ns + 'id'),
         'element': witness}
        for witness in witnesses
    ]

    # Search which <witness> represents the print edition
    # ('bonetti' or 'garufi'):
    juxtaPrintSiglum = 'unknown'
    for myWitness in juxtaSigla:
        # If 'garufi' in... or if 'bonetti' in...
        if printEdition in myWitness['element'].text.lower():
            juxtaPrintSiglum = myWitness['juxtaSiglum']
            # Associate my print siglum (e.g. 'g') to the JuxtaCommons siglum
            # (e.g. 'wit-41657'):
            myWitness['mySiglum'] = printSiglum

    # Check if the print <witness> has been found or not
    if juxtaPrintSiglum == 'unknown':
        print('I haven\'t found what witness in %s corresponds to %s. \
              Please include string «%s» in the text of one <witness> in %s' %
              (siglum, printEdition.capitalize(), printEdition, siglum))
    else:
        print('The JuxtaCommons-generated witness for %s is %s' %
              (printEdition.capitalize(), juxtaPrintSiglum))

    for myWitness in juxtaSigla:
        # if myWitness['mySiglum'] is None:
        if 'mySiglum' not in myWitness:
            # Associate my MS siglum (e.g. 'a') to the JuxtaCommons siglum
            # (e.g. 'wit-41658'):
            myWitness['mySiglum'] = msSiglum

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

    ######################################
    # Remove empty <p> wrapping all text #
    ######################################
    body = mytree.tree.find('.//{http://www.tei-c.org/ns/1.0}body')
    par = body.find('.//{http://www.tei-c.org/ns/1.0}p')
    for child in par:
        body.append(child)
    body.remove(par)

    print(mytree.siglum, len(par))

    # Replace file
    mytree.tree.write(xmlfile, encoding='UTF-8', method='xml',
                      pretty_print=True, xml_declaration=True)


######################
# EXECUTE FUNCTIONS  #
######################


'''
postProcessJuxtaCommonsFile(siglum='m1', printEdition='garufi',
                            printSiglum='g', msSiglum='a')
postProcessJuxtaCommonsFile(siglum='m1-short', printEdition='garufi',
                            printSiglum='g', msSiglum='a')
'''
postProcessJuxtaCommonsFile(siglum='m2', printEdition='bonetti',
                            printSiglum='b', msSiglum='a')
