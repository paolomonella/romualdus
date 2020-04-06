# Romualdus Project

This is the source code (mostly TEI XML and Python) of the digital scholarly edition
of the _Chronicon_ by Romualdus Salernitanus (Romualdus Guarna, XII century) from codices
[Vaticanus Latinus 3973 (A)](http://digi.vatlib.it/view/MSS_Vat.lat.3973), [Biblioteca Apostolica Vaticana, Archivio di San Pietro, E 22 (B)](http://digi.vatlib.it/mss/detail/Arch.Cap.S.Pietro.E.22) and [Paris, Bibliothèque Nationale, Latinus 4933 (C)](http://archivesetmanuscrits.bnf.fr/ark:/12148/cc63823p), edited by [Paolo Monella](http://www.unipa.it/paolo.monella) within the [ALIM Project](http://it.alim.unisi.it/) (2017-2020).


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
    - `index.html`: the home page of the [http://www1.unipa.it/paolo.monella/romualdus/](project Website), including
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


- `bonetti_and_o_splitter.py`: split transcription/OCR files of the second part of the work (see XML file description above)
- `collatex_for_romualdus_xml.py`: collate transcriptions with CollateX
- `detect_combinations.py`: find abbreviation combinations in transcriptions and compare them with the relevant CSV file
- `diff`: spreadsheets to check the diffs found by module `variant_subtype.py`
- `entitize.py`: replace long tags with XML entities
- `id_fixer.py`: check that transcriptions of MSS A, B and C all have the same TEI XML paragraph tags with the same `xml:id`'s
- `itertext.py`: module to easily get all textual content in an XML element
- `juxta.py`: trigger for all other scripts (pre-processing before collation and post-procesing after collation)
- `layers.py`: extract/divide the transcription layers from the TEI XML source file, producing HTML code for visualization
- `lint.py`: check that only graphemes in the table of signs have been used in graphematic transcription
- `m_unifier.py`: re-unify collation files (see XML file description above)
- `myconst.py`: module including global variables to be used by other scripts
- `my_database_import.py`: function to easily import sqlite3 DB tables
- `names.py`: check named entities in transcription/OCR files
- `non_rs.txt`: a list of named entities in transcription/OCR files
- `numerals.py`: mark numerals in TEI XML and relative checks
- `ocr.py`: post-process OCR txt files to produce TEI XML
- `other.py`: modules utilized to visualize MS transcriptions at the graphematic layer
- `output.py`: produce HTML visualizations of MS transcriptions at the graphematic layer
- `philologist.py`: assist during the _constitutio textus_, working on collation files and the sqlite3 DB
- `post_process_juxta_commons_file.py`: post-process JuxtaCommons files (see XML file description above)
- `renew_collation_on_paragraph.py`: 
- `replace.py`: 
- `replace.pyc`: 
- `ripostiglio`: 
- `romanranges`: 
- `rs_bonetti_all.txt`: 
- `rs_garufi_pp_1-20.txt`: 
- `rs.txt`: 
- `simplify_markup_for_collation.py`: 
- `sort_a2.py`: 
- `splitter.py`: 
- `strip_individual_node.py`: 
- `update_db.py`: 
- `variant_subtype.py`: 
- `visualization.py`: 
- `xmlns_collatex`: 
