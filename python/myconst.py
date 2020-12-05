#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

# File paths and folders
xmlpath = '../xml/'
simplifiedpath = '../xml/'
csvpath = '../csv/'
htmlpath = '../html/'
# splitpath = '../xml/split_files_for_collation/'
splitpath = '../xml/'
dbpath = '../db/'
dbname = 'romualdus.sqlite3'
entitize_backup_path = '../xml/ripostiglio/backup/backup_entitization/'
simplifiedsuffix = '-simple'
juxta_par_and_sigla_suffix = '-par'  # outdated?
juxta_par_suffix = '-par'
juxta_sigla_suffix = '-sigla'
update_db_tempfile = 'record.txt'
biblio_file = 'biblio.xml'
tei_header_template = 'teiHeader_template.xml'
chronicon_output_file = 'chronicon.xml'
stats_template = 'stats_template.xml'
stats_filled = 'stats_filled.xml'

# Metatext markers
# The e.text of HTML elements having @class="pb">, @class="garufi" etc.
# should not undergo the GL-to-AL substitutions
# (but their e.tail should):
metatextlist = ['pb', 'cb', 'garufi', 'note']

# XML/HTML namespaces

ns = {
    # For elements without prefix:
    None: 'http://www.tei-c.org/ns/1.0',
    # for TEI XML:
    't': 'http://www.tei-c.org/ns/1.0',
    # for attributes like xml:id:
    'xml': 'http://www.w3.org/XML/1998/namespace',
    # for (X)HTML output
    'h': 'http://www.w3.org/1999/xhtml',
    # for bibtexml, ouput of Jabref
    'b': 'http://bibtexml.sf.net/'}

tei_ns = "{%s}" % ns['t']
xml_ns = "{%s}" % ns['xml']
html_ns = "{%s}" % ns['h']


# Whitespace and punctuation
# These whitespace Unicode chars will be allowed at both GL and AL:
myspace = [' ', '\n', '\t']

# alp = A(lphabetic) L(ayer) P(unctuation).
# These chars are AL punctuation that will nevertheless be allowed also
# in the GL XML code and will be removed when extracting/visualizing the GL
alp = [r'.', ',', ':', ';', '!', '?', "'", '–', '—', '(', ')', '…']

# These chars will be considered legal by the lint at both GL and AL:
legal = myspace + alp
