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
import entitize
# import a_unifier
import splitter
import sort_a2
import simplify_markup_for_collation
import post_process_juxta_commons_file
import philologist
import m_unifier

# If true: suppress standard output messages to console
quiet = False

#################
# PRE-COLLATION #
#################

# a_unifier.py
# a_unifier.a_unifier(quiet=quiet)

# splitter.py
splitter.a_splitter()

# entitize.py
for f in iglob('%s*.xml' % (xmlpath)):
    # base = f.split('/')[-1].split('.')[0]
    entitize.entitize(f, quiet=quiet)

# sort_a2.py
sort_a2.sort_a2(quiet=quiet)

# simplify_markup_for_collation.py / class msTree
# edition_list = ['a1', 'a2-sorted', 'o', 'o-short', 'g', 'bonetti',
edition_list = ['a1', 'a2-sorted', 'o', 'g', 'bonetti',
                'bonetti-short']
for edition in edition_list:
    mytree = simplify_markup_for_collation.msTree(edition, quiet=quiet)
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
simplify_markup_for_collation.finalProcessingBeforeJuxta(
    siglaList=['a1', 'a2-sorted', 'o', 'g', 'bonetti'],
    siglaToShortenList=['a1', 'a2-sorted', 'g', 'bonetti'],
    quiet=quiet)


##################
# POST-COLLATION #
##################

parameters = [
    {'siglum': 'm1',
     'ed': 'garufi',
     'printSiglum': 'g',
     'msaSiglum': 'a',
     'msa2Siglum': 'a2',
     'msoSiglum': 'o'},
    {'siglum': 'm2',
     'ed': 'bonetti',
     'printSiglum': 'b',
     'msaSiglum': 'a',
     'msa2Siglum': 'a2',
     'msoSiglum': 'o'},
    {'siglum': 'm3',
     'ed': 'bonetti',
     'printSiglum': 'b',
     'msaSiglum': 'a',
     'msa2Siglum': 'a2',
     'msoSiglum': 'o'}
]

for mp in parameters:

    ''' Post-processing of JuxtaCommons-generated files
        (from module post_process_juxta_commons_file.py)'''
    post_process_juxta_commons_file.replacePointyBrackets(mp['siglum'])
    myTree = post_process_juxta_commons_file.msTree(mp['siglum'],
                                                    mp['ed'],
                                                    mp['printSiglum'],
                                                    mp['msaSiglum'],
                                                    mp['msa2Siglum'],
                                                    mp['msoSiglum'])
    myTree.replaceSigla()
    myTree.removeEmptyParWrappingAllText()

    ''' Set <lem>/<rdg> and set @type attributes for <app>s
        (from module set_variant_types_in_appcrit_tei_file.py) '''
    newSiglum = mp['siglum'] + juxta_par_and_sigla_suffix
    myTree = philologist.treeWithAppElements(newSiglum,
                                             mp['printSiglum'],
                                             mp['msaSiglum'],
                                             mp['msa2Siglum'],
                                             mp['msoSiglum'],
                                             quiet=quiet)
    myTree.setA2ForAdditions()
    # myTree.findAndLocateSicCorr()
    myTree.variantTypesCountPrint()
    myTree.setTypeAttributesForApps()
    myTree.setLemsBasedOnType()
    myTree.setLemsBasedOnDB()
    myTree.editTeiHeader()
    myTree.putLemAsFirstInApp()
    myTree.write()

m_unifier.unify()
