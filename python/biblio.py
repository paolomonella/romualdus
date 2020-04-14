#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module imports the bibliography from a file
    in BibTeXML format to the 'front' element of the
    final XML product of the edition (chronicon.xml)
    '''

from lxml import etree
from myconst import xmlpath, ns, biblio_file, chronicon_output_file

list_remove = ['language', 'langid', 'lccn', 'keywords', 'bibtexkey',
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
    pages.text = pages.text.replace('--', '-')
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

    if (e.find('.//b:%s' % ('series'), ns) is not None or
            e.find('.//b:%s' % ('journal'), ns) is not None):
        teiseries = createchild('series', parent=e)
        moveinto('series', oldparent=e, newparent=teiseries)
        renameto(e, oldname='series', newtagname='title',
                 attr='level', value='s')
        moveinto('volume', oldparent=e, newparent=teiseries)
        renameto(e, oldname='volume', newtagname='biblScope',
                 attr='unit', value='volume')

    url = e.find('.//b:%s' % ('url'), ns)
    if url is not None:
        e.append(url)
    renameto(e, oldname='url', newtagname='ref',
             attr='type', value='url')

    for tag in list_remove:
        remove_element(tag, e)


def miscellaneous(e, entrytype):

    miscellaneous = e.find('.//b:%s' % (entrytype), ns)
    imprint = createchild('imprint', parent=miscellaneous)
    analytic = createchild('analytic', parent=e)
    e.insert(0, analytic)

    moveinto('publisher', oldparent=e, newparent=imprint)

    moveinto('year', oldparent=e, newparent=imprint)
    renameto(e, oldname='year', newtagname='date')

    moveinto('location', oldparent=e, newparent=imprint)
    renameto(e, oldname='location', newtagname='pubPlace')

    moveinto('pages', oldparent=e, newparent=imprint)
    pages = e.find('.//b:%s' % ('pages'), ns)
    if pages is not None:
        process_pages(e, pages)

    renameto(e, oldname=entrytype, newtagname='monogr')

    moveinto('author', oldparent=e, newparent=analytic)
    moveinto('title', oldparent=e, newparent=analytic)

    renameto(e, oldname='booktitle', newtagname='title',
             attr='level', value='m')

    if (e.find('.//b:%s' % ('series'), ns) is not None or
            e.find('.//b:%s' % ('journal'), ns) is not None):
        teiseries = createchild('series', parent=e)
        moveinto('series', oldparent=e, newparent=teiseries)
        renameto(e, oldname='series', newtagname='title',
                 attr='level', value='s')
        moveinto('volume', oldparent=e, newparent=teiseries)
        renameto(e, oldname='volume', newtagname='biblScope',
                 attr='unit', value='volume')

    url = e.find('.//b:%s' % ('url'), ns)
    if url is not None:
        e.append(url)
    renameto(e, oldname='url', newtagname='ref',
             attr='type', value='url')


def article(e):

    article = e.find('.//b:%s' % ('article'), ns)
    imprint = createchild('imprint', parent=article)
    analytic = createchild('analytic', parent=e)
    e.insert(0, analytic)

    moveinto('publisher', oldparent=e, newparent=imprint)

    moveinto('year', oldparent=e, newparent=imprint)
    renameto(e, oldname='year', newtagname='date')

    moveinto('location', oldparent=e, newparent=imprint)
    renameto(e, oldname='location', newtagname='pubPlace')

    moveinto('volume', oldparent=e, newparent=imprint)
    renameto(e, oldname='volume', newtagname='biblScope',
             attr='unit', value='vol')

    moveinto('number', oldparent=e, newparent=imprint)
    renameto(e, oldname='number', newtagname='biblScope',
             attr='unit', value='issue')

    moveinto('pages', oldparent=e, newparent=imprint)
    pages = e.find('.//b:%s' % ('pages'), ns)
    if pages is not None:
        process_pages(e, pages)

    renameto(e, oldname='article', newtagname='monogr')

    moveinto('author', oldparent=e, newparent=analytic)
    moveinto('title', oldparent=e, newparent=analytic)

    renameto(e, oldname='journal', newtagname='title',
             attr='level', value='j')

    if e.find('.//b:%s' % ('series'), ns) is not None:
        teiseries = createchild('series', parent=e)
        moveinto('series', oldparent=e, newparent=teiseries)
        moveinto('volume', oldparent=e, newparent=teiseries)
        renameto(e, oldname='series', newtagname='title',
                 attr='level', value='s')
        renameto(e, oldname='volume', newtagname='biblScope',
                 attr='unit', value='volume')

    url = e.find('.//b:%s' % ('url'), ns)
    if url is not None:
        e.append(url)
    renameto(e, oldname='url', newtagname='ref',
             attr='type', value='url')


def biblio():
    ''' Translate bibliography from biblio.xml (export of JabRef, BibTeXML format)
        to TEI format and append it to to <listBibl> in chronicon.xml
        '''

    # Input bib entries:
    in_tree = etree.parse('%s%s' % (xmlpath, biblio_file))
    entries = in_tree.findall('.//b:%s' % ('entry'), ns)

    # Import chronicon.xml
    chronicon_path = '%s%s' % (xmlpath, chronicon_output_file)
    out_tree = etree.parse(chronicon_path)
    list_bibl = out_tree.find('.//t:%s' % ('listBibl'), ns)

    for entry in entries:
        for tag in list_remove:
            remove_element(tag, entry)
        if entry.find('.//b:%s' % ('book'), ns) is not None:
            book(entry)
        elif entry.find('.//b:%s' % ('inproceedings'), ns) is not None:
            miscellaneous(entry, entrytype='inproceedings')
        elif entry.find('.//b:%s' % ('inbook'), ns) is not None:
            miscellaneous(entry, entrytype='inbook')
        elif entry.find('.//b:%s' % ('article'), ns) is not None:
            article(entry)
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
