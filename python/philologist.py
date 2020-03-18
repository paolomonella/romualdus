#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module manages <app> elements from a TEI XML file '''


import my_database_import
import variant_type
import operator
from lxml import etree
from myconst import ns, xmlpath, dbpath, dbname

debug = False


class treeWithAppElements:

    def __init__(self, juxtaSiglum, printSiglum,
                 msaSiglum, msa2Siglum, msoSiglum,
                 quiet=False):
        ''' - juxtaSiglum is the siglum (e.g. 'm1' or 'm2')
                of the file with the <app> elements;
            - printSiglum is the siglum (e.g. 'g' or 'bonetti')
                of the first witness (that's normally the print edition)
                of the first witness (that's normally the print edition)
            - msaSiglum is the siglum of MS A
            - msa2Siglum is the siglum of MS A, hand 2
            - msoSiglum is the siglum of MS O
            - if quiet is True: suppress basic messages '''

        # Input and output filenames definition:
        self.juxtaSiglum = juxtaSiglum
        self.myJuxtaXmlFile = '%s%s.xml' % (xmlpath, juxtaSiglum)
        self.outputXmlFile = self.myJuxtaXmlFile.replace('.xml', '-out.xml')

        # Sigla for editions and MSS:
        self.printSiglum = printSiglum
        self.msaSiglum, = msaSiglum,
        self.msa2Siglum = msa2Siglum
        self.msoSiglum = msoSiglum
        self.msaSiglum, self.msoSiglum = msaSiglum, msoSiglum

        # Parse the juxtacommons file XML tree:
        self.juxtaTree = etree.parse(self.myJuxtaXmlFile)
        self.justaBody = self.juxtaTree.find('.//t:%s' % ('body'), ns)
        self.apps = self.juxtaTree.findall('.//t:app', ns)

        # Quieter output:
        self.quiet = quiet

        # Import (some) tables from DB
        self.decision_variant_types = my_database_import.import_table(
            dbpath,
            'romualdus.sqlite3',
            'decision_variant_types')
        self.decisions = my_database_import.import_table(
            dbpath,
            'romualdus.sqlite3',
            'decisions')

    def setA2ForAdditions(self):
        ''' In sections that are additions by hand2, replace wit="a" with
            wit="a2" '''

        # Import table hand2_additions from DB
        hand2_additions_table = my_database_import.import_table(
            dbpath,
            dbname,
            'hand2_additions')

        # Create a list with the xml:id's of those <p>s
        additions_xmlids = [x[0] for x in hand2_additions_table]

        # All <p>s in the XML document
        pars = self.justaBody.findall('.//t:%s' % ('p'), ns)

        # Find the <p>s that include additions and include
        # them in list pars_with_addition and put them
        # in list pars_with_additions
        pars_with_additions = []
        additions_count = 0
        for par in pars:
            par_xmlid = par.get('{%s}id' % ns['xml'])
            if par_xmlid in additions_xmlids:
                additions_count += 1
                pars_with_additions.append(par)

        if debug:
            print('found {} pars with adds in {}'.format(
                self.juxtaSiglum, len(pars_with_additions)))

        # Set wit="#a2" if it was "#a"
        #
        # For each <p> with additions in the XML file:
        for par_with_addition in pars_with_additions:
            # All <app> children of that <p>:
            apps_in_par = par_with_addition.findall('.//t:app', ns)
            for app in apps_in_par:
                # Get all <rdg> children of <app>
                rdg_in_app = app.findall('.//t:rdg', ns)
                # Get all <lem> children of <app>
                lem_in_app = app.findall('.//t:lem', ns)
                # All <lem> and <rdg> children of <app>
                # (they should all be <rdg> in fact)
                rdg_and_lem_in_app = rdg_in_app + lem_in_app
                for child in rdg_and_lem_in_app:
                    child_wit = child.get('wit')
                    if child_wit == '#a':
                        # Better not use namespaces when
                        # setting TEI attributes!
                        child.set('wit', '#a2')

    def editTeiHeader(self):
        ''' Set some basic elements in the teiHeader of m1.xml and m2.xml '''

        # Title and editor in <titleStmt>
        title_stmt = self.juxtaTree.find('.//t:titleStmt', ns)
        work_title = title_stmt.find('.//t:title', ns)
        work_title.text = 'Romualdi Salernitani Chronicon'
        work_editor = etree.SubElement(title_stmt, '{%s}editor' % ns['t'])
        work_editor.text = 'Paolo Monella'
        work_editor.set('{%s}id' % ns['xml'], 'pm')

        # <sourceDesc> (imported from a2.xml)
        m_source_desc = self.juxtaTree.find('.//t:sourceDesc', ns)
        for child in m_source_desc:  # Empty <sourceDesc>
            m_source_desc.remove(child)
        a2_file_path = '%sa2.xml' % xmlpath
        a2_tree = etree.parse(a2_file_path)
        a_source_desc = a2_tree.find('.//t:sourceDesc', ns)
        # Import content of a2.xml's <sourceDesc> into m1.xml's and
        # m2.xml's <sourceDesc>
        for child in a_source_desc:
            m_source_desc.append(child)

        # Append a new <msDesc xml:id="a2"> to <sourceDesc> for MS A, hand 2
        list_bibl = m_source_desc.find('.//t:listBibl', ns)
        a2_msDesc = etree.SubElement(list_bibl, '{%s}msDesc' % ns['t'])
        a2_msDesc.set('{%s}id' % ns['xml'], 'a2')
        a2_msIdentifier = etree.SubElement(
            a2_msDesc, '{%s}msIdentifier' % ns['t'])
        etree.SubElement(a2_msIdentifier,
                         '{%s}settlement'
                         % ns['t']).text = 'Biblioteca Apostolica Vaticana'
        etree.SubElement(a2_msIdentifier,
                         '{%s}idno' % ns['t']).text = 'Vat. lat. 3973'
        a2_ab = etree.SubElement(
            a2_msDesc, '{%s}ab' % ns['t'])
        a2_ab.text = ('This siglum represent a later hand, probably of the'
                      ' XVII century, in this manuscript')

        # a2_idno.text = 'Vat. lat. 3973'
        #  etree.SubElement(a2_msDesc, '{%s}msIdentifier' % ns['t'])

        # Remove old <front>/<div>/<listWit> (generated by JuxtaCommons),
        # now redundant
        text_front = self.juxtaTree.find('.//t:front', ns)
        text_front.getparent().remove(text_front)

    def appDict(self):
        ''' Arguments:
            The function parses file myJuxtaXmlFile, finds all <app> elements,
            then creates and populates 'comparisons', a list of dictionaries
            (one dict for each <app> in the TEI XML file).
            Each dict in the list is the result of the comparison of two
            <app> TEI XML elements, and has those keys (examples are for
            variants "sillaba" vs "syllaba"):
                'r1' = the variant characters in myString1 ('y'),
                    inherited from function variantComparison()
                'r2' = the variant characters in myString2 ('i'),
                    inherited from function variantComparison()
                'type' = the variant type ('y-type'),
                    inherited from function variantComparison()
                plus new additional keys:
                'app' = the <app> XML element
                'printReading' = the <rdg> or <lem> XML element of the
                    print edition (corresp. to printSiglum)
                'msaReading' = the <rdg> or <lem> XML element of MS A
                    (corresp. to msaSiglum)
                'msa2Reading' = the <rdg> or <lem> XML element of MS A,
                    hand 2, i.e. wit="#a2"
                    (corresp. to msaSiglum)
                'msoReading' = the <rdg> or <lem> XML element of MS O
                    (if present; corresp. to msaSiglum)
                'printText' = the text (string) of the variant of the print
                    edition (corresp. to printSiglum)
                'msaText' = the text (string) of the variant of MS A
                    (corresp. to msaSiglum)
                'msoText' = the text (string) of the variant of MS O
                    (corresp. to msoSiglum)
                'where' = the xml:id of the parent <p>
        '''

        # This will become a list of dictionaries:
        comparisons = []
        for app in self.apps:
            printReading = app.find('.//t:*[@wit="#%s"]' %
                                    (self.printSiglum), ns)
            msaReading = app.find('.//t:*[@wit="#%s"]' % (self.msaSiglum), ns)
            # If any:
            msa2Reading = app.find('.//t:*[@wit="#%s"]' % (self.msa2Siglum),
                                   ns)
            # If any:
            msoReading = app.find('.//t:*[@wit="#%s"]' % (self.msoSiglum), ns)

            # Debug tests: check if something went wrong.
            #
            # Everything is OK if there is one reading
            # and one manuscript reading. The latter can belong
            # to MS A, to the second hand of MS A or to MS O.
            # If the print reading or one of the MSS readings are missing,
            # something is wrong:
            if (printReading is None or
                (msaReading is None
                 and msa2Reading is None
                 and msoReading is None)):
                print(('\n[Debug 07.03.2020 10.29] In file {},'
                       ' paragraph {} {}, I found those readings:\n'
                       '\t- print reading: {}\n'
                       '\t- MS A reading: {}\n'
                       '\t- MS A hand 2 reading: {}\n'
                       '\t- MS O print reading: {}').format(
                           self.myJuxtaXmlFile,
                           app.getparent().tag,
                           app.getparent().attrib,
                           printReading,
                           msaReading,
                           msa2Reading,
                           msoReading,))

            # Set variables printText, msaText, msoText...
            # ...for print edition
            if printReading is not None and printReading.text is not None:
                printText = printReading.text
            else:
                printText = ''
            # ... for MS A
            if msaReading is not None and msaReading.text is not None:
                msaText = msaReading.text
            else:
                msaText = ''
            # ... for MS A, hand 2
            if msa2Reading is not None and msa2Reading.text is not None:
                msa2Text = msa2Reading.text
            else:
                msa2Text = ''
            # ... and for MS O (if any)
            if msoReading is not None and msoReading.text is not None:
                msoText = msoReading.text
            else:
                msoText = ''

            # Debug
            if debug:
                print('\n\nprintText: «%s»' % (printText))
                print('msaText: «%s»' % (msaText))
                print('msoText: «%s»' % (msoText))

            # MyComp is a dictionary (and 'comparisons' a list of
            # dictionaries).
            # This is the line that imports the dictionary from function
            # variantComparision (from module variant_type.py):
            myComp = variant_type.variantComparison(printText, msaText)

            # Set additional keys in dictionary myComp. See the documentation
            # of this method above for details.
            myComp['app'] = app
            myComp['printReading'] = printReading
            myComp['msaReading'] = msaReading
            myComp['msa2Reading'] = msa2Reading
            myComp['msoReading'] = msoReading
            myComp['printText'] = printText
            myComp['msaText'] = msaText
            myComp['msa2Text'] = msa2Text
            myComp['msoText'] = msoText
            myComp['where'] = app.getparent().get(
                '{%s}id' % ns['xml'])

            # Determine @type of <app>
            #
            # 1) when there are two variants,
            #   i.e. [print vs MS A] or [print vs MS A2]:
            #   myComp['app'] is automatically inherited from
            #   variantComparison(),
            #   based on a comparison between print edition and MS A.
            #   If unkown, myComp['app'] = 'unknown-type'; otherwise,
            #   it is set by variantComparison()
            #   (I am ignoring the variant of MS O, or it would all become
            #    too complex).
            if msoReading is None:
                pass

            # 2) when there are 2 variants, i.e. [print vs MS O]:
            #   myComp['app] = 'unknown-print-vs-o-type'
            #   (assumption: there is always a print <rdg>)
            elif (msoReading is not None and
                  (msaReading is None and msa2Reading is None)):
                myComp['type'] = 'unknown-print-vs-o-type'

            # 3) when there are 3 variants, i.e. [print vs MS A vs MS O]:
            #   myComp['app] = 'unknown-print-vs-a-vs-o-type'
            elif (msoReading is not None and
                  (msaReading is not None or msa2Reading is not None)):
                myComp['type'] = 'unknown-print-vs-a-vs-o-type'

            # 4) Catch errors
            else:
                print(('[philologist.py]: I could not manage '
                       'the presence/absence of readings in MS A '
                       'and in MS O'))

            comparisons.append(myComp)
        return comparisons

    def variantTypesList(self):
        '''Return a list all variant types in <app> '''
        myList = [c['type'] for c in self.appDict()]
        return myList

    def variantTypesCountSetList(self):
        '''Same as variantTypesList, but it returns a list
            in which each element only occurs once'''
        mySet = set(self.variantTypesList())
        # mySetList is still a list, but in which each element
        # of myList occurs only once
        mySetList = [t for t in mySet]
        return mySetList

    def variantTypesCount(self):
        '''Return a dict like
            {'missing-in-ms-type': 124,
            'missing-in-print-vs-punct-in-ms-type': 252 etc.}
            counting in how many <app> elements in the juxtaTree each
            variant type recurs '''
        myList = self.variantTypesList()
        myListCount = []    # A list (of tuples)
        for x in self.variantTypesCountSetList():
            # Add a new tuple to the list
            myListCount.append((x, myList.count(x)))
        # Ordered from highest number to lowest:
        myListCount = sorted(myListCount, key=operator.itemgetter(1),
                             reverse=True)
        return myListCount

    def variantTypesCountPrint(self):
        '''Print variantTypesCountDict'''
        if not self.quiet:
            print(('\n[set_variant_types_in_appcrit_tei_file / '
                   'variantTypesCountPrint]: '
                   'In file {} there are:').format(self.juxtaSiglum))
            for x in self.variantTypesCount():
                print('{:5} {:12}'.format(x[1], x[0]))

    def setTypeAttributesForApps(self):
        '''Set @type attributes in <app> elements in the input TEI XML file '''
        if debug:
            myTypesDebug = [c['type'] for c in self.appDict()]
            print('[Debug 07.03.2020] %s' % (set(myTypesDebug)))
        for c in self.appDict():
            # Better not use namespaces when setting TEI attributes!
            # c['app'].set('{%s}type' % ns['t'], c['type'])
            c['app'].set('type', c['type'])

            if debug:
                print('\n')
                print('«%s» | «%s» %15s @type="%s"' %
                      (c['printText'], c['msaText'], '·', c['type']))
                for k in c:
                    print('%s: «%s»' % (k, c[k]))

    def findAndLocateSicCorr(self):
        # self.juxtaSiglum, self.printSiglum, self.msaSiglum
        if self.printSiglum == 'g':
            myPrintXmlFile = '%s%s.xml' % (xmlpath, self.printSiglum)
        elif self.printSiglum == 'b':
            # Cope with the fact that the xml file for Bonetti currently
            # is not b.xml but bonetti.xml:
            myPrintXmlFile = '%s%s.xml' % (xmlpath, 'bonetti')
        printTree = etree.parse(myPrintXmlFile)
        corrs = printTree.findall('.//t:corr', ns)
        # choices = [corr.getparent() for corr in corrs]
        # sics = [choice.find('.//t:sic', ns) for choice in choices]

        # Create a list of dictionaries, like:
        # {'choice' = <choice> element, 'corr' = <corr>, 'sic' = <sic>}
        corrections = []
        for c in corrs:
            myDict = {'corr': c}    # A dictionary
            myDict['choice'] = c.getparent()
            myDict['sic'] = myDict['choice'].find('.//t:sic', ns)
            corrections.append(myDict)

        # Manage case in which <choice><orig>+<reg> is in <corr>:
        for c in corrections:
            for e in [c['corr'], c['sic']]:
                # If <sic> or <corr> has a <choice> child:
                innerchoice = e.find('.//t:choice', ns)
                if innerchoice is not None:
                    # If <choice> has <reg> and <orig> as children:
                    innerreg = innerchoice.find('.//t:reg', ns)
                    innerorig = innerchoice.find('.//t:orig', ns)
                    if innerreg is not None and innerorig is not None:
                        # Remove <orig> and keep <reg>:
                        innerchoice.remove(innerorig)

        # Get (iter)text of <corr> and of <sic>
        for c in corrections:
            c['corrText'] = ''.join(c['corr'].itertext())
            c['sicText'] = ''.join(c['sic'].itertext())

        # Locate the corrections in m1 or m2
        count = 0
        for c in corrections:
            for a in self.appDict():
                # ...but I guess that it should only be
                # if a[sicText] == a[printText] (not also corrText)
                '''if c['corrText'].lower() == a['printText'].lower() or \
                   c['sicText'].lower() == a['printText'].lower():'''
                if c['sicText'].lower() == a['printText'].lower():
                    count += 1
                    if not self.quiet:
                        print(('[findAndLocateSicCorr] '
                               'file {}: '
                               'Matching correction «{}» for «{}» '
                               'with app print «{}»/ms «{}»'
                               'in par. {}.').format(
                                   self.juxtaSiglum,
                                   c['corrText'],
                                   c['sicText'],
                                   a['printText'],
                                   a['msaText'],
                                   a['app'].getparent().get('{%s}id' %
                                                            ns['xml'])
                             ))
        if not self.quiet:
            print(('[set lems based on sic/corr], file {}: '
                   'I located {} corrections').format(
                       self.juxtaSiglum,
                       count))

    def make_lem(self, myElement):
        ''' Promote myElement to chosen text,
            i.e. set its tag name to <lem> '''
        # Always add the namespace when setting new tag
        myElement.tag = '{%s}lem' % ns['t']

    def make_rdg(self, myElement):
        ''' Demote myElement to not chosen text,
            i.e. set its tag name to <rdg> '''
        # Always add the namespace when setting new tag
        myElement.tag = '{%s}rdg' % ns['t']

    def make_substantial(self, substantial_app):
        ''' Demote myElement to not chosen text,
            i.e. set its tag name to <rdg> '''
        # Better not use namespaces when setting TEI attributes!
        # substantial_app.set('{%s}type' % ns['t'], 'substantial-type')
        substantial_app.set('type', 'substantial-type')
        # Better not use namespaces when setting TEI attributes!
        # substantial_app.set('{%s}cert' % ns['t'], 'high')
        substantial_app.set('cert', 'high')

    def setLemsBasedOnType(self, setCert=True):
        '''For some @type(s) of <app>, decide the <lem> automatically
            based on that @type. '''

        # Decide <lem> and set @cert based on decision_variant_types:
        if debug:
            print(self.appDict())
        for c in self.appDict():
            for myRow in self.decision_variant_types:

                # E.g.: 'different-punct-type':
                if c['type'] == myRow['type']:
                    # db_preferredRdg can be 'reading_of_the_print_edition'
                    # or a generic 'reading_of_one_of_the_mss':
                    db_preferredRdg = myRow['preferredRdg']

                    if db_preferredRdg == 'reading_of_the_print_edition':
                        self.make_lem(c['printReading'])

                    elif db_preferredRdg == 'reading_of_one_of_the_mss':
                        # Choose the reading of MS A, if any:
                        if c['msaReading'] is not None:
                            self.make_lem(c['msaReading'])
                        # If there is a MS A reading, the script will
                        # skip the other lines. Otherwise (if there
                        # is no MS A reading),
                        # choose the reading of MS A2, if any:
                        elif c['msa2Reading'] is not None:
                            self.make_lem(c['msa2Reading'])
                        # If there is no MS A reading and
                        # no MS A2 reading,
                        # choose the reading of MS O, if any:
                        elif c['msoReading'] is not None:
                            self.make_lem(c['msoReading'])
                        else:
                            print(('\n[setLemsBasedOnType] I should'
                                   ' choose a reading from a MS, but'
                                   ' I can\'t find any MS reading in'
                                   ' the <app> element. This <app>'
                                   ' has printText «{}» and these'
                                   ' features: «{}»/').format(
                                       ' '.join(c['printReading'].itertext()),
                                       c))

                    else:
                        print(('\n[setLemsBasedOnType] I couln\'t'
                               ' read table decision_variant_types'
                               ' from the DB properly. My db_preferredRdg'
                               ' is {}').format(db_preferredRdg))

                    if setCert is True:
                        # myCert can be 'low', 'middle' or 'high':
                        myCert = myRow['cert']
                        # Better not use namespaces when setting
                        # TEI attributes!
                        # c['app'].set('{%s}cert' % ns['t'], myCert)
                        c['app'].set('cert', myCert)

    def findMsReading(self, fn_app_dict):
        ''' Input an appDict (a dict generated by appDict).
            Return the XML element representing the only
            MS reading in the appDict '''

        # Identify the MS reading. There is only one,
        # i.e. MS A, MS A2 or MS O)
        fn_ms_reading = None
        for x in [fn_app_dict['msaReading'],
                  fn_app_dict['msa2Reading'],
                  fn_app_dict['msoReading']]:
            if x is not None and fn_ms_reading is None:
                # This is it!
                fn_ms_reading = x
            # Check if more than one of them is not None
            # (it should never happen, because <app> only has 2
            # children)
            elif x is not None and fn_ms_reading is not None:
                print(('[setLemBasedOnDBFor2Readings]'
                       ' file {}: <app> {} has more than one'
                       ' MS reading, but I am handling it'
                       ' as though it only had one').format(
                           self.juxtaSiglum, fn_app_dict))

        # Check if the script found no MS reading at all
        if fn_ms_reading is None:
            print(('[setLemBasedOnDBFor2Readings]'
                   ' file {}: <app> {} has no'
                   ' MS reading').format(
                       self.juxtaSiglum, fn_app_dict))

        return fn_ms_reading

    def setLemBasedOnDBFor2Readings(self, a):
        # For each record in the 'decisions' DB table:
        for r in self.decisions:

            ####################################################
            # Decide if the <app> corresponds to the DB record #
            ####################################################

            # If the print reading in <app> is the same
            # of the print reading in the DB record...
            if(r['print'] == a['printText']

               # and the MS reading in the DB record is
               # the MS A reading or MS A2 reading
               # or MS O reading in <app>
               and r['ms'] in [a['msaText'], a['msa2Text'], a['msoText']]

               # and we are in the right <p>...
               and (a['where'] == r['where']
                    # ...or the DB decision is to be applied everywhere
                    or r['where'] == 'everywhere')):

                ############################
                # Set <lem> and <rdg> tags #
                ############################

                # The print reading will always be set to <rdg>
                self.make_rdg(a['printReading'])

                # Identify the MS reading
                my_ms_reading = self.findMsReading(a)

                if r['type'] == 'choose':
                    # Make the MS reading <lem>
                    self.make_lem(my_ms_reading)

                elif r['type'] == 'conj':

                    # Make also the MS reading <rdg>
                    self.make_rdg(my_ms_reading)

                    # Manifacture a new <lem> element
                    # I am not sure if I should add
                    # the namespace or not
                    conj_lem = etree.SubElement(
                        a['app'],  # 'lem')
                        '{%s}lem' % ns['t'])
                    conj_lem.text = r['conj']
                    # Better not use namespaces when setting
                    # TEI attributes!
                    # conj_lem.set('{%s}resp' % ns['t'], '#pm')
                    conj_lem.set('resp', '#pm')
                else:
                    print(('[philologist.py/setLemBasedOnDBFor2Readings] '
                           'I can\'t find a "decision" field '
                           'in the DB record'))
                self.make_substantial(a['app'])

            # Debug
            if not self.quiet:
                print(('[setLemsBasedOnDB], part m{}, '
                       'origin {}. Print/MS:\n'
                       'DB «{}»/«{}» \n'
                       '<app> «{}»/«{}»\n'
                       'Paragraph {}\n').format(
                           r['part'],
                           r['origin'],
                           r['print'],
                           r['msa'],
                           a['printText'],
                           a['msaText'],
                           a['app'].getparent().get('{%s}id' %
                                                    ns['xml'])))

    def setLemBasedOnDBFor3Readings(self):
        ''' I'll code this if/when I actually collate MS O.
            Probably the best thing to do is to manage those cases
            (very few, if any) by hand '''
        pass

    def setLemsBasedOnDB(self):
        '''Read DB table and decide <lem> for some <app>s '''
        for app_dict in self.appDict():

            # Case A: 2 variants, 1 <lem> + 1 <rdg>
            # The 1st will be from print,
            # the 2nd will be from A or A2 or O
            if len(app_dict['app']) == 2:
                self.setLemBasedOnDBFor2Readings(app_dict)

            # Case B: 3 variants, 1 <lem> + 2 <rdg>
            # The 1st will be from print,
            # The 2nd from A or A2,
            # The 3rd from O
            elif len(app_dict['app']) == 3:
                self.setLemBasedOnDBFor3Readings(app_dict)

            # Case C: more than 3 variants
            elif len(app_dict['app']) > 3:
                    print(('[setLemsBasedOnDB]'
                           ' file {}: <app> {} has more than'
                           ' three children').format(
                               self.juxtaSiglum, app_dict))
            else:
                    print(('[setLemsBasedOnDB]'
                           ' file {}: <app> {} has a strange'
                           ' number of children').format(
                               self.juxtaSiglum, app_dict))

    def putLemAsFirstInApp(self):
        ''' In the TEI DTD, <lem> must be the first child of <app>.
            This method puts <lem> first '''
        for a in self.appDict():
            app = a['app']
            for child in app:
                # If the child is a <lem>:
                if child.tag == '{%s}lem' % ns['t']:
                    if app.index(child) > 0:
                        app.insert(0, child)

    def write(self):
        ''' Write my XML juxtaTree to an external file '''
        self.juxtaTree.write(self.outputXmlFile,
                             encoding='UTF-8', method='xml',
                             pretty_print=True, xml_declaration=True)
