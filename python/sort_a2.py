#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


def sort_a2(pSiglum='bonetti', mSiglum='a2', quiet=False):
    ''' This module re-orders paragraphs in a2.xml
        to match those in Bonetti.
            prefix 'p' = 'print'
            prefix 'm' = 'MS' '''

    if not quiet:
        print('\n[sort_a2.py]: '
              'I am re-arranging the <p>s of a2.xml '
              'according to the order of <p>s '
              'in Bonetti\n')
    from lxml import etree
    from myconst import xmlpath, ns, xml_ns

    pFile = '%s/%s.xml' % (xmlpath, pSiglum)
    mFile = '%s/%s.xml' % (xmlpath, mSiglum)

    parser = etree.XMLParser(ns_clean=True, remove_comments=True)

    pTree = etree.parse(pFile, parser)
    mTree = etree.parse(mFile, parser)

    # pOutFile = pFile.replace('.xml', '-sorted.xml')
    mOutFile = mFile.replace('.xml', '-sorted.xml')

    pBody = pTree.find('.//t:%s' % ('body'), ns)
    mBody = mTree.find('.//t:%s' % ('body'), ns)

    # I'm ignoring <anchor>s and <interp>s, and only importing <p>s
    pPars = pBody.findall('.//t:%s' % ('p'), ns)

    xmlid = xml_ns + 'id'

    # This list will incude the new sequence of <p>s of a2.xml,
    # sorted according to the order of Bonetti:
    mSortedPars = []

    for pPar in pPars:
        myId = pPar.get(xmlid)
        # The corresponding <p> in a2.xml:
        mPar = mBody.find('.//t:%s[@%s="%s"]' % ('p', xmlid, myId), ns)
        if False:
            if mPar is None:
                print('xml:id «%s» not found' % myId)
        mSortedPars.append(mPar)

    # Empty the <body> of a2.xml (delete all its children)
    for x in mBody:
        mBody.remove(x)

    # Re-populate the <body> of a2.xml with the <p>s from list mSortedPars
    for x in mSortedPars:
        mBody.append(x)

    mTree.write(mOutFile, encoding='UTF-8', method='xml',
                pretty_print=True, xml_declaration=True)

    # Check that everything went OK

    if False:
        mNewTree = etree.parse(mOutFile, parser)
        mNewBody = mNewTree.find('.//t:%s' % ('body'), ns)

        # The <p>s in a2-sorted.xml
        mNewPars = mNewBody.findall('.//t:%s' % ('p'), ns)
        # print(len(mNewPars))

        if len(mNewPars) == len(pPars):
            for i in range(len(mNewPars)):
                print('{:20} {:20}'.format(pPars[i].get(xmlid),
                                           mNewPars[i].get(xmlid)))
        else:
            print('Bonetti and a2-sorted don\'t have \
                  the same number of paragraphs')
