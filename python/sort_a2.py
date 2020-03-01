#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module re-orders paratraphs in a2.xml to match those in Bonetti '''

from lxml import etree
import myconst

debug = False


pSiglum = 'bonetti' # prefix 'p' = 'print'
mSiglum = 'a2'      # prefix 'm' = 'MS'

#pSiglum, mSiglum = pSiglum, mSiglum

pFile = '%s/%s.xml' % (myconst.xmlpath, pSiglum)
mFile  = '%s/%s.xml' % (myconst.xmlpath, mSiglum)

parser = etree.XMLParser(ns_clean=True, remove_comments=True)

pTree = etree.parse(pFile, parser)
mTree = etree.parse(mFile, parser)

#pOutFile = pFile.replace('.xml', '-sorted.xml')
mOutFile = mFile.replace('.xml', '-sorted.xml')

pBody = pTree.find('.//t:%s' % ('body'), myconst.ns)
mBody = mTree.find('.//t:%s' % ('body'), myconst.ns)

# I'm ignoring <anchor>s and <interp>s, and only importing <p>s
pPars = pBody.findall('.//t:%s' % ('p'), myconst.ns)
mPars = mBody.findall('.//t:%s' % ('p'), myconst.ns)

xmlid = myconst.xml_ns + 'id'

if False:
    # Check how many milestones are there
    mMiles = mBody.findall('.//t:%s' % ('milestone'), myconst.ns)
    print('There are {} <milestone>s in total'.format(len(mMiles)))

if False:
    # Check what kind of children <body> has
    print('In a2.xml, <body> has these direct children:')   
    for x in set(bodyChildren):
        print('{:4}  {:10}'.format(bodyChildren.count(x), x))

if False:
    # Compare how many paragraphs a2.xml and bonetti.xml have
    print('Length of pPars: {}\nLength of mMars: {}'.format(len(pPars), len(mPars)))

mSortedPars = []   # This list will incude the new sequence of <p>s of a2.xml, sorted according to the order of Bonetti

for pPar in pPars:
    myId = pPar.get(xmlid)
    mPar = mBody.find('.//t:%s[@%s="%s"]' % ('p', xmlid, myId), myconst.ns) # The corresponding <p> in a2.xml
    mSortedPars.append(mPar)

# Empty the <body> of a2.xml (delete all its children)
for x in mBody:
    mBody.remove(x)

# Re-populate the <body> of a2.xml with the <p>s from list mSortedPars
for x in mSortedPars:
    mBody.append(x)

mTree.write(mOutFile, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)

# Check that everything went OK

if False:
    mNewTree = etree.parse(mOutFile, parser)
    mNewBody = mNewTree.find('.//t:%s' % ('body'), myconst.ns)

    # The <p>s in a2-sorted.xml
    mNewPars = mNewBody.findall('.//t:%s' % ('p'), myconst.ns)
    #print(len(mNewPars))

    if len(mNewPars) == len(pPars):
        for i in range(len(mNewPars)):
            print('{:20} {:20}'.format(pPars[i].get(xmlid), mNewPars[i].get(xmlid)))
    else:
        print('Bonetti and a2-sorted don\'t have the same number of paragraphs')
