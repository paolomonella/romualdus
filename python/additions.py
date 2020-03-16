#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
''' This module includes one big function, extracting/dividing
    the layers from the TEI XML source file. See the documentation
    of the function below for details.
    '''

from lxml import etree
from myconst import xmlpath, ns, dbpath
import sqlite3
from my_database_import import scrub, import_table

goodplaces = ['marginandfooter', 'footer', 'addedfolios', 'margin']


def onlytag(tag_with_ns):
    return tag_with_ns.split('}')[1]


class myTree:

    def __init__(self, siglum, quiet=False):
        self.siglum = siglum
        self.xmlfile = '%s%s.xml' % (xmlpath, siglum)
        self.tree = etree.parse(self.xmlfile)
        self.body = self.tree.find('.//t:body', ns)
        # pars = body.findall('.//t:p', ns)
        self.adds = self.body.findall('.//t:add', ns)
        self.additions = []
        for a in self.adds:
            self.xmlid = '{%s}id' % ns['xml']
            # my_xmlid = a.get('{%s}id' % ns['xml'])
            my_xmlid = a.get(self.xmlid)
            if my_xmlid is not None and 'add100' in my_xmlid:
                #  xmlid = '{http://www.w3.org/XML/1998/namespace}id'
                #  if 'add100' in a.get(xmlid):
                self.additions.append(a)

    def check_additions(self, quiet=False):
        for a in self.additions:
            parent = a.getparent()
            # print(parent.tag)
            children = [onlytag(child.tag) for child in parent]
            oktags = ['link', 'milestone', 'note']
            for tag in children:
                if tag in oktags:
                    children.remove(tag)
            for tag in children:
                if tag in oktags:
                    children.remove(tag)
            if len(children) > 0 and children != ['add']:
                print(('Suspicious paragraph (including more than '
                       'one <app>: {}, with children {}').format(
                           parent.get(self.xmlid),
                           children))

    def par_id_list(self, quiet=False):
        id_list = []
        for a in self.additions:
            parent = a.getparent()
            my_xmlid = parent.get(self.xmlid)
            id_list.append(my_xmlid)
        return id_list  # This is a list

    def populate_db_table(self,
                          my_dbname='romualdus.sqlite3',
                          my_table_name='hand2_additions'):

        connection = sqlite3.connect('%s%s' % (dbpath, my_dbname))
        connection.row_factory = sqlite3.Row
        cur = connection.cursor()
        scrubbed_table_name = scrub(my_table_name)
        my_list = self.par_id_list()
        sqlite_query = 'INSERT INTO %s VALUES(?);' % (scrubbed_table_name)
        print(sqlite_query)
        # cur.executemany(sqlite_query, )
        # cur.executemany(sqlite_query, self.par_id_list())
        for i in my_list:
            print(i)
            cur.execute(sqlite_query, (i,))
        cur.close()
        connection.commit()
        if (connection):
            connection.close()

    def populate_db_table2(self,
                           my_list,
                           my_dbname='romualdus.sqlite3',
                           my_table_name='hand2_additions'):
        connection = sqlite3.connect('%s%s' % (dbpath, my_dbname))
        connection.row_factory = sqlite3.Row
        cur = connection.cursor()
        # sqlite_query = 'INSERT INTO %s(add_xml_id) VALUES(?);' % \
        sqlite_query = \
            'UPDATE hand2_additions SET add_xml_id=? WHERE _rowid_=?;'
        # cur.executemany(sqlite_query, )
        # cur.executemany(sqlite_query, self.par_id_list())
        for x in my_list:
            my_index = my_list.index(x) + 1
            print(my_index, x)
            cur.execute(sqlite_query, (x, my_index))
        cur.close()
        connection.commit()
        if (connection):
            connection.close()

    def populate_db_table3(self,
                           my_dbname='romualdus.sqlite3',
                           my_table_name='hand2_additions'):
        connection = sqlite3.connect('%s%s' % (dbpath, my_dbname))
        connection.row_factory = sqlite3.Row
        cur = connection.cursor()
        # sqlite_query = 'INSERT INTO %s(add_xml_id) VALUES(?);' % \
        my_list = self.par_id_list()
        sqlite_query = 'INSERT INTO hand2_additions VALUES(?, ?);'
        # cur.executemany(sqlite_query, )
        # cur.executemany(sqlite_query, self.par_id_list())
        for add in self.additions:
            par_id = add.getparent().get(self.xmlid)
            add_id = add.get(self.xmlid)
            cur.execute(sqlite_query, (par_id, add_id))
            print(par_id, add_id)
        cur.close()
        connection.commit()
        if (connection):
            connection.close()

    def check_add100(self,
                     my_dbname='romualdus.sqlite3',
                     my_table_name='hand2_additions'):
        table = import_table(dbpath, my_dbname, my_table_name)
        for r in table:
            if r[1] != r[0] + 'add100':
                print(r[1])
            else:
                print('ok', end = ' ')

# a2
tree = myTree('a2')
# tree.par_id_list()
tree.check_add100()
# tree.populate_db_table3()

sweet_list = [
    'g179.15-180.12add100',
    'g180.13-180.15add100',
    'g181.1-181.1add100',
    'g181.2-181.5add100',
    'g181.6-181.10add100',
    'g181.10-181.11add100',
    'g181.12-182.19add100',
    'g183.1-184.6add100',
    'g184.7-184.9add100',
    'g184.10-185.7add100',
    'g186.6-186.7add100',
    'g186.8-186.8add100',
    'g186.9-186.9add100',
    'g187.5-187.8add100',
    'g187.11-187.14add100',
    'g188.5-188.7add100',
    'g188.12-190.8add100',
    'g191.3-191.5add100',
    'g195.6-195.8add100',
    'g198.4-198.5add100',
    'g198.12-198.13add100',
    'g198.16-198.17add100',
    'g199.1-199.8add100',
    'g200.17-200.21add100',
    'g201.19-201.20add100',
    'g202.5-202.10add100',
    'g202.11-203.2add100',
    'g203.6-203.6add100',
    'g206.13-206.17add100',
    'g208.1-208.9add100',
    'g210.23-210.24add100',
    'g211.15-211.17add100',
    'g212.5-212.9add100',
    'g212.10-212.11add100',
    'g212.12-212.16add100',
    'g213.1-213.8add100',
    'g214.12-215.3add100',
    'g214.14-215.3add100',
    'g219.3-219.4add100',
    'g214.n8-215.n14add100',
    'g216.n10-217.n1add100',
    'g217.n4-217.n10add100',
    'g218.n16-218.n23add100',
    'g219.n1-219.n13add100',
    'g217.n10-218.n16add100',
    'g234.n1-236.n10add100',
    'g258.1-258.7surplusadd100'
    ]

# bonetti
# tree = myTree('bonetti')
