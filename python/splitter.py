#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module includes one big function, extracting/dividing
    the layers from the TEI XML source file. See the documentation
    of the function below for details.
    '''

from lxml import etree
from copy import deepcopy
import sqlite3
from myconst import xmlpath, splitpath, ns, dbpath, dbname
from my_database_import import import_table


def a_splitter(siglum_a1='a1', siglum_a2='a2',
               siglum_uni='a', quiet=False):

    # File names
    xmlfile_uni = '%s%s.xml' % (xmlpath, siglum_uni)
    xmlfile_a1 = '%s%s.xml' % (splitpath, siglum_a1)
    xmlfile_a2 = '%s%s.xml' % (splitpath, siglum_a2)

    # Parse a.xml
    tree_uni = etree.parse(xmlfile_uni)

    # Create deep copies of the original tree for a1 and for a2
    # (because the teiHeader and the general XML tree structure
    #  of a1.xml and a2.xml will be the same of that of a.xml)
    tree_a1 = deepcopy(tree_uni)
    tree_a2 = deepcopy(tree_uni)

    # Find the two <body>es
    body_a1 = tree_a1.find('.//t:body', ns)
    body_a2 = tree_a2.find('.//t:body', ns)

    # a1
    light = 'green'
    for child in body_a1:
        if (child.tag == '{%s}milestone' % (ns['t']) and
            child.get('type') ==
                'bonetti-is-collation-exemplar-from-here-on'):
            light = 'red'
        if light == 'red':
            body_a1.remove(child)

    # a2
    light = 'red'
    for child in body_a2:
        if (child.tag == '{%s}milestone' % (ns['t']) and
            child.get('type') ==
                'bonetti-is-collation-exemplar-from-here-on'):
            light = 'green'
        if light == 'red':
            body_a2.remove(child)

    # Insert <interp>s into a2.xml too
    interps = body_a1.findall('.//t:%s' % ('interp'), ns)
    for interp in reversed(interps):
        new_interp = deepcopy(interp)
        body_a2.insert(0, new_interp)

    if not quiet:
        print(('\n[a_splitter.py]: I\'m splitting'
               ' {}.xml into {}.xml and {}.xml'
               ' for separate JuxtaCommons'
               ' collation.').format(siglum_uni, siglum_a1, siglum_a2))

    # Write a1.xml
    tree_a1.write(xmlfile_a1, encoding='UTF-8', method='xml',
                  pretty_print=True, xml_declaration=True)
    # Write a2.xml
    tree_a2.write(xmlfile_a2, encoding='UTF-8', method='xml',
                  pretty_print=True, xml_declaration=True)


def populate_db_table_with_mso_paragraphs():

    o_file = '%s%s.xml' % (xmlpath, 'o')
    tree = etree.parse(o_file)
    mso_pars = tree.findall('.//t:%s' % ('p'), ns)
    connection = sqlite3.connect('%s%s' % (dbpath, dbname))
    cur = connection.cursor()
    sqlite_query = 'INSERT INTO ottobonianus(par) VALUES(?);'
    for p in mso_pars:
        xmlid = p.get('{%s}id' % ns['xml'])
        cur.execute(sqlite_query, (xmlid,))
        print('«{}»'.format(xmlid))
    connection.commit()
    cur.close()
    if (connection):
        connection.close()


def second_half_splitter(siglum_second_half,
                         suffix_pre_o,
                         suffix_with_o,
                         suffix_post_o,
                         quiet=False):
    ''' Split bonetti.xml or a2-sorted.xml into smaller
        files for JuxtaCommons collation.
        Mind the dash: if siglum_second_half is "bonetti"
        and suffix_pre_o is "alfa", the output file
        name will be "bonetti-alfa.xml" (with an extra dash) '''

    # Import DB table
    table = import_table(dbpath, dbname, 'paragraphs')

    # Check that the three suffixes correspond to the 'chunks'
    # column of the DH table
    db_chunk_list = [x['chunk'] for x in table if x['chunk'] is not '1']
    db_chunk_set = set(db_chunk_list)
    # chunk_list2 = [set(db_chunk_set)]  # Not needed
    if (sorted([suffix_pre_o, suffix_with_o, suffix_post_o]) !=
            sorted(db_chunk_set)):
        print(('[splitter.py / second_half_splitter] Attention:'
               ' the arguments of function second_half_splitter ({})'
               ' don\'t correspond to the "chunks" column of the'
               ' DB table {}').format(
                   sorted([suffix_pre_o, suffix_with_o, suffix_post_o]),
                   sorted(db_chunk_set)))

    # Input file, already existing
    xmlfile_second_half = '%s%s.xml' % (xmlpath, siglum_second_half)
    # Output files to be created
    xmlfile_pre = '%s%s-%s.xml' % (splitpath,
                                   siglum_second_half, suffix_pre_o)
    xmlfile_with = '%s%s-%s.xml' % (splitpath,
                                    siglum_second_half, suffix_with_o)
    xmlfile_post = '%s%s-%s.xml' % (splitpath,
                                    siglum_second_half, suffix_post_o)

    # Parse the input file
    tree_second_half = etree.parse(xmlfile_second_half)

    # Create deep copies of the original tree for the output files
    # (because the teiHeader and the general XML tree structure
    #  will be the same of that of the input file)
    tree_pre_o = deepcopy(tree_second_half)
    tree_with_o = deepcopy(tree_second_half)
    tree_post_o = deepcopy(tree_second_half)

    # Find the <body>es
    body_second_half = tree_second_half.find('.//t:body', ns)
    body_pre_o = tree_pre_o.find('.//t:body', ns)
    body_with_o = tree_with_o.find('.//t:body', ns)
    body_post_o = tree_post_o.find('.//t:body', ns)

    # ...and empty those of the output files
    for body in [body_pre_o, body_with_o, body_post_o]:
        for child in body:
            body.remove(child)

    # For each <p> in the input file
    for p in body_second_half.findall('.//t:%s' % ('p'), ns):
        xmlid = p.get('{%s}id' % ns['xml'])
        for r in table:
            if r['xmlid'] == xmlid:
                chunk = r['chunk']

                # ...move it to the appropriate output file
                if chunk is None:
                    # This paragraph will is handled via the
                    # manual collation files
                    pass
                elif chunk == '2-alfa':
                    body_pre_o.append(p)
                elif chunk == '2-bravo':
                    body_with_o.append(p)
                elif chunk == '2-charlie':
                    body_post_o.append(p)
                else:
                    print(('\n[splitter.py / second_half_splitter]'
                           ' Attention: DB has chunk «{}»,'
                           ' but I can\'t handle it').format(
                               chunk))

    # Write output files
    tree_pre_o.write(xmlfile_pre, encoding='UTF-8', method='xml',
                     pretty_print=True, xml_declaration=True)
    tree_with_o.write(xmlfile_with, encoding='UTF-8', method='xml',
                      pretty_print=True, xml_declaration=True)
    tree_post_o.write(xmlfile_post, encoding='UTF-8', method='xml',
                      pretty_print=True, xml_declaration=True)
