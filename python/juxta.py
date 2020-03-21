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
quiet = True

# If True, perform pre-collation operations
pre = True
# If True, perform post-collation operations
post = True

#################
# PRE-COLLATION #
#################

if pre:

    # Split a.xml into a1.xml and a2.xml
    splitter.a_splitter(quiet=quiet)

    # Sort <p>s in a2.xml to make them match Bonetti's sorting.
    # Produce file a2-sorted.xml
    sort_a2.sort_a2(quiet=quiet)

    # Split bonetti.xml and a2-sorted.xml for JuxtaCommons collation
    splitter.second_half_splitter('bonetti', '2-alfa', '2-bravo', '2-charlie')
    splitter.second_half_splitter('a2-sorted', '2-alfa', '2-bravo',
                                  '2-charlie')

    # entitize.py
    for f in iglob('%s*.xml' % (xmlpath)):
        # base = f.split('/')[-1].split('.')[0]
        entitize.entitize(f, quiet=quiet)

    # simplify_markup_for_collation.py / class msTree
    edition_list = ['g',
                    'a1',
                    'bonetti-alfa',
                    'bonetti-bravo',
                    'bonetti-charlie',
                    'a2-sorted-alfa',
                    'a2-sorted-bravo',
                    'a2-sorted-charlie',
                    'o']
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
                ['rs', 'hi', 'w', 'choice', 'orig', 'reg', 'num',
                 'subst', 'add', 'del', 'expan', 'sic',
                 'seg', 'lb', 'pb', 'quote', 'title', 'said', 'soCalled',
                 'surplus', 'supplied', 'gap', 'l']
                )
        mytree.handle_paragraph_tags('bracketsOnly')
        # mytree.tags_to_brackets(['l'])
        mytree.write()

    # simplify_markup_for_collation.py / function finalProcessingBeforeJuxta
    simplify_markup_for_collation.finalProcessingBeforeJuxta(
        siglaList=edition_list,
        quiet=quiet)

##################
# POST-COLLATION #
##################

if post:

    my_msa_siglum = 'a'
    my_msa2_siglum = 'a2'
    my_mso_siglum = 'o'

    parameters = [
        {'siglum': 'm1',
         'ed': 'garufi',
         'printSiglum': 'g'},
        {'siglum': 'm2-alfa',
         'ed': 'bonetti',
         'printSiglum': 'b'},
        {'siglum': 'm2-bravo',
         'ed': 'bonetti',
         'printSiglum': 'b'},
        {'siglum': 'm2-charlie',
         'ed': 'bonetti',
         'printSiglum': 'b'},
    ]

    for mp in parameters:

        ''' Post-processing of JuxtaCommons-generated files
            (from module post_process_juxta_commons_file.py)'''
        post_process_juxta_commons_file.replacePointyBrackets(mp['siglum'])
        myTree = post_process_juxta_commons_file.msTree(mp['siglum'],
                                                        mp['ed'],
                                                        mp['printSiglum'],
                                                        my_msa_siglum,
                                                        my_msa2_siglum,
                                                        my_mso_siglum)
        myTree.replaceSigla()

        myTree.findAndJoinIdenticalReadings()
        myTree.removeEmptyParWrappingAllText()

        ''' Set <lem>/<rdg> and set @type attributes for <app>s
            (from module set_variant_types_in_appcrit_tei_file.py) '''
        newSiglum = mp['siglum'] + juxta_par_and_sigla_suffix
        myTree = philologist.treeWithAppElements(newSiglum,
                                                 mp['printSiglum'],
                                                 my_msa_siglum,
                                                 my_msa2_siglum,
                                                 my_mso_siglum,
                                                 quiet=quiet)
        myTree.set_a2_for_additions()
        # myTree.find_and_locate_sic_corr()
        myTree.variant_subtypes_count_print()
        myTree.set_type_and_subtype_in_all_apps()
        myTree.set_all_lems_based_on_subtype()
        myTree.set_all_lems_based_on_db()
        myTree.edit_tei_header()
        myTree.checkout_checked_paragraphs()
        myTree.put_lem_as_1st_in_app()
        myTree.write()

    m_unifier.unify()
