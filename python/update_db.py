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
# Change type to substantial (app has 2 children)
if arg == '-m2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, type, xmlid) '
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
            's',   # field 'type' (substantial)
            xmlid))  # field 'xmlid' (<p @xml:id> value)


# Print reading is OK.
# Only set type to orthography (app has 2 children)
elif arg == '-o2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, type, xmlid) '
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
            'o',     # field 'type' (orthography)
            'all'))  # field 'xmlid' (in all paragraphs)


# Print reading is OK.
# Only set type to orthography and subtype to double
# (app has 2 children)
elif arg == '-double2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, type, subtype, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?);')

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
            'o',     # field 'type' (orthography)
            'double',  # field 'subtype' (double)
            'all'))  # field 'xmlid' (in all paragraphs)


# Print reading is OK.
# Only set type to orthography and subtype to h
# (app has 2 children)
elif arg == '-h2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, type, subtype, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?);')

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
            'o',     # field 'type' (orthography)
            'h',  # field 'subtype' (h)
            'all'))  # field 'xmlid' (in all paragraphs)


# Print reading is OK.
# Only set type to substantial (app has 2 children)
#   (This case can be used to insert the app in the DB,
#    so it will be confirmed with @cert=high, or to change
#    subtype e.g. from "tc" to "y")
elif arg == '-s2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, type, xmlid) '
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
            's',     # field 'type' (substantial)
            xmlid))  # field 'xmlid' (<p @xml:id> value)


# Print reading is OK.
# Only set type to substantial (app has 3 children)
#   (so I can possibly edit the DB record later)
elif arg == '-s3':

    sqlite_query = ('INSERT INTO decisions3 (origin, action, '
                    'print, msa, mso, type, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?);')

    # (Re-)interpret text file lines
    printrdg = lines[0]
    msardg = lines[1]
    msordg = lines[2]
    xmlid = lines[3]

    # Update DB table
    cur.execute(
        sqlite_query, (
            'm',     # field 'origin' in the DB table (manual)
            't',     # field 'action' (only change type)
            printrdg,  # field 'print' (print reading)
            msardg,   # field 'msa' (MS reading)
            msordg,   # field 'mso' (MS reading)
            's',     # field 'type' (substantial)
            xmlid))  # field 'xmlid' (<p @xml:id> value)

# Print reading is OK.
# Set type to orthographic (app has 3 children)
elif arg == '-o3':

    sqlite_query = ('INSERT INTO decisions3 (origin, action, '
                    'print, msa, mso, type, xmlid) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?);')

    # (Re-)interpret text file lines
    printrdg = lines[0]
    msardg = lines[1]
    msordg = lines[2]
    xmlid = lines[3]

    # Update DB table
    cur.execute(
        sqlite_query, (
            'm',     # field 'origin' in the DB table (manual)
            't',     # field 'action' (only change type)
            printrdg,  # field 'print' (print reading)
            msardg,   # field 'msa' (MS reading)
            msordg,   # field 'mso' (MS reading)
            'o',     # field 'type' (orthographic)
            xmlid))  # field 'xmlid' (<p @xml:id> value)


# Choose MS reading instead of print reading.
# Set type to orthograph (app has 2 children)
elif arg == '-mo2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, type, xmlid) '
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
            'o',     # field 'type' (orthography)
            'all'))  # field 'xmlid' (in all paragraphs)


# Print reading is OK. - new
# Only set type to transposition
# (app has 2 children)
elif arg == '-t2':
    sqlite_query = ('INSERT INTO decisions2 (origin, action, '
                    'print, ms, type, xmlid) '
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
            't',     # field 'type' (transposition)
            xmlid))  # field 'xmlid' (<p @xml:id> value)


# Set 1 to field 'checked' in DB table 'paragraphs'
elif arg == '-p':
    sqlite_query = ('UPDATE paragraphs SET checked=1 '
                    'WHERE xmlid=?;')

    # Interpret text file lines
    xmlid = lines[0]

    # Update DB table
    cur.execute(sqlite_query, (xmlid,))

connection.commit()
cur.close()
if (connection):
    connection.close()

# Empty text file
open(input_text_file, 'w').close()
