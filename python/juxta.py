#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This script triggers all functions and methods related with
    collation with JuxtaCommons, that is:
        - the scripts for pre-processing the original transcriptions (a1.xml,
        a2.xml, g.xml etc.), that are simplified to be fed to JuxtaCommons
        - and the scripts for post-processing the output of JuxtaCommons
        '''

from glob import iglob  # Needed for function entitize
from myconst import xmlpath, juxta_par_and_sigla_suffix
from entitize import entitize
from a_unifier import a_unifier
from sort_a2 import sort_a2
from simplify_markup_for_collation import msTree
from simplify_markup_for_collation import finalProcessingBeforeJuxta
from post_process_juxta_commons_file import replacePointyBrackets
from post_process_juxta_commons_file import replaceSigla
from post_process_juxta_commons_file import removeEmptyParWrappingAllText
from philologist import treeWithAppElements

#################
# PRE-COLLATION #
#################

# entitize.py
for f in iglob('%s*.xml' % (xmlpath)):
    base = f.split('/')[-1].split('.')[0]
    print(('[entitize.py / entitize]: '
           'I am restoring entities for file {}').format(base))
    entitize(base)

# a_unifier.py
a_unifier()

# sort_a2.py
sort_a2()

# simplify_markup_for_collation.py / class msTree
edition_list = ['a1', 'a2-sorted', 'o', 'g', 'bonetti']
for edition in edition_list:
    print(('[simplify_markup_for_collation.py]: I\'m simplifying'
          'witness «{}»').format(edition))
    mytree = msTree(edition)
    if edition == 'a1':
        mytree.reduce_layers_to_alph_only()
    for tag_to_strip in ['interp', 'abbr', 'surplus', 'note', 'milestone',
                         'link', 'anchor']:
        mytree.my_strip_elements(tag_to_strip)
    mytree.handle_numerals()
    mytree.handle_gaps()
    mytree.handle_add_del()  # only needed for MS A
    mytree.choose(parenttag='choice', keeptag='sic', keeptype='',
                  removetag='corr')
    mytree.choose(parenttag='choice', keeptag='reg', keeptype='numeral',
                  removetag='orig')
    mytree.choose(parenttag='choice', keeptag='reg', keeptype='j',
                  removetag='orig')
    mytree.choose(parenttag='choice', keeptag='reg', keeptype='v',
                  removetag='orig')
    # Only needed for MS A; with False,
    # it stays 'ae'; with True, it becomes 'e':
    mytree.ecaudatum(monophthongize=True)
    mytree.remove_comments()
    mytree.recapitalize()
    mytree.simplify_to_scanlike_text(
            ['rs', 'hi', 'w', 'choice', 'orig', 'reg', 'num', 'subst', 'add',
             'del', 'expan', 'sic',
             'seg', 'lb', 'pb', 'quote', 'title', 'said', 'soCalled',
             'surplus', 'supplied', 'gap', 'l']
            )
    mytree.handle_paragraph_tags('bracketsOnly')
    # mytree.tags_to_brackets(['l'])
    mytree.write()
    '''
    # Temporarily needed for CollateX (remove @xmlns)
    with open('%s%s%s.xml' % (myconst.simplifiedpath,
                              edition, myconst.simplifiedsuffix), 'r')\
            as infile:
        data = infile.read()
    with open('%s%s%s.xml' % (myconst.simplifiedpath,
                              edition, myconst.simplifiedsuffix), 'w')\
            as outfile:
        data = data.replace(' xmlns="http://www.tei-c.org/ns/1.0"', '')
        outfile.write(data)
        '''

# simplify_markup_for_collation.py / function finalProcessingBeforeJuxta
finalProcessingBeforeJuxta(
    siglaList=['a1', 'a2-sorted', 'o', 'g', 'bonetti'],
    siglaToShortenList=['a1', 'a2-sorted', 'g', 'bonetti'])

##################
# POST-COLLATION #
##################

parameters = [
    {'siglum': 'm1',
     'ed': 'garufi',
     'printSiglum': 'g',
     'msSiglum': 'a'},
    {'siglum': 'm2',
     'ed': 'bonetti',
     'printSiglum': 'b',
     'msSiglum': 'a'}
]

for mp in parameters:

    ''' Post-processing of JuxtaCommons-generated files
        (from module post_process_juxta_commons_file.py)'''
    replacePointyBrackets(mp['siglum'])
    replaceSigla(mp['siglum'],
                 mp['ed'],
                 mp['printSiglum'],
                 mp['msSiglum'])
    removeEmptyParWrappingAllText(mp['siglum'])

    ''' Set <lem>/<rdg> and set @type attributes for <app>s
        (from module set_variant_types_in_appcrit_tei_file.py) '''
    newSiglum = mp['siglum'] + juxta_par_and_sigla_suffix
    myTree = treeWithAppElements(newSiglum,
                                 mp['printSiglum'],
                                 mp['msSiglum'])
    myTree.variantTypesCountPrint()
    myTree.setTypeAttributesForApps()
    myTree.setLemsBasedOnSicCorr()
    myTree.setLemsBasedOnType()
    myTree.write()
