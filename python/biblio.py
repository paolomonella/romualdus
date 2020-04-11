#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module includes one big function, extracting/dividing
    the layers from the TEI XML source file. See the documentation
    of the function below for details.
    '''

from lxml import etree
from myconst import xmlpath, ns, biblio_file, chronicon_output_file

'''
from copy import deepcopy
import sqlite3
from my_database_import import import_table
'''

list_remove = ['language', 'lccn', 'keywords',
               'note', 'abstract', 'isbn']


def moveinto(child_tagname, oldparent, newparent):
    child = oldparent.find('.//b:%s' % (child_tagname), ns)
    if child is not None:
        newparent.append(child)


def renameto(e, oldname, newtagname, attr=None, value=None):

    descendant = e.find('.//b:%s' % (oldname), ns)
    if descendant is not None:
        descendant.tag = '{%s}%s' % (ns['t'], newtagname)
        if attr is not None and value is not None:
            descendant.set(attr, value)


def remove_element(tagname, e):
    descendant = e.find('.//b:%s' % (tagname), ns)
    if descendant is not None:
        descendant.getparent().remove(descendant)


def change_ns(e):
    oldtag = e.tag
    just_tag = oldtag.split('}')[1]
    newtag = '{%s}%s' % (ns['t'], just_tag)
    e.tag = newtag


def createchild(tagname, parent):
    new_element = etree.SubElement(parent, '{%s}%s' % (ns['t'], tagname))
    new_element.text, new_element.tail = '\n                ', '\n'
    return new_element


def process_pages(e, pages):
    myfrom = pages.text.split('-')[0]
    myto = pages.text.split('-')[1]
    # renameto(e, oldname='pages', newtagname='biblScope')
    pages.tag = '{%s}%s' % (ns['t'], 'biblScope')
    pages.set('unit', 'page')
    pages.set('from', myfrom)
    pages.set('to', myto)


def book(e):

    book = e.find('.//b:%s' % ('book'), ns)
    imprint = createchild('imprint', parent=book)

    moveinto('publisher', oldparent=e, newparent=imprint)

    moveinto('year', oldparent=e, newparent=imprint)
    renameto(e, oldname='year', newtagname='date')

    moveinto('location', oldparent=e, newparent=imprint)
    renameto(e, oldname='location', newtagname='pubPlace')

    renameto(e, oldname='book', newtagname='monogr')

    renameto(e, oldname='url', newtagname='ref',
             attr='type', value='url')

    if e.find('.//b:%s' % ('series'), ns) is not None:
        teiseries = createchild('series', parent=e)
        moveinto('series', oldparent=e, newparent=teiseries)
        moveinto('volume', oldparent=e, newparent=teiseries)
        renameto(e, oldname='series', newtagname='title',
                 attr='level', value='s')
        renameto(e, oldname='volume', newtagname='biblScope',
                 attr='unit', value='volume')

    for tag in list_remove:
        remove_element(tag, e)


def inproceedings(e):

    inproceedings = e.find('.//b:%s' % ('inproceedings'), ns)
    imprint = createchild('imprint', parent=inproceedings)
    analytic = createchild('analytic', parent=e)
    e.insert(0, analytic)

    moveinto('publisher', oldparent=e, newparent=imprint)

    moveinto('year', oldparent=e, newparent=imprint)
    renameto(e, oldname='year', newtagname='date')

    moveinto('location', oldparent=e, newparent=imprint)
    renameto(e, oldname='location', newtagname='pubPlace')

    renameto(e, oldname='inproceedings', newtagname='monogr')

    renameto(e, oldname='url', newtagname='ref',
             attr='type', value='url')

    moveinto('author', oldparent=e, newparent=analytic)
    moveinto('title', oldparent=e, newparent=analytic)

    renameto(e, oldname='booktitle', newtagname='title',
             attr='level', value='m')

    pages = e.find('.//b:%s' % ('pages'), ns)
    if pages is not None:
        process_pages(e, pages)

    if e.find('.//b:%s' % ('series'), ns) is not None:
        teiseries = createchild('series', parent=e)
        moveinto('series', oldparent=e, newparent=teiseries)
        moveinto('volume', oldparent=e, newparent=teiseries)
        renameto(e, oldname='series', newtagname='title',
                 attr='level', value='s')
        renameto(e, oldname='volume', newtagname='biblScope',
                 attr='unit', value='volume')


def biblio():
    ''' Translate bibliography from biblio.xml (export of JabRef, BibTeXML format)
        to TEI format and append it to to <listBibl> in chronicon.xml
        '''

    # Input bib entries:
    in_tree = etree.parse('%s%s' % (xmlpath, biblio_file))
    entries = in_tree.findall('.//b:%s' % ('entry'), ns)

    # Import chronicon.xml
    chronicon_path = '%s%s' % (xmlpath, chronicon_output_file)
    out_tree = etree.parse('%s%s' % (xmlpath, chronicon_path))
    list_bibl = out_tree.find('.//t:%s' % ('listBibl'), ns)

    for entry in entries:
        for tag in list_remove:
            remove_element(tag, entry)
        if entry.find('.//b:%s' % ('book'), ns) is not None:
            book(entry)
        elif entry.find('.//b:%s' % ('inproceedings'), ns) is not None:
            inproceedings(entry)
        entry.tag = '{%s}biblStruct' % ns['t']
        # Replace @id with @xml:id
        xmlid = entry.get('id')
        entry.attrib.pop('id')
        entry.set('{%s}id' % ns['xml'], xmlid)

        descendants = entry.findall('.//b:*', ns)
        for d in descendants:
            change_ns(d)
        list_bibl.append(entry)

    in_tree = etree.parse('%s%s' % (xmlpath, biblio_file))

    # Write tree to output file template.xml
    # (warning: I'm overwriting the file)
    out_tree.write(chronicon_path,
                   encoding='UTF-8', method='xml',
                   pretty_print=True, xml_declaration=True)
