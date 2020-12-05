#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import sqlite3


def scrub(table_name):
    ''' Source:
        https://stackoverflow.com/questions/3247183/
        variable-table-name-in-sqlite'''
    # scrub('); drop tables --')  # returns 'droptables'
    my_out_string = ''
    for chr in table_name:
        if chr.isalnum() or chr == '_':
            my_out_string = my_out_string + chr
    # return ''.join(chr for chr in table_name if chr.isalnum())
    return my_out_string


def import_table(my_dbpath, my_dbname, my_table_name):
    ''' Import a whole table into a Row object.
        See documentation on this data type in
        https://docs.python.org/3/library/sqlite3.html#sqlite3.Row
        '''
    connection = sqlite3.connect('%s%s' % (my_dbpath, my_dbname))
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    scrubbed_table_name = scrub(my_table_name)
    sqlite_select_query = 'SELECT * FROM %s;' % (scrubbed_table_name)
    cur.execute(sqlite_select_query)
    my_list = cur.fetchall()
    cur.close()
    if (connection):
        connection.close()
    return my_list
