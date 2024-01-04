#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


''' 


    How to use this script:
    1. Review the OCR before running the script:
        1a. Perform OCR twice with gImageReader
        1b. Use "vim -d x.txt y.txt" to check differences
        1c. Use gespeaker to read the OCR txt aloud and check it on the Garufi PDF print
    2. Create an input file named 'input.txt' in the 'xml' folder
	(where the MSS transcriptions already are);
    3. Run this script in the 'romython' folder, where it is;
    4. The output will be appended to file g.xml in the 'xml' folder.

The input.txt file must look like this:

5.3-5.10                                                      
Etas quippe duobus modis dicitur: aut enim hominis, sicut a natiuitate infantia usque in
annos septem, pueritia usque ad annos quatuordecim, adolescentia a quintodecimo usque in
uicesimus octauum, juuentus usque ad XLVIIII, senectus a quinquagesimo usque ad Lxxvmr,
decrepita ab anno octogesimo quousque uita finitur. Aut mundi, cujus prima etas ab Adam
usque ad Noe, secunda a Noe usque ad Abraham, tertia ab Abraham usque ad Dauid, quarta 
a Dauid usque ad captiuitatem Judeorum in Babyloniam, quinta deinde usque ad aduentum
SaluatoriS, sexta, que nunc est usque quo mundus iste finiatur, quarum decursus per gene-
rationes, et regna euidentius infra, prout inuenire potui, explicabo.
5.11-5.18                                                     
Creator omnium uisibilium et inuisibilium, qui trinus et unus Deus est, in principio creauit
celum, terram, mare, et omnia, que in eis sunt, tempora quoque instituit, nam prima die in
lucis nomine condidit angelos, secunda die celos in appellatione firmamenti, tertia die in
discretionis uocabulo speciem aquarum, quarta luminaria celi, uidelicet solem, et lunam, et
stellas, que temporum sunt ordinationes, quinta animantia ex aquis, sexta animantia ex terra,
et hominem, quem appellauit Adam, et posuit in paradiso, Cujus de latere dormientis costam
tollens, mulierem edificauit, ut eius adjutorio genus propagaret humanum, septima autem die
requieuit Deus' ab omni opere prime ac noue conditionis; hoc autem secundum licteram.

'''

import os
import re
from string import punctuation
import constants
from lxml import etree
import time

os.system('clear')


def properNames (properNamesInputXmlFile):
    ''' Parse an xml file and return a set (not list) of names marked
        with <rs> in that file. All names in the set are in lowercase.
        '''
    names_tree = etree.parse(properNamesInputXmlFile)
    rss = names_tree.findall('.//t:rs', constants.ns)
    namelist = [rs.text.lower() for rs in rss]
    return set(namelist)

