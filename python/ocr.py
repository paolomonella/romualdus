#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

bom = True     # Set to True if you want to get rid of the initial BOM

''' 

    How to use this script:
    1. Review the OCR before running the script:
        1a. Perform OCR twice with gImageReader
        1b. Use "vim -d x.txt y.txt" to check differences
        1c. Use gespeaker to read the OCR txt aloud and check it on the Garufi PDF print
    2. Put an input file named 'input.txt' in the 'xml' folder
	(where the MSS transcriptions already are);
    3. Comment/uncomment the last lines of this script;
    4. Run this script in the 'python' folder, where it is;
    5. The output will be appended to files g_temp.xml, a.xml or g.xml in the 'xml' folder.
    6. Check if <rs>'s and <hi>'s and all remaining uppercase chars are OK (vim /\v[A-Z][a-z]  and   /\v[.!?-]   etc.)
    7. You *can* add <seg type="num">
    8. Un-capitalize everything
    9. Substitute j → i in a.xml
    10. Eventually check empty <p>s appended (with the same xml:id's) to b.xml and c.xml

The input.txt file must look like this

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
        Add to that set the proper names added 'by hand' to file rs.txt
        '''
    names_tree = etree.parse(properNamesInputXmlFile)
    rss = names_tree.findall('.//t:rs', constants.ns)
    namelist = [rs.text.lower() for rs in rss]
    with open ('rs.txt', 'r') as rstxt:
        for l in rstxt:
            namelist.append(l.strip().lower())
    return set(namelist)


def listNames (properNamesInputXmlFile, myNamespace):
    ''' This script parses the ../xml/temp_g.xml file and lists
        the textual content of all its <rs> elements.
        All names in the list are in lowercase.
        '''
    names_tree = etree.parse(properNamesInputXmlFile)
    rss = names_tree.findall('.//%srs' % myNamespace)
    for rs in rss:
        print(rs.text, end=',')
    print('\n---\n')

def sorted_nicely( l ): 
    ''' Sort the given iterable in the way that humans expect.''' 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def updateNamesFile (updateProperNamesInputXmlFile):
    ''' Update the rs.txt file, merging names in <rs> elements in
        file updateProperNamesInputXmlFile (e.g. a.xml) and names
        in the original rs.txt file. Backup the original file.
        '''

    # Get updated set of names from XML file and rs.txt
    newNamesSet = properNames(updateProperNamesInputXmlFile)

    # Backup old rs.txt
    datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
    backup_filename = '_'.join([datetime, 'rs_backup.txt'])
    os.system('cp rs.txt %s' % (backup_filename))

    #Create new rs.txt file
    with open ('rs.txt', 'w') as f:
        for n in sorted_nicely(newNamesSet):
            print(n.strip(), file=f)

def checkrs (myProperNamesInputFile):
    ''' This function parses an XML file, performs a textual search
        on the XML file for each proper name listed in file
        rs.txt, and checks that each of the occurrences of each name
        in the XML files is marked with a <rs> tag.
        If this is not the case, the script prints out the XML file name,
        the parent element including the name, and that element's text. '''
    names_tree = etree.parse(myProperNamesInputFile)
    regexpNS = 'http://exslt.org/regular-expressions'
    with open ('rs.txt', 'r') as rsfile:
        for l in rsfile:
            myname = l.strip()
            find = etree.XPath('//text()[re:match(., "\W%s\W", "i")]/parent::*' % (myname), namespaces={'re':regexpNS})
            # Doc: http://exslt.org/regexp/ e http://exslt.org/regexp/functions/test/index.html
            for r in find(names_tree):
                if r.tag != constants.tei_ns + 'rs':
                    print('%10s %s %10s %s %10s %s' % ('File:', myProperNamesInputFile, 'Name:', myname, 'Tag:', r.tag))
                    #print(' '.join([t.strip() for t in r.itertext()]))




