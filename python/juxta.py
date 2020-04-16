#!/usr/bin/python3.6

# -*- coding: utf-8 -*-
''' Trigger functions/methods related with collation with JuxtaCommons, i.e.:
        - the scripts for pre-processing the original transcriptions (a1.xml,
            a2.xml, g.xml etc.), that are simplified to be fed to JuxtaCommons

        - and the scripts for post-processing the output of JuxtaCommons '''
from glob import iglob  # Needed for function entitize
from myconst import xmlpath, juxta_par_and_sigla_suffix, dbpath, dbname
import entitize
import splitter
import sort_a2
import simplify_markup_for_collation
import post_process_juxta_commons_file
import philologist
import m_unifier
import my_database_import
import biblio
import statistics

quiet = True  # If true, suppress standard output messages to console
# chosen_ones = ('m1', 'm2-alfa', 'm2-bravo', 'm2-charlie')
chosen_ones = ('m2-alfa')
pre = True  # Do pre-processing (before collation)
post = True  # Do post-processing (after collation)


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
                    'bonetti-2-alfa',
                    'bonetti-2-bravo',
                    'bonetti-2-charlie',
                    'a2-sorted-2-alfa',
                    'a2-sorted-2-bravo',
                    'a2-sorted-2-charlie',
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

    complete_parameters = [
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

    parameters = [x for x in complete_parameters
                  if x['siglum'] in chosen_ones]

    print('Working on ', end='')
    for mp in parameters:
        print('{}, '.format(mp['siglum']), end='')

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
        myTree.findAndJoinIdenticalReadings()  # Only needed for 2-bravo
        myTree.removeEmptyParWrappingAllText()
        newSiglum = mp['siglum'] + juxta_par_and_sigla_suffix
        myTree = philologist.treeWithAppElements(newSiglum,
                                                 mp['printSiglum'],
                                                 my_msa_siglum,
                                                 my_msa2_siglum,
                                                 my_mso_siglum,
                                                 quiet=quiet)
        myTree.set_decls_for_long_version_additions()
        myTree.set_a2_for_some_paragraphs()
        myTree.set_all_lems_based_on_subtype()
        myTree.set_all_lems_based_on_db()
        myTree.edit_tei_header()
        myTree.handle_case_variants()
        myTree.set_type_and_subtype_xml_attrib_in_all_apps()
        myTree.checkout_checked_paragraphs()
        myTree.put_lem_as_1st_in_app_and_beautify_app()
        myTree.handle_punctuation_variants()
        myTree.beautify_paragraphs()
        myTree.handle_no_collation_paragraphs()
        myTree.exclude_paragraphs(action='remove')
        myTree.remove_lb_between_paragraphs()
        myTree.write()

    m_unifier.unify()
    statistics.recalculate_statistics(include_general=False)
    statistics.import_statistics()
    biblio.biblio()


def completion():
    ''' Tell me how many paragraphs are left '''
    tot_par = my_database_import.import_table(dbpath, dbname, 'paragraphs')
    checked_par = [p for p in tot_par if p['checked'] > 0]
    done = len(checked_par) - 1  # - 1 b/c there is a 'all' record in the table
    todo = len(tot_par) - 1
    percent = round(done / todo * 100, 1)
    print('checked {}/{}, {}%.'.format(
        done, todo, percent
    ))
