# Romualdus Project

This is the code (mostly TEI XML and Python) of my digital scholarly edition of the _Chronicon_ by Romualdus Salernitanus (or Romualdus Guarna), XII century.


## Repository structure

- `csv` folder includes CSV tables:
    - tables of signs for each manuscript (MS) transcribed at the graphematic layer, such as `a-tos.csv` for MS A and `b-tos.csv` for MS B
    - tables of abbreviation combinations for those MSS (manuscripts), such as `a-combi.csv` for MS A and `b-combi.csv` for MS B
    (note that the transcription has been done at the graphematic layer only for the first paragraphs of MSS A, B and C;
    MS A has been entirely transcribed at the alphabetic layer only; MSS B and C have not transcribed except for the first paragraphs)

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


## XML files

Files in the `xml` folder:

### Transcription and OCR files

Original files:

- `a.xml`: complete transcription of MS A
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

- `m1.xml`: the result of the (JuxtaCommons.org) collation between `g-simple.xml` and `a1-simple.xml`
- `m2-alfa.xml`: result of collation between 
- `m2-bravo.xml`: result of collation between
- `m2-charlie.xml`: result of collation between

`a2-sorted-2-alfa.xml` and `bonetti-2-alfa.xml`
`a2-sorted-2-bravo.xml` and `bonetti-2-bravo.xml`
`a2-sorted-2-charlie.xml` and `bonetti-2-charlie.xml`




- `m1-par.xml`: 

- `m1-par-out.xml`: 
- `m2-alfa-par.xml`: 
- `m2-alfa-par-out.xml`: 

- `m2-bravo-par.xml`: 
- `m2-bravo-par-out.xml`: 

- `m2-charlie-par.xml`: 
- `m2-charlie-par-out.xml`: 