def spread_ids (get_p_ids_from, append_p_ids_to):
    ''' This function takes xml:id's from XML file "get_p_ids_from"
        checks which <p>'s are present in XML file "get_p_ids_from" but
        missing from XML files listed in "append_p_ids_to", then
        appends new <p>'s to those XML files.
        It creates backup files in the same 'xml' directory as the
        original XML files.
        '''
    input_tree = etree.parse('../xml/%s.xml' % get_p_ids_from)
    input_body = input_tree.find('.//t:body', constants.ns)
    pp = input_body.findall('.//t:p', constants.ns)
    ids = [p.get(constants.xml_ns + 'id') for p in pp]
    
    for ms in append_p_ids_to:
        datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
        input_filename = '.'.join([ms, 'xml'])
        backup_filename = '_'.join([datetime, ms, 'id-spreading-backup.xml'])
        os.system('cp ../xml/%s ../xml/%s' % (input_filename, backup_filename)) # Create backup of old file
        output_tree = etree.parse('../xml/%s.xml' % ms)
        output_body = output_tree.find('.//t:body', constants.ns)
        pp = output_body.findall('.//t:p', constants.ns)
        outids = [p.get(constants.xml_ns + 'id') for p in pp]
        for ii in ids:
            if ii.strip() not in outids:
                newp = etree.Element(constants.tei_ns + 'p')
                newp.set(constants.xml_ns + 'id', ii)
                output_body.append(newp)
                #print('Nel MS %s NON c\'era %s' % (ms, ii))
        output_tree.write('../xml/%s.xml' % (ms), encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)



