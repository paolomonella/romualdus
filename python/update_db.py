#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import sqlite3
import myconst
import sys  # To accept arguments

# Get arguments
arg = sys.argv[1]

# Connect to DB
connection = sqlite3.connect('%s%s' % (myconst.dbpath, myconst.dbname))
cur = connection.cursor()

# Read text file
input_text_file = '%s%s' % (myconst.xmlpath,
                            myconst.update_db_tempfile)
with open(input_text_file, 'r') as f:
    lines = [line[:-1] for line in f.readlines()]


if arg == 'm2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, app_type, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?);')

    # Interpret text file lines
    printrdg = lines[0]
    msrdg = lines[1]
    xmlid = lines[2]

    # Update DB table
    cur.execute(sqlite_query, ('m', 'm',
                               printrdg, msrdg, 's', xmlid))

elif arg == 'o2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, app_type, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?);')

    # Interpret text file lines
    printrdg = lines[0]
    msrdg = lines[1]
    xmlid = lines[2]

    # Update DB table
    cur.execute(sqlite_query, ('m', 't',
                               printrdg, msrdg, 'o', 'all'))

connection.commit()
cur.close()
if (connection):
    connection.close()

# Empty text file
open(input_text_file, 'w').close()
