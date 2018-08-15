# About this file

Version history of files with filename starting with garufi_ocr_21-163 (the OCR from Garufi, pages 21-163). The headers here refer to the file version appended at the end of the filename. The extension of the files may be .txt or .xml.

# 1.0

Reviewed OCR. There are some supplied and some surplus tags, but not used correctly.

# 1.1

Regularized the use of surplus and supplied. Now <pb>s are always out of <p>s.

# 2.0

The output of script ocr.py. Its input was version 1.1. I edited by hand the wrong points that made the output non-valid XML. I added the Garufi header, <text> and <body>. First version with .xml (not .txt) extension.

I created a symbolic link n.xml (for "n"ew Garufi scan) in the XML folder, to make python scripts run.
That link will always point to the latest version of the garufi_ocr_21-163 file.

<milestone type="mass_ocr_21-163_starts_here" ed="#g"/>
to 
<milestone type="mass_ocr_21-163_ends_here" ed="#g"/>
After making  all further markup (numerals etc.,) and checks (e.g. check <hi> and <rs>), I'll merge its content into g.xml.

# 3.0

Removed some useless line beginnings (entities).

# 3.1

Check <rs> and <hi> with the help of names.py.

# 3.2

Checked <rs> and <hi> with names.py, function chechrsandhi()

# 3.3

Manually corrected xml errors. Now file validates.

# 3.4

Checked <rs> and <hi> with names.py, function chechrsandhi() again

# 3.5

Checked <rs> and <hi> with names.py, function chechrsandhi() again

# 3.6

Checked <rs> with names.py, function checkrs(). This function checks names marked that are with <rs> at some point of the text, but not marked in other points. I checked words that must always be marked with <rs> and words that never must be markedwith <rs>. Still to do: words that can be or not be marked with <rs>.

# 3.7

Checked <rs> with names.py, function checkrs(). Checked words that can be or not be marked with <rs>.

# 3.8

Checked <rs> with names.py, function checkrs(). Checked words that can be or not be marked with <rs> (again)

# 4.0

Pre-processed files to identify Roman numerals. I am trying to put all numerals with more than one letter in all uppercase (i.e. not xxx but XXX). I marked by hand the numerals with one letter only (I, V, X, L, C, D, M).

# 4.1

This is the output of function wrapNumerals() of numerals.py. Still to be checked for cases such as
    cerca </num>&nbsp;
(i.e. with an entity right before or right after <num>) or with a <num> inside another <num>.
