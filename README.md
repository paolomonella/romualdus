# Romualdus Project

This is the code (mostly TEI XML and Python) of my digital scholarly edition of the _Chronicon_ by Romualdus Salernitanus (or Romualdus Guarna), XII century.

You can read the (ongoing) edition in http://www1.unipa.it/paolo.monella/romualdus/index.html

## XML files

a.xml
Transcription of MS A

b.xml
Transcription of MS B

c.xml
Transcription of MS C

g.xml
OCR from the Garufi edition

a_juxta.xml
Transcription of MS A, modified to be uploaded to JuxtaCommons for collation. E.g.: numbers are normalized

g_juxta.xml
OCR from the Garufi edition, modified to be uploaded to JuxtaCommons for collation. E.g.: 'j's are transformed into 'i's

input.txt
Temporary file in which the un-checked OCR from Garufi is put, so it can be processed by ocr.py

Romualdus G vs A-punct-and-capital-ignored.xml
Parallel segmentation method output from JuxtaCommons, with punctuation and capitals ignored.
Version 1.0: produced from g.xml and a.xml without further edits.
Version 2.0: produced from a_juxta.xml (numbers normalized) and g_juxta.xml (j's transformed into i's)

temp_g.xml
Temporary file in which the OCR from Garufi is put, so it can be exported into g.xml

x.xml
A copy of g.xml in which I added <app>s 'by hand' with the help of "vim -d"

y--ms_a.xml
A 'foo' copy of a.xml. I gave "vim -d x.xml y--ms_a.xml" to create the <app>s in x.xml

## JuxtaCommons links

# Link JuxtaCommons

G:
http://juxtacommons.org/shares/L1MiI3

A:
http://juxtacommons.org/shares/Y07PP4

Collazione:
http://juxtacommons.org/shares/3BAYYx