class ocr:

    def __init__ (self, ocrpath):
        with open (ocrpath, 'r') as f:
            self.lines = f.readlines()

    def lowercasize (self):
        ''' First, transform "est. Adam" to "est. <rs>Adam</rs>" (based on a list of all
            proper names already marked with <rs> in g.xml).
            Then transform uppercase initials to lowercase after punctuation such as full stop.
            E.g.: "est. Ergo..." becomes  "est. ergo...".
            Chances are that some cases such as "est. Adam"
            are left unmarked and turned to lowercase ("est. adam"), because "Adam" is not recognized
            as a proper name (because it had not been marked with <rs> previously in the g.xml file).
            The block "if after_tag_search" does the same, but with case "<blabla>Adam...".
            '''
        names = properNames('../xml/g.xml') # Create list of proper names previously marked 
        punct_pattern = re.compile('([' + punctuation + '] )([A-Z]\w*\W)')
        after_tag_pattern = re.compile('(>)([A-Z]\w*\W)')

        for l in self.lines:
            i = self.lines.index(l)
            punct_search =  punct_pattern.search(l)
            after_tag_search = after_tag_pattern.search(l)

            if after_tag_search:
                tword = after_tag_search.group(2)[:-1]
                if tword.lower() in names: # If the word after tag is recognized as a proper name
                    l = re.sub(tword, '<rs>' + tword.lower() + '</rs>', l) #... mark it with <rs>
                else:   # Transform "<blabla>Ergo" to "<blabla>ergo"
                    callback = lambda pat: pat.group(1) + pat.group(2).lower()
                    l = re.sub('(>)([A-Z])', callback, l)

            if punct_search:
                pword = punct_search.group(2)[:-1]
                if pword.lower() in names: # If the word after punctuation is recognized as a proper name
                    l = re.sub(pword, '<rs>' + pword.lower() + '</rs>', l) #... mark it with <rs>
                else:   # Transform "est. Ergo" to "est. ergo"
                    callback = lambda pat: pat.group(1) + pat.group(2).lower()
                    l = re.sub('([' + punctuation + '] )([A-Z])', callback, l)

            self.lines[i] = l


    def garufize (self):
        ''' Remove syllabation dashes at the end of lines. Replace each dash with
            <lb break="no" rend="-" type="g"/>. Reunite words separated by those dashes
            in the first line. 
            Wrap everything inside a temporary <div> element.
            Insert <p>s; transform Garufi's pages and lines (e.g.: 3.7-3.16)
            to @xml:id="g3.7-3.16"; append other attributes (@decs and @facs) to <p>;
            put <lb type="g"/> at the beginning of each line except for
            1) lines with Garufi's pages and lines (like 3.7-3.16)
            2) lines whose previous line already has a <lb break="no" rend="-" type="g"/> inside.
            For lines in case 2, function manage_dashes() had inserted a comment <!--nolb--> at
            the their beginning.
            '''


        for l in self.lines:
            i = self.lines.index(l)

            if i < len(self.lines) - 1:  # If it's not the last line of the file
                ''' This 'if' manages syllabation dashes '''
                nextline = self.lines[i+1]
                if len(l) > 1 and l[-2] == '-':
                    firstword, nextline = nextline.split(' ', 1)
                    self.lines[i] = ''.join( [ l[:-2], '<lb break="no" rend="-" type="g"/>', firstword, '\n' ] )
                    # The <!--nolb--> comment prevents the next 'if' block from inserting another <lb>
                    # at the beginning of lines following the lines with <lb break="no" rend="-" type="g"/>
                    self.lines[i+1] = ''.join(['<!--nolb-->', nextline])


            if re.match('\d*\.\d*-.*', l):  # Digits + full stop + digit(s) + dash + the rest of the line
                p_start_tag = '<!--nolb--><p xml:id="g' + l[:-1] + '" decls="#ocr" facs="img/vat.lat.3973.pdf#page=21">'
                self.lines.insert(i + 1, p_start_tag)
                if self.lines.index(l) > 0:
                    self.lines[i] = ''
                    self.lines.insert(i, '')
                    self.lines.insert(i, '</p>')
                else:
                    self.lines[i] = ''
                #self.lines[i] = '<p xml:id="g' + l[:-1] + '" decls="#ocr" facs="img/Vat.lat.3973.pdf#page=21">'
            elif l.startswith('<!--nolb-->'):
                self.lines[i] = self.lines[i].replace('<!--nolb-->', '')
            elif len(l) > 1:
                self.lines[i] = ''.join([    # Pre-pend <lb type="g"/> to the line
                        '<lb type="g"/>',
                        self.lines[i]
                        ])
        self.lines.append('\n</p>')


        self.lines.insert(0, '<div>\n')   # Insert (temporary) <div> before the fist line
        self.lines.append('</div>\n')   # Insert (temporary) </div> after the last line


    def wrap_proper_names (self):
        ''' Wrap <rs> and </rs> around proper names.
            It also deals with the special case of a word interrupted by <lb>.
            '''
        for l in self.lines:
            i = self.lines.index(l)
            s = []
            words = l.split()
            for t in words:
                wi = words.index(t)
                if re.match('[A-Z][a-z]', t[0:2]):  # 1st char is uppercase, 2nd is lowercase
                    if '<lb' in t:  # If the proper name has <lb> inside, like: Ni<lb break="no" rend="-" type="g"/>nus
                        t = ''.join(['<rs>', t])    # Append <rs> before: <rs>Ni<lb break="no" rend="-" type="g"/>nus</rs>
                        words[wi + 3] = ''.join([   # words[wi + 3] is a token like: type="g"/>nus
                            words[wi + 3],
                            '</rs>'  ])             # Append </rs> after it: type="g"/>nus</rs>
                    else:
                        word = t
                        punct = ''
                        if t[-1] in punctuation:    # If the token ends with punctuation, like: homo,
                            word, punct = t[:-1], t[-1]
                        t = '<rs>' + word + '</rs>' + punct
                s.append(t)
            s.append('\n')
            self.lines[i] = ' '.join(s)

    def a_abbrev (self, abbrev_siglum):
        ''' Substitute parts of words with abbreviations.
            E.g.: "eorum" becomes "eo4" and "lupum" becomes "lupu3".
            Argument abbrev_siglum is 'a' for manuscript a, 'b' for MS b, etc.

            An improved version might read the a-combo.csv file and populate the <wholeWorld>
            part of the subdict dictionary automatically.
            '''

        import csv

	# Input CSV combo file
        csvfile = '%s%s-combi.csv' % (constants.csvpath, abbrev_siglum)    # csvpath might look like "../csv/"

        with open(csvfile) as mycsv:
            combi = list(list(rec) for rec in csv.reader(mycsv, delimiter='\t')) #reads csv into a list of lists


        sd = {} # Substitutions Dictionary

        # Append to dictionary 'sd' all whole-word abbreviations like <dno> for 'domino'
        for c in combi: 
            if c[0].startswith('<'):

                expan = c[1]
                abbrev = c[0][1:-1]

                expan_re = '(\W)%s(\W)' % expan
                abbrev_re = '\g<1>%s\g<2>' % abbrev

                sd[expan_re] = abbrev_re

        # Append select other abbreviations 'manually'
        sd['(\w)rum(\W)'] = '\g<1>4\g<2>'  # From the a-tos.csv file
        sd['(\wb)us(\W)'] = '\g<1>9\g<2>'  # This is from the a-combi.csv file
        sd['(\w)m(\W)'] = '\g<1>3\g<2>'

        for l in self.lines:
            i = self.lines.index(l)
            for x in sd:
                l = re.sub(x, sd[x], l)
            self.lines[i] = l

    def xml_export (self, outputXmlFile):
        datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
        backup_filename = '_'.join([outputXmlFile, datetime, 'backup.xml'])
        os.system('cp %s %s' % (outputXmlFile, backup_filename)) # Create backup of old file
        os.system('mv %s %s' % (backup_filename, '../xml/backup')) # Move backup to backup folder
        input_text = ''.join(self.lines)    # Cat all input text (with XML tags) in one long string
        temp_div = etree.fromstring(input_text)  # This is the temporary element <div> to wrap the input text
        export_tree = etree.parse(outputXmlFile)
        export_body = export_tree.find('.//t:body', constants.ns)
        for d in temp_div:
            export_body.append(d)
        export_tree.write(outputXmlFile, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)



o = ocr('../xml/new.xml')
'''
o.garufize()
o.lowercasize()
o.wrap_proper_names()
# The text is now ready to be appended to g.xml
o.xml_export('../xml/g.xml')
'''

o.a_abbrev('a')
o.xml_export('../xml/a.xml')