class ocr:

    def __init__ (self, ocrpath):
        with open (ocrpath, 'r') as f:
            self.lines = f.readlines()
            if bom:
                self.lines[0] = self.lines[0][1:]   # This is to get rid of initial BOM which created trouble

    def lowercasize (self):
        ''' First, transform "est. Adam" to "est. <rs>Adam</rs>" (based on a list of all
            proper names already marked with <rs> in g.xml).
            Then mark the rest of the capitalized names with <hi> and transform their initial letter to
            lowercase after punctuation such as full stop. E.g.: "est. Ergo..." becomes  "est. <hi>ergo</hi>".
            Chances are that some cases such as "est. Adam"
            are wrongly transformed to "est. <hi>adam</hi>), if "Adam" is not recognized
            as a proper name (because it had not been marked with <rs> previously in the g.xml file).
            The block "if after_tag_search" does the same, but with case "<blablabla>Adam..." or "&lbs;Adam"

            '''
        names = properNames('../xml/g.xml') # Create list of proper names previously marked 
        after_tag_pattern = re.compile('([;>])([A-Z]\w*\W)')                   # E.g.: "<blablabla>Adam" or "&lbs;Adam"
        punct_pattern = re.compile('([' + punctuation + '] )([A-Z]\w*\W)')  # E.g.: "est. Adam"

        for l in self.lines:
            i = self.lines.index(l)
            after_tag_search = after_tag_pattern.search(l)  # E.g.: "<blablabla>Adam"
            punct_search =  punct_pattern.search(l)         # E.g.: "est. Adam"

            if after_tag_search:    # E.g.: "<blablabla>Adam"
                tword = after_tag_search.group(2)[:-1]
                if tword.lower() in names: # If the word after the entity is recognized as a proper name
                    l = re.sub(tword, '<rs>' + tword.lower() + '</rs>', l) #... mark it with <rs>
                elif False:   # Transform "<blablabla>Adam" to "<blablabla>Adam" -- This is how I used to do this before
                    callback = lambda pat: pat.group(1) + pat.group(2).lower()
                    l = re.sub('(>)([A-Z])', callback, l)
                else:    #... mark the word with <hi>
                    l = re.sub(tword, '<hi>' + tword.lower() + '</hi>', l)  #... mark it with <hi>

            if punct_search:        # E.g.: "est. Adam"
                pword = punct_search.group(2)[:-1]
                if pword.lower() in names: # If the word after punctuation is recognized as a proper name
                    l = re.sub(pword, '<rs>' + pword.lower() + '</rs>', l) #... mark it with <rs>
                elif False:   # Transform "est. Ergo" to "est. ergo" -- This is how I used to do this before
                    callback = lambda pat: pat.group(1) + pat.group(2).lower()
                    l = re.sub('([' + punctuation + '] )([A-Z])', callback, l)
                else:   #... mark the word with <hi>
                    l = re.sub(pword, '<hi>' + pword.lower() + '</hi>', l) #... mark it with <hi>

            self.lines[i] = l


    def garufize (self):
        ''' 1. Remove syllabation dashes at the end of lines.
            2. Replace each dash with &lb; (corresponding to <lb break="no" rend="-" type="g"/>).
            3. Reunite words separated by those dashes in the first line. 
            4. Wrap everything inside a temporary <div> element.
            5. Insert <p>s.
            6. Transform Garufi's pages and lines (e.g.: 3.7-3.16) to @xml:id="g3.7-3.16".
            7. Append other attributes (@decs) to <p>.
            8. Put &lbs; (corresponding to <lb type="g"/>) at the beginning of each line except for
                a) lines with Garufi's pages and lines (like 3.7-3.16)
                b) lines whose previous line already has a <lb break="no" rend="-" type=) g"/> inside.
            9. For lines in case 2, function manage_dashes() had inserted a comment <!--nolb--> at
            the their beginning.
            '''


        for l in self.lines:
            i = self.lines.index(l)

            if i < len(self.lines) - 1:  # If it's not the last line of the file
                ''' This 'if' manages syllabation dashes '''
                nextline = self.lines[i+1]
                if len(l) > 1 and l[-2] == '-':
                    firstword, nextline = nextline.split(' ', 1)
                    #self.lines[i] = ''.join( [ l[:-2], '<lb break="no" rend="-" type="g"/>', firstword, '\n' ] )
                    self.lines[i] = ''.join( [ l[:-2], '&lb;', firstword, '\n' ] )
                    # The <!--nolb--> comment prevents the next 'if' block from inserting another <lb>
                    # at the beginning of lines following the lines with '&lb;'
                    # (corresponding to <lb break="no" rend="-" type="g"/>)
                    self.lines[i+1] = ''.join(['<!--nolb-->', nextline])


            if re.match('\d*\.\d*-.*', l): # Digits + full stop + digit(s) + dash + the rest of the line
                p_start_tag = '<!--nolb--><p xml:id="g' + l[:-1] + '" decls="#ocr">'
                self.lines.insert(i + 1, p_start_tag)
                if self.lines.index(l) > 0:
                    self.lines[i] = ''
                    self.lines.insert(i, '')
                    self.lines.insert(i, '</p>')
                else:
                    self.lines[i] = ''
                #self.lines[i] = '<p xml:id="g' + l[:-1] + '" decls="#ocr">'
            elif l.startswith('<!--nolb-->'):
                self.lines[i] = self.lines[i].replace('<!--nolb-->', '')
            elif len(l) > 1:
                self.lines[i] = ''.join([    # Pre-pend <lb type="g"/> to the line
                        #'<lb type="g"/>',
                        '&lbs;',            # This line was: '<lb type="g"/>',
                        self.lines[i]
                        ])
        self.lines.append('\n</p>')

        self.lines.insert(0, '<div>\n')     # Insert a (temporary) <div> before the fist line
        self.lines.append('</div>\n')       # ... and a (temporary) </div> after the last line

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
                    # Note that the following 'if' case is not necessary if I use &lb; instead
                    # of <lb break="no" rend="-" type="g"/>, but it doesn't hurt either, so I'm leaving it
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
                        t = '<rs>' + word.lower() + '</rs>' + punct
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

	# Input CSV combi file
        combifile = '%s%s-combi.csv' % (constants.csvpath, abbrev_siglum)    # csvpath might look like "../csv/"
	# Input CSV tos file
        tosfile = '%s%s-tos.csv' % (constants.csvpath, abbrev_siglum)    # csvpath might look like "../csv/"

        with open(combifile) as mycombi:
            combi = list(list(rec) for rec in csv.reader(mycombi, delimiter='\t')) #reads csv into a list of lists

        with open(tosfile) as mytos:
            tos = list(list(rec) for rec in csv.reader(mytos, delimiter='\t')) #reads csv into a list of lists

        sd = {} # Substitutions Dictionary


        for t in tos:     # Append brevigraphs from a-tos to the dictionary

            if tos.index(t) == 0:
                pass
            elif t[3] == 'Brevigraph' and t[0] != 'ł':
                expan = t[1]
                abbrev = t[0]
                sd[expan] = abbrev


        for c in combi:     # Append abbreviations from a-combi to the dictionary

            if combi.index(c) == 0:
                pass

            elif c[0].startswith('<'): # Append all whole-word abbreviations (e.g. <dno> for 'domino') to the dict
                expan = c[1]
                abbrev = c[0][1:-1]

                expan_re = '(\W)%s(\W)' % expan
                abbrev_re = '\g<1>%s\g<2>' % abbrev

                sd[expan_re] = abbrev_re

            elif c[0][0].isalpha(): # Append all part-of-the-word abbreviations (e.g. t0 for ter) to the dict
                expan = c[1]
                abbrev = c[0]
                sd[expan] = abbrev

        # Insert select other abbreviations 'manually'
        sd['j'] = 'i'                      # This is no abbreviation. But MS A has not 'j' grapheme
        '''
        sd['(\W)omni'] = '\g<1>omi0'       # From the a-combi.csv file
        sd['(\w)cundum(\W)'] = '\g<1>cdm0\g<2>'  # From the a-combi.csv file
        sd['(\w)cunda(\W)'] = '\g<1>cda0\g<2>'   # From the a-combi.csv file
        '''
        sd['(\w)rum(\W)'] = '\g<1>4\g<2>'  # From the a-tos.csv file
        sd['(\W)per'] = '\g<1>þ'           # From the a-tos.csv file
        sd['(\W)pro'] = '\g<1>ŋ'           # From the a-tos.csv file
        sd['(\w)ter'] = '\g<1>t0'           # From the a-tos.csv file
        '''
        sd['(\wb)us(\W)'] = '\g<1>9\g<2>'  # This is from the a-combi.csv file
        sd['(\wq)ue(\W)'] = '\g<1>9\g<2>'  # This is from the a-combi.csv file
        sd['(\wt)ur(\W)'] = '\g<1>2\g<2>'  # This is from the a-combi.csv file
        '''
        sd['(\w)m(\W)'] = '\g<1>3\g<2>'

        for l in self.lines:
            i = self.lines.index(l)
            for x in sd:
                #l = re.sub(x, sd[x], l)   # This was simpler, but not case insensitive
                insensitive_pattern = re.compile(x, re.IGNORECASE)
                if insensitive_pattern.search(l):
                    l = insensitive_pattern.sub(sd[x], l)
            self.lines[i] = l

    def export_to_txt (self, outputTxtFile):
        with open(outputTxtFile, 'w') as temp:
            print(file=temp)
            for l in self.lines:
                print(l, file=temp, end='')

    def append_to_xml (self, outputXmlFile):
        datetime = time.strftime('%Y-%m-%d_%H.%M.%S')
        backup_filename = '_'.join([outputXmlFile, datetime, 'backup.xml'])
        os.system('cp %s %s' % (outputXmlFile, backup_filename)) # Create backup of old file
        os.system('mv %s %s' % (backup_filename, '../xml/backup')) # Move backup to backup folder
        input_text = ''.join(self.lines)    # Cat all input text (with XML tags) in one long string
        temp_body = etree.fromstring(input_text)  # This is the temporary element <div> to wrap the input text
        export_tree = etree.parse(outputXmlFile)
        export_body = export_tree.find('.//t:body', constants.ns)
        for d in temp_body:
            export_body.append(d)
        export_tree.write(outputXmlFile, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)

    def printout (self):
        for l in self.lines:
            print(l, end='')



''' PROPER NAMES '''

#listNames('../xml/g.xml', constants.tei_ns) 
#updateNamesFile('../xml/a.xml')
#print('\n-----------------------\n\nNEW SEARCH: \n')
#for myf in ['../xml/a.xml', '../xml/g.xml']:
#for myf in ['../xml/a.xml']:
    #checkrs(myf)


''' ACTUAL OCR '''

o = ocr('../xml/input.txt')
o.garufize()
o.lowercasize()
o.wrap_proper_names()
#o.export_to_txt('../xml/temp_g.xml')

spread_ids('g', ['a', 'b', 'c'])
    
#proofread = ocr('../xml/temp_g.xml')
#proofread.a_abbrev('a')
#proofread.append_to_xml('../xml/a.xml')

''' No longer in use:
o.append_to_xml('../xml/g.xml')
o.a_abbrev('a')        '''
