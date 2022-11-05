# Romualdus Project

[![DOI](https://zenodo.org/badge/133493153.svg)](https://zenodo.org/badge/latestdoi/133493153)

This repository includes the source code (mostly TEI XML and Python) of the digital scholarly edition
of the _Chronicon_ by Romualdus Salernitanus (Romualdus Guarna, XII century)
edited by [Paolo Monella](http://www.paolomonella.it) within the [ALIM Project](http://it.alim.unisi.it/) (2017-2020).

The home page of this edition is [http://www.paolomonella.it/romualdus](http://www.paolomonella.it/romualdus)

The _textus constitutus_ of the edition, including an introduction and some textual statistics,
is in the TEI XML P5 file `XML/chronicon.xml` in this repository.

The edition has been published in the ALIM digital library at <http://alim.unisi.it/dl/resource/299> in 2020.
At this URL you can read a HTML visualization of the edition and download it in XML (the original source),
HTML, PDF and plain text format.


## Sigla and editions

- Manuscripts
	- A: [Vaticanus Latinus 3973](http://digi.vatlib.it/view/MSS_Vat.lat.3973)
	- B: [Biblioteca Apostolica Vaticana, Archivio di San Pietro, E 22](http://digi.vatlib.it/mss/detail/Arch.Cap.S.Pietro.E.22)
	- C: [Paris, Bibliothèque Nationale, Latinus 4933](http://archivesetmanuscrits.bnf.fr/ark:/12148/cc63823p),
	- O (Schwartz's Aa): [Ottobonianus Latinus 2940](https://digi.vatlib.it/mss/detail/Ott.lat.2940),
		1st fragment, i.e. folios 16r-18v = 168,5-188,1 of Garufi's edition
- Print editions
	- Garufi: _Romualdi Salernitani Chronicon (A.m. 130-A.C. 1178)_, ed. by 
		Garufi, Carlo Alberto, Città di Castello, S. Lapi 1914
		(Rerum italicarum scriptores: Nuova edizione, 7.1)
	- Bonetti: _Romualdo II Guarna, Chronicon_, ed. by 
		Bonetti, Cinzia, Salerno, Avagliano 2001
		(ISBN 9788883090561)

## Repository structure

- `csv` folder includes CSV tables:
    - tables of signs for each manuscript (MS) transcribed at the graphematic layer,
	such as `a-tos.csv` for MS A and `b-tos.csv` for MS B
    - tables of common abbreviation combinations for those MSS (manuscripts),
	such as `a-combi.csv` for MS A and `b-combi.csv` for MS B
    (note that the transcription has been done at the graphematic layer only
	for the first paragraphs of MSS A, B and C;
    	MS A has been entirely transcribed at the alphabetic layer only;
	MSS B and C have not transcribed except for the first paragraphs)

- `db` folder includes the Sqlite3 database file `romualdus.sqlite3` with tables on variant types and subtypes, textual decisions and on collation

- `fonts` folder includes fonts used for HTML visualizatoin
    (see file `index.html` and folder `html` below)

- `html` folder includes HTML visualization of MSS transcriptions at the graphematic/alphabetic layer
    - transcription at the graphematic layer has only been created for the first paragraphs of MSS A, B and C, then abandoned
    
- `img` folder in my local version of this repository includes links to PDF digital facsimiles of MSS A and O
    - those PDF files are not available online due to (questionable) copyright restrictions
    
- `python` folder includes the Python 3 code used in this project

- `scan/ocr` folder includes .txt files resulting of the OCR, at different stages of manual revision

- `xml` folder includes the XML source files


- Other files in the root of the repository:
    - `index.html`: the home page of the [project website](http://www.paolomonella.it/romualdus), including
        - a brief MSS description
        - links to the graphematic/alphabetic layer transcription visualization
        
    - `romualdus.png`: a screenshot to be possibly used in the Website

    - `stylesheet.css`: CSS stylesheet associated to `index.html`


## Files in the `xml` folder

### Transcription and OCR files

Original files (all .xml files are valid TEI P5 XML):

- `a.xml`: complete TEI XML transcription of MS A
    - only the first paragraphs have been transcribed at the graphematic layer
    - the other have been transcribed at the alphabetic layer only
    - for paragraphs from g116.6-118.8 through g163.1-163.5 I only transcribed major variants
    - Garufi's edition was the collation base until (and including) paragraph g163.1-163.5
    - Bonetti's edition was the collation base for the collation from (and including) paragraph g163.6-163.7
- `o.xml`: transcription of the fragment of MS O (Schwartz's Aa) including the text of the "short version" of the Chronicon,
    i.e. paragraphs g168.5-168.7 through g185.8-186.5
    - the text has been transcribed at the alphabetic layer
    - Bonetti's edition was the collation base
- `g.xml`: reviewed OCR of Garufi's edition (1914)
- `bonetti.xml`: reviewed OCR of Bonetti's edition (only the critical text, that Bonetti drew from Garufi 1914 and Arndt 1866),
    reporting only the second part of the Chronicon (from Garufi page 163, i.e. par. g163.6-163.7,
    to the end of the work, including the Peace of Venice)
- `b.xml`: graphematic transcription of the first paragraphs of MS B
- `c.xml`: graphematic transcription of the first paragraphs of MS C

Split and sorted versions of `a.xml`:

- `a.xml` was split by script `python/splitter.py` into two chunks to facilitate collation:
    - `a1.xml` to be collated with `g.xml`
    - `a2.xml` to be collated with `bonetti.xml` (paragraphs g163.6-163.7 to the end of the work, including the Peace of Venice)
    - `a2-sorted.xml` is a version of `a2.xml` (created by script `python/sort_a2.py`) in which the order of paragraphs
    matches that of Bonetti's edition, to facilitate collation
- `a2-sorted.xml` and `bonetti.xml` were further split (again, by script `python/splitter.py`)
    into three chunks, reporting the same portions of the Chronicon, to facilitate collation:
    - `a2-sorted-2-alfa.xml` and `bonetti-2-alfa.xml`: paragraphs g163.6-163.7 through g167.4-168.4, for which only Bonetti and A must be collated
    - `a2-sorted-2-bravo.xml` and `bonetti-2-bravo.xml`: par. g168.5-168.7 through g185.8-186.5, i.e. the part for which Bonetti, A and O must be collated
    - `a2-sorted-2-charlie.xml` and `bonetti-2-charlie.xml`: par. g186.6-186.7 to the end of the work, inlcuding the Peace of Venice,
    for which only Bonetti and A must be collated

Those files have been further processed by a number of scripts in the `python` folder (mainly `python/simplify_markup_for_collation.py`)
to produce simplified versions that have been fed to JuxtaCommons.org for collation. Most TEI XML markup was removed. For paragraph tags,
&lt; and &gt; were replaced with brackets.
The simplified version of each of the above file has a `-simple` suffix. E.g.:

- `a1-simple.xml` is the simplified version of `a1.xml`
- `a2-sorted-2-bravo-simple.xml`, of `a2-sorted-2-bravo.xml`
- `bonetti-2-charlie-simple.xml`, of `bonetti-2-charlie.xml` etc.

### Collation files

Direct ouput of JuxtaCommons.org (later edited manually to improve the result):

- `m1.xml`: the result of the (JuxtaCommons.org) collation between
	`g-simple.xml` and `a1-simple.xml`
- `m2-alfa.xml`: result of collation between 
	`a2-sorted-2-alfa-simple.xml` and `bonetti-2-alfa-simple.xml`
- `m2-bravo.xml`: result of collation between
	`a2-sorted-2-bravo-simple.xml` and `bonetti-2-bravo-simple.xml`
- `m2-charlie.xml`: result of collation between
	`a2-sorted-2-charlie-simple.xml` and `bonetti-2-charlie-simple.xml`


Script `python/post_process_juxta_commons_file.py` then processed those files
to produce XML well-formed files in which the brackets for paragraph tags were re-transformed
to &lt; and &gt;. The resulting files were respectively:

- `m1-par.xml` 
- `m2-alfa-par.xml` 
- `m2-bravo-par.xml` 
- `m2-charlie-par.xml` 

Finally, with the help of script `python/philologist.py' and other modules imported by it
(e.g. `python/variant_subtype.py`, to detect the variant subtype), I brought about the
_constitutio textus_, by storing information in the `db/romualdus.sqlite3` database.
The output files for each chunk were:

- `m1-par-out.xml` 
- `m2-alfa-par-out.xml` 
- `m2-bravo-par-out.xml` 
- `m2-charlie-par-out.xml` 

Finally, script `python/m_unifier.py` 
and re-unified the latter files, attaching their content to a
template teiHeader taken from file `xml/teiHeader_template.xml`. It thus produced file
`chronicon.xml`, the _textus constitutus_ of the edition.



## Python code in the `python` folder


Transcription and OCR:

- `names.py`: check named entities in transcription/OCR files
- `non_rs.txt`: a list of words that are not named entities in transcription/OCR files
- `numerals.py`: mark numerals in TEI XML and relative checks
- `ocr.py`: post-process OCR txt files to produce TEI XML
- `romanranges`: text files to help the processing of Roman numerals
- `rs_bonetti_all.txt`, `rs_garufi_pp_1-20.txt`, `rs.txt`: lists of named entities in transcription/OCR files


Initial attempts to collate transcriptions with CollateX:

- `collatex_for_romualdus_xml.py`: collate transcriptions with CollateX
- `xmlns_collatex`: originally used to store versions of the XML files compatible with CollateX


Visualization of MS transcriptions at the graphematic layer:

- `detect_combinations.py`: find abbreviation combinations in transcriptions and compare them with the relevant CSV file
- `id_fixer.py`: check that transcriptions of MSS A, B and C all have the same TEI XML paragraph tags with the same `xml:id`'s
- `layers.py`: extract/divide the transcription layers from the TEI XML source file, producing HTML code for visualization
- `lint.py`: check that only graphemes in the table of signs have been used in graphematic transcription
- `other.py`: modules utilized to visualize MS transcriptions at the graphematic layer
- `output.py`: produce HTML visualizations of MS transcriptions at the graphematic layer
- `replace.py`: produce the alphabetic representation of sequences of graphemes (for MS transcriptions at the graphematic layer)
- `visualization.py`: trigger for modules producing a HTML visualization of MS transcriptions at the graphematic layer

Pre-processing of transcription/OCR files before JuxtaCommons.org collation:

- `bonetti_and_o_splitter.py`: split transcription/OCR files of the second part of the work (see XML file description above)
- `entitize.py`: replace long tags with XML entities
- `simplify_markup_for_collation.py`: simplify TEI XML markup (see XML file description above)
- `sort_a2.py`: re-arrange paragraphs in the second part of the work (see XML file description above)
- `splitter.py`: (see XML file description above)


Post-processing of JuxtaCommons.org collation files:

- `biblio.py`: import bibliography from a BibTeXML file to the 'front' element of chronicon.xml
- `diff`: spreadsheets to check the diffs found by module `variant_subtype.py`
- `juxta.py`: trigger for all other scripts (pre-processing before collation and post-procesing after collation)
- `m_unifier.py`: re-unify collation files (see XML file description above)
- `my_database_import.py`: function to easily import sqlite3 DB tables
- `renew_collation_on_paragraph.py`: repeat collation of a paragraph with CollateX (I planned to use it after JuxtaCommons collation)
- `philologist.py`: assist during the _constitutio textus_, working on collation files and the sqlite3 DB
- `post_process_juxta_commons_file.py`: post-process JuxtaCommons files (see XML file description above)
- `update_db.py`: extract the readings (deriving from `chronicon.xml`) from a temporary text file, then insert them in the DB
- `variant_subtype.py`: detect the variant subtype (e.g. 'num-num', 'missing-in-print' etc.)


General:

- `itertext.py`: module to easily get all textual content in an XML element
- `myconst.py`: module including global variables to be used by other scripts
- `ripostiglio`: previous versions of Pyhon modules and scripts
- `statistics.py`: create textual statistics and insert them in the `front` element of `chronicon.xml`
- `strip_individual_node.py`: strip an XML node and keep its text and tail textual content
