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


# Choose MS reading instead of print reading.
# Change subtype to generic-substantial-subtype (app has 2 children)
if arg == 'm2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, subtype, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?);')

    # Interpret text file lines
    printrdg = lines[0]
    msrdg = lines[1]
    xmlid = lines[2]

    # Update DB table
    cur.execute(
        sqlite_query, (
            'm',   # field 'origin' in the DB table (manual)
            'm',   # field 'action' (choose MS reading)
            printrdg,  # field 'print' (print reading)
            msrdg,  # field 'ms' (MS reading)
            's',   # field 'subtype' (generic-substantial-subtype)
            xmlid))  # field 'xmlid' (<p @xml:id> value)


# Print reading is OK.
# Only set subtype to generic-orthography-subtype (app has 2 children)
elif arg == 'o2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, subtype, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?);')

    # Interpret text file lines
    printrdg = lines[0]
    msrdg = lines[1]
    xmlid = lines[2]

    # Update DB table
    cur.execute(
        sqlite_query, (
            'm',     # field 'origin' in the DB table (manual)
            't',     # field 'action' (only change type)
            printrdg,  # field 'print' (print reading)
            msrdg,   # field 'ms' (MS reading)
            'o',     # field 'subtype' (generic-orthography-subtype)
            'all'))  # field 'xmlid' (in all paragraphs)

# Choose MS reading instead of print reading.
# Set subtype to generic-orthography-subtype (app has 2 children)
elif arg == 'mo2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, subtype, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?);')

    # Interpret text file lines
    printrdg = lines[0]
    msrdg = lines[1]
    xmlid = lines[2]

    # Update DB table
    cur.execute(
        sqlite_query, (
            'm',     # field 'origin' in the DB table (manual)
            'm',   # field 'action' (choose MS reading)
            printrdg,  # field 'print' (print reading)
            msrdg,   # field 'ms' (MS reading)
            'o',     # field 'subtype' (generic-orthography-subtype)
            'all'))  # field 'xmlid' (in all paragraphs)

connection.commit()
cur.close()
if (connection):
    connection.close()

# Empty text file
open(input_text_file, 'w').close()
