#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module unifies m1.xml and m2.xml into one file '''

# from shutil import copyfile
from lxml import etree
import my_database_import
from myconst import ns, xmlpath, tei_header_template, chronicon_output_file
from myconst import dbpath, dbname

debug = False


def unify():
    ''' Unify the files '''

    # Import 'paragraphs' table from DB:
    par_table = my_database_import.import_table(
        dbpath,
        dbname,
        'paragraphs')
    # Create a dictionary looking like {'g3.1-3.1': 1 etc.}
    # connecting xml:id's and divs (in this case, <div n="1">)
    div = {}
    for row in par_table:
        div[row['xmlid']] = row['div']  # e.g. div['g3.1-3.1'] = 1

    # Parse input XML files:
    m1_file = '%s%s.xml' % (xmlpath, 'm1-par-out')
    m1_tree = etree.parse(m1_file)

    m2_alfa_file = '%s%s.xml' % (xmlpath, 'm2-alfa-par-out')
    m2_alfa_tree = etree.parse(m2_alfa_file)

    m2_bravo_file = '%s%s.xml' % (xmlpath, 'm2-bravo-par-out')
    m2_bravo_tree = etree.parse(m2_bravo_file)

    m2_charlie_file = '%s%s.xml' % (xmlpath, 'm2-charlie-par-out')
    m2_charlie_tree = etree.parse(m2_charlie_file)

    # This is the file in which I edited the teiHeader by hand
    template_file = '%s%s' % (xmlpath, tei_header_template)

    # Old code:
    # Copy m1-par-out.xml to template.xml
    # copyfile(m1_file, template_file)

    # Parse template.xml
    template_tree = etree.parse(template_file)

    # Set output file name chronicon.xml
    chronicon_file = '%s%s' % (xmlpath, chronicon_output_file)

    # Find <body> elements
    m1_body = m1_tree.find('.//t:body', ns)
    m2_alfa_body = m2_alfa_tree.find('.//t:body', ns)
    m2_bravo_body = m2_bravo_tree.find('.//t:body', ns)
    m2_charlie_body = m2_charlie_tree.find('.//t:body', ns)
    template_body = template_tree.find('.//t:body', ns)

    # Pour <p>s of m1.xml's <body> into the relevant <div> of template.xml:
    for input_body in [m1_body, m2_alfa_body, m2_bravo_body, m2_charlie_body]:
        for p in input_body.findall('.//t:p', ns):
            # @xml:id of  <p>
            par_xmlid = p.get('{%s}id' % ns['xml'])
            # @n of the relvant <div> (it's an integer)
            relevant_div_n = div[par_xmlid]
            # Relevant <div> element in the template XML file:
            relevant_div = template_body.find('.//t:div[@n="%d"]' %
                                              relevant_div_n, ns)
            relevant_div.append(p)

    # Textual critical notes <div> in the template file
    div_notes = template_body.find('.//t:div[@n="notes"]', ns)

    # Pour <note>s of m1.xml's <body> into the relevant <div> of template.xml:
    for input_body in [m1_body, m2_alfa_body, m2_bravo_body, m2_charlie_body]:
        for note in input_body.findall('.//t:note', ns):
            div_notes.append(note)

    # Write tree to output file chronicon.xml:
    template_tree.write(chronicon_file,
                        encoding='UTF-8', method='xml',
                        pretty_print=True, xml_declaration=True)
