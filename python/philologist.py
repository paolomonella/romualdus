#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module manages <app> elements from a TEI XML file '''


import my_database_import
import variant_subtype
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
        self.juxtaBody = self.juxtaTree.find('.//t:%s' % ('body'), ns)
        self.apps = self.juxtaTree.findall('.//t:app', ns)

        # Quieter output:
        self.quiet = quiet

        # Import tables from DB:
        self.decisions2 = my_database_import.import_table(
            dbpath,
            dbname,
            'decisions2')
        self.decisions3 = my_database_import.import_table(
            dbpath,
            dbname,
            'decisions3')
        self.paragraphs = my_database_import.import_table(
            dbpath,
            dbname,
            'paragraphs')
        self.variant_subtypes = my_database_import.import_table(
            dbpath,
            dbname,
            'variant_subtypes')

        # This dictionary will be used by a method that will be
        # repeated many times. It expands abbreviations of 'type'
        # field in DB tables decisions2 and decisions3
        self.type_expansion = {
            's': 'substantial',
            'o': 'orthography',
            'p': 'punctuation',
            'g': 'gap-in-ms',
            'i': 'illegible-in-ms',
            't': 'transposition',
            'u': 'unknown'
        }

    def set_a2_for_additions(self):
        ''' In sections that are additions by hand2, replace wit="a" with
            wit="a2" (consider that @wit may have more than on siglum
            in <app> '''

        # A list with the xml:id's of those <p>s (from the DB)
        additions_xmlids = [x['xmlid'] for x in self.paragraphs
                            if x['a2'] == 1]

        # A list with all <app> XML elements (not appdict
        # dictionaries) that are in the right <p>s (from appdict)
        apps_in_additions = [a['app'] for a in self.appdict()
                             if a['xmlid'] in additions_xmlids]
        if debug:
            print([a['xmlid'] for a in apps_in_additions])
            print(len(apps_in_additions))

        # Replace "#a" with #a2" in @wit (including the "#b #a" case)
        for app in apps_in_additions:  # <app> XML elements
            for child in app:
                old_wit_value = child.get('wit')
                if '#a' in old_wit_value:
                    new_wit_value = old_wit_value.replace('#a', '#a2')
                    child.set('wit', new_wit_value)

    def edit_tei_header(self):
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

    def check_garufi_and_bonetti(self, app):
        ''' Argument: an <app> element. Return True or False.
            Check if the <app> is in the following case:
                - Bonetti is collation exemplar (i.e. 'print' reading)
                - there is only one MS (A or A2)
                - but Garufi has a reading that's different than Bonetti's.
            So we have 3 <rdg>s with 3 variants:
                - 1 for Bonetti,
                - 1 for MS A or A2,
                - 1 for Garufi '''
        response = False
        witnesses = [child.get('wit') for child in app]
        if (len(app) == 3
                and '#b' in witnesses
                and '#g' in witnesses):
            response = True
        return response

    def appdict(self):
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
                'subtype' = this will become the value of @subtype in <app>
                    (e.g. 'y'), inherited from method
                    variantComparison().
                    The value of @type will be set only at the end, by method
                    set_type_and_subtype_xml_attrib_in_all_apps()
                ...plus new additional keys:
                'app' = the <app> XML element
                'printReading' = the <rdg> or <lem> XML element of the
                    print edition (corresp. to printSiglum)
                'msaReading' = the <rdg> or <lem> XML element of MS A
                    (corresp. to msaSiglum)
                'msa2Reading' = the <rdg> or <lem> XML element of MS A,
                    hand 2, i.e. wit="#a2"
                    (corresp. to msaSiglum)
                'conjReading' = the <lem> XML element with my conjecture
                'msoReading' = the <rdg> or <lem> XML element of MS O
                    (if present; corresp. to msaSiglum)
                'printText' = the text (string) of the variant of the print
                    edition (corresp. to printSiglum)
                'msaText' = the text (string) of the variant of MS A
                    (corresp. to msaSiglum)
                'msoText' = the text (string) of the variant of MS O
                    (corresp. to msoSiglum)
                'conjText' = the text (string) of my conjecture
                'xmlid' = the xml:id of the parent <p>
        '''

        # This will become a list of dictionaries:
        comparisons = []
        for app in self.apps:

            #####################################################
            # Find <rdg> elements corresponding to each witness #
            #####################################################

            printReading = None
            msaReading = None
            msa2Reading = None
            msoReading = None
            conjReading = None

            for rdg in app:

                # Conjecture
                wit_value = rdg.get('wit')
                resp_value = rdg.get('resp')

                if wit_value is None and resp_value is not None:
                    # This should be a conjecture, so <lem resp="#pm">
                    # (no @wit attribute)
                    conjReading = rdg

                elif wit_value is None and resp_value is None:
                    print('[philologist / appdict] Attention:'
                          ' <app> {} has child {} {} with'
                          ' @wit «{}» and @resp {}\n'.format(
                              app.attrib, rdg, rdg.attrib,
                              wit_value, resp_value))

                # Regular reading from a witness
                else:
                    wit_list = wit_value.split()  # A list
                    if ('#%s' % self.printSiglum) in wit_list:
                        printReading = rdg
                    # Not elif, because @wit in <rdg> or <lem> can include
                    # more than one MS (e.g. <rdg wit="#b #a")
                    if ('#%s' % self.msaSiglum) in wit_list:
                        msaReading = rdg
                    if ('#%s' % self.msa2Siglum) in wit_list:  # Not elif
                        msa2Reading = rdg
                    if ('#%s' % self.msoSiglum) in wit_list:  # Not elif
                        msoReading = rdg

            # Debug
            if debug:
                print(('\n[philologist.py / appdict()] In file {},'
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

            ################################################
            # Set variables printText, msaText, msoText... #
            ################################################
            ''' Eventually, none of those elements will have
            text = None. If it was None, it is set to '' (this
            will come handy later '''

            # ...for print edition
            if printReading is not None:
                if printReading.text is None:
                    printReading.text = ''
                printText = printReading.text
            else:
                printText = ''

            # ... for MS A (if any)
            if msaReading is not None:
                if msaReading.text is None:
                    msaReading.text = ''
                msaText = msaReading.text
            else:
                msaText = ''

            # ... for MS A, hand 2 (if any)
            if msa2Reading is not None:
                if msa2Reading.text is None:
                    msa2Reading.text = ''
                msa2Text = msa2Reading.text
            else:
                msa2Text = ''

            # ... and for MS O (if any)
            if msoReading is not None:
                if msoReading.text is None:
                    msoReading.text = ''
                msoText = msoReading.text
            else:
                msoText = ''

            # ... and for the conjecture (if any)
            if conjReading is not None:
                if conjReading.text is None:
                    conjReading.text = ''
                conjText = conjReading.text
            else:
                conjText = ''

            ##############################
            # Find out the app structure #
            ##############################
            ''' I.e.: find out how many <rdg> elements <app> has
            and how many different variant texts, based
            on the chunk we are in (collation b/w 2 MSS
            or b/w 3 MSS) and on how many children it has'''

            app_struct = ''

            # Find out in which <p> we are
            # xmlid = app.getparent().get('{%s}id' % ns['xml'])
            xmlid = self.parent_xmlid(app)

            # These are the xmlids of the paragraphs for
            # which I collated 3 sources (print, A/A2 and O)
            pars_with_triple_collation = [
                r['xmlid'] for r in self.paragraphs
                if r['chunk'] == '2-bravo']

            # If we are not in the chunk in which I collated 3 sources:
            if xmlid not in pars_with_triple_collation:
                # This is the case in which Bonetti is collation exemplar,
                # there is only one MS (A or A2), but Garufi has a reading
                # that's different than Bonetti's. So I have 3 <rdg>s with
                # 3 variants: 1 for Bonetti, 1 for MS A or A2, 1 for Garufi
                if self.check_garufi_and_bonetti(app):
                    app_struct = '3elements3variants_bonetti_and_garufi'
                else:
                    app_struct = '2elements2variants'
            # If we are in that chunk, there must be 3 variants
            # (1st variant = print;  2nd variant =  A or A2, 3. O),
            # but they can be in 2 or 3 elements
            else:
                if len(app) > 3:
                    print(('[philologist.py / setappStruct] An <app>'
                           ' in {} has more than 3 children').format(
                               app.getparent().get(
                                   '{%s}id' % ns['xml'])))
                elif len(app) == 3:
                    app_struct = '3elements3variants'
                elif len(app) == 2:
                    app_struct = '2elements3variants'

            # debug:
            if app_struct == '':
                print(('[philologist.py / setappStruct] I could'
                       ' not set the app_struct for an <app>'
                       ' in {}').format(
                           app.getparent().get(
                               '{%s}id' % ns['xml'])))

            if debug:
                print(xmlid, app_struct, end=' | ')

            ################################
            # Create the output dictionary #
            ################################
            ''' MyComp is a dictionary, including the subtype of the variant,
            and 'comparisons' is a list of dictionaries)'''

            # In these 2 cases, import dict from variantComparison()
            if (app_struct == '2elements2variants'
                    or app_struct == '2elements3variants'):
                # I need to identify ther other child of <app>,
                # different from printReading

                non_print_child = self.find_non_print_child_in_two(
                    app, printReading)
                # I am assuming that that 'text' is never None
                # (if it was None, it was set to '' earlier)
                if non_print_child.text is None:
                    print(('[philologist.py / setappStruct] The'
                           ' text of a child of <app> is None'
                           ' in {}. The print text is {}').format(
                               app.getparent().get(
                                   '{%s}id' % ns['xml']),
                               printText
                           ))
                myComp = variant_subtype.variantComparison(
                    printText,
                    non_print_child.text)

            # In the other cases, I'll do without function
            # variantComparison() and create the dict anew
            elif app_struct == '3elements3variants':
                myComp = {'r1': '',
                          'r2': '',
                          'subtype': '3elements3variants'}
            elif app_struct == '3elements3variants_bonetti_and_garufi':
                myComp = {'r1': '',
                          'r2': '',
                          'subtype': '3elements3variants_bonetti_and_garufi'}

            # Set additional keys in dictionary myComp. See the documentation
            # of this method above for details.
            myComp['app'] = app
            myComp['xmlid'] = xmlid
            myComp['appStruct'] = app_struct
            myComp['printReading'] = printReading
            myComp['msaReading'] = msaReading
            myComp['msa2Reading'] = msa2Reading
            myComp['msoReading'] = msoReading
            myComp['conjReading'] = printReading
            myComp['printText'] = printText
            myComp['msaText'] = msaText
            myComp['msa2Text'] = msa2Text
            myComp['msoText'] = msoText
            myComp['conjText'] = conjText

            comparisons.append(myComp)

        return comparisons

    def variant_subtypes_list(self):
        '''Return a list all variant subtypes in <app> '''
        myList = [a['subtype'] for a in self.appdict()]
        return myList

    def variant_subtypes_count_set_list(self):
        '''Same as variant_subtypes_list, but it returns a list
            in which each element only occurs once'''
        mySet = set(self.variant_subtypes_list())
        # mySetList is still a list, but in which each element
        # of myList occurs only once
        mySetList = [t for t in mySet]
        return mySetList

    def variant_subtypes_count(self):
        '''Return a dict like
            {'missing-in-ms': 124,
            'missing-in-print-vs-punct-in-ms': 252 etc.}
            counting in how many <app> elements in the juxtaTree each
            variant subtype recurs '''
        myList = self.variant_subtypes_list()
        myListCount = []    # A list (of tuples)
        for x in self.variant_subtypes_count_set_list():
            # Add a new tuple to the list
            myListCount.append((x, myList.count(x)))
        # Ordered from highest number to lowest:
        myListCount = sorted(myListCount, key=operator.itemgetter(1),
                             reverse=True)
        return myListCount

    def variant_subtypes_count_print(self):
        '''Print out variant_subtypes_count'''
        if not self.quiet:
            print(('\n[phylologist.py / '
                   'variant_subtypes_count_print]: '
                   'In file {} there are:').format(self.juxtaSiglum))
            for x in self.variant_subtypes_count():
                print('{:5} {:12}'.format(x[1], x[0]))

    def find_and_locate_sic_corr(self):
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
            for a in self.appdict():
                # ...but I guess that it should only be
                # if a[sicText] == a[printText] (not also corrText)
                '''if c['corrText'].lower() == a['printText'].lower() or \
                   c['sicText'].lower() == a['printText'].lower():'''
                if c['sicText'].lower() == a['printText'].lower():
                    count += 1
                    if not self.quiet:
                        print(('[find_and_locate_sic_corr] '
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

    def parent_xmlid(self, app_element):
        ''' Each <app> is child of a <p>. Get @xml:id of that <p>
            (useful for debug messages) '''
        return app_element.getparent().get('{%s}id' % ns['xml'])

    def find_non_print_child_in_two(self,
                                    app_element,
                                    print_child):
        '''Input an <app> element and its print child.
            Return the other child, that does not include '''
        non_print_child = None
        for child in app_element:
            if child != print_child:
                non_print_child = child
        if non_print_child is None:
            # Good debug message
            print(('\n[philologist.py/find_non_print_child_in_two]'
                   ' I can\'t find the non-print element in {},'
                   ' \nparagraph {}, \n<{}> {}.'
                   ' \nThe print reading is <{}> {}\nwith text «{}»\n').format(
                       self.juxtaSiglum,
                       self.parent_xmlid(app_element),
                       etree.QName(app_element).localname,
                       app_element.attrib,
                       etree.QName(print_child).localname,
                       print_child.attrib,
                       print_child.text))
        return non_print_child

    def set_all_lems_based_on_subtype(self, setCert=True):
        '''For some subtype(s) of <app>, decide the <lem> automatically
            based on that @subtype. If the <app> has 3 children,
            subtype is 3elements3variants, which has preferred
            reading 'p' (i.e. print), which is handled very simply and
            effectively, so this method also works in that case'''

        # Decide <lem> and set @cert based on DB
        # table variant_subtypes:

        for a in self.appdict():
            for myRow in self.variant_subtypes:

                # E.g.: 'different-punct':
                if a['subtype'] == myRow['subtype']:
                    # db_preferredRdg can be
                    # 'p (reading of the print edition) or
                    # 'm' (reading of one of the MSS)
                    db_preferredRdg = myRow['preferredRdg']

                    if db_preferredRdg == 'p':
                        self.make_lem(a['printReading'])

                    elif db_preferredRdg == 'm':
                        # We can assume that <app> only has 2 children:
                        # see the initial comment of this method
                        my_non_print_rdg = self.find_non_print_child_in_two(
                            a['app'], a['printReading'])
                        self.make_lem(my_non_print_rdg)

                    else:
                        print(('\n[set_all_lems_based_on_subtype] I couln\'t'
                               ' read table variant_subtypes'
                               ' from the DB properly. My db_preferredRdg'
                               ' is {}').format(db_preferredRdg))

                    if setCert is True:
                        # myCert can be 'low', 'middle' or 'high':
                        myCert = myRow['cert']
                        # Better not use namespaces when setting
                        # TEI attributes!
                        # a['app'].set('{%s}cert' % ns['t'], myCert)
                        a['app'].set('cert', myCert)

    def set_lem_based_on_db_2elements(self, a):
        ''' This manages two cases:
            1) a['appStruct'] = 2elements_2readings
                <rdg wit="#a">
                <rdg wit="#b">
            and
            2) a['appStruct'] = 2elements_3readings, e.g.
                <rdg wit="#b #a">
                <rdg wit="#o"> (or   #b+#o   vs   #a)
                or
                <rdg wit="#b">
                <rdg wit="#a #o">
                ... or the same with #a2 instead of #a
            (see lines with if/elif r['action'] for details).
            '''

        #################################################
        # Identify print and non-print element and text #
        #################################################

        # my_print_rdg is the <rdg> that _includes_ #g or #b
        # among its witnesses (e.g. it can be #b alone, or "#b #a",
        # or "#b #o" etc.)'''
        my_print_rdg = a['printReading']
        my_print_text = a['printReading'].text

        # my_non_print_rdg is the other one (its witnesses can
        # be one or two, but they are only MSS, not print edition)
        my_non_print_rdg = self.find_non_print_child_in_two(
            a['app'], a['printReading'])
        my_non_print_text = my_non_print_rdg.text

        ####################################################
        # Decide if the <app> corresponds to the DB record #
        ####################################################

        # For each record in the 'decisions' DB table:
        for r in self.decisions2:

            # If the print reading text in <app> is the same
            # of the print reading text in the DB record...
            # ('strip' is for readings/DB cells with space)
            # ('str' is to cope with cases in which the DB cell is Null)
            if(str(r['print']).strip() == my_print_text.strip()

               # and the MS reading text in the DB record is
               # the MS A reading text or MS A2 reading text
               # or MS O reading text in <app>
               and str(r['ms']).strip() == my_non_print_text.strip()

               # and we are in the right <p>...
               and (r['xmlid'] == a['xmlid']
                    # ...or the DB decision is to be applied in all cases
                    or r['xmlid'] == 'all')):

                ###################################
                # Set @subtype and @cert of <app> #
                ###################################

                # Set @type
                # (DB tables decisions2 and decisions3 always have a 'type')
                expanded_type = self.type_expansion[r['type']]
                a['app'].set('type', expanded_type)

                # Remove previous @subtype from <app>, if any
                if 'subtype' in a['app'].attrib:
                    a['app'].attrib.pop('subtype')

                # Set @subtype
                # If there is a subtype in the DB, set it in <app>
                if r['subtype'] is not None and r['subtype'] is not '':
                    a['app'].set('subtype', r['subtype'])

                # Set @cert="high"
                a['app'].set('cert', 'high')

                ############################
                # Set <lem> and <rdg> tags #
                ############################

                # Choose MS reading as 'correct'
                if r['action'] == 'm':
                    # Make print reading <rdg>
                    self.make_rdg(my_print_rdg)
                    # Make the non-print reading <lem>
                    self.make_lem(my_non_print_rdg)

                # Only change subtype. Print is 'correct', so
                # don't change <lem>/<rdg> (i.e. print reading stays <lem>),
                # only set @subtype (based on the DB) and set @cert=high
                # (both things were already done above)
                elif r['action'] == 't':
                    pass

                # Choose my conjecture as 'correct' reading
                elif r['action'] == 'conj':

                    # Make print reading <rdg>
                    self.make_rdg(my_print_rdg)
                    # Make the MS reading <rdg> too
                    self.make_rdg(my_non_print_rdg)

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
                    print(('[philologist.py/set_lem_based_on_db_2elements] '
                           'I don\'t understand the «{}» in the «action» '
                           'field in the DB record for app {}.').format(
                               r['action'], a))

        # Debug
        if not self.quiet:
            print(('[philologist.py/set_lem_based_on_db_2elements],'
                   '\npart m{},\norigin {}.\nPrint/MS: DB «{}»/«{}»'
                   '\n<app> «{}»/«{}»'
                   '\nParagraph {}\n').format(
                       r['origin'],
                       r['print'],
                       r['ms'],
                       a['printText'],
                       a['msaText'],
                       a['xmlid']))

    def set_lem_based_on_db_3elements(self, a):

        # Identify print element and text
        my_print_rdg = a['printReading']
        my_print_text = a['printReading'].text

        ####################################################
        # Decide if the <app> corresponds to the DB record #
        ####################################################

        for r in self.decisions3:

            # If the print reading text in <app> is the same
            # of the print reading text in the DB record...
            # ('strip' is for readings/DB cells with space)
            if(str(r['print']).strip() == my_print_text.strip()

               # and the MS A or MS A2 text reading
               # matches that of the DB record
               and (str(r['msa2']).strip() == a['msaText'].strip()
                    or str(r['msa2']).strip() == a['msa2Text'].strip())

               # and the MS O text reading
               # matches that of the DB record
               and str(r['mso']).strip() == a['msoText'].strip()

               # and we are in the right <p>...
               and (r['xmlid'] == a['xmlid']
                    # ...or the DB decision is to be applied in all cases
                    or r['xmlid'] == 'all')):

                ###################################
                # Set @subtype and @cert of <app> #
                ###################################

                # Set @type
                # (DB tables decisions2 and decisions3 always have a 'type')
                expanded_type = self.type_expansion[r['type']]
                a['app'].set('type', expanded_type)

                # Remove previous @subtype from <app>, if any
                if 'subtype' in a['app'].attrib:
                    a['app'].attrib.pop('subtype')

                # Set @subtype
                # If there is a subtype in the DB, set it in <app>
                if r['subtype'] is not None and r['subtype'] is not '':
                    a['app'].set('subtype', r['subtype'])

                # Set @cert="high"
                a['app'].set('cert', 'high')

                ############################
                # Set <lem> and <rdg> tags #
                ############################

                # The print reading will always be set to <rdg>
                self.make_rdg(my_print_rdg)

                # 'coris in one of the mss
                print(r['print'])  # §§§
                if r['action'] == 'm':

                    # Identify "correct" MS element and text
                    # based on on the 'lem' column in the decisions3 table
                    db_lem = r['lem_if_not_print']
                    my_correct_ms_rdg = None
                    if db_lem == 'msa':
                        my_correct_ms_rdg = a['msaReading']
                    elif db_lem == 'msa2':
                        my_correct_ms_rdg = a['msa2Reading']
                    elif db_lem == 'mso':
                        my_correct_ms_rdg = a['msoReading']
                    elif db_lem == 'g':
                        my_correct_ms_rdg = a['g']
                    if my_correct_ms_rdg is None:
                        # Good debug message:
                        print(('\n[philologist.py/'
                               'set_lem_based_on_db_3elements]'
                               ' I can\'t find the "correct" MS reading'
                               ' in {}, <app> {}.').format(
                                   self.juxtaSiglum, a))

                    my_correct_ms_text = my_correct_ms_rdg.text
                    if debug:
                        print(('\n[philologist.py/'
                               'set_lem_based_on_db_3elements]'
                               ' The "correct" text in triple <app>'
                               ' in {},\nparagraph {}, \n<{}> {},'
                               ' is {}.'
                               ' \nThe print reading is <{}> {}'
                               ' \nwith text «{}»\n').format(
                                   self.juxtaSiglum,
                                   a['xmlid'],
                                   etree.QName(a['app']).localname,
                                   a['app'].attrib,
                                   my_correct_ms_text,
                                   etree.QName(a['printReading']).localname,
                                   a['printReading'].attrib,
                                   a['printReading'].text))

                    # Make the "correct" MS element <lem>
                    self.make_lem(my_correct_ms_rdg)

                # Only change subtype. Print is 'correct', so
                # don't change <lem>/<rdg> (i.e. print reading stays <lem>),
                # only set @subtype (based on the DB) and set @cert=high
                # (both things were already done above)
                elif r['action'] == 't':
                    pass

                # 'correct' rdg is my conjecture.
                # I never tested this elif
                elif r['action'] == 'conj':

                    # Make all readings <rdg>
                    for child in a['app']:
                        self.make_rdg(child)

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
                    print(('[philologist.py/set_lem_based_on_db_3elements] '
                           'I don\'t understand the «{}» in the «action»'
                           'field in the DB record for app {}.').format(
                               r['action'], a))

    def set_lem_based_on_db_3elements_bonetti_and_garufi(self, a):
        ''' See definition of method check_garufi_and_bonetti() for
            details about this case '''

        ##################################################################
        # Identify print=Bonetti, MS and extra Garufi elements and texts #
        ##################################################################

        # I need to identify the 3 elements/texts with a different approach
        app = a['app']
        for child in app:
            if child.get('wit') == '#b':
                b_reading = child
                b_text = b_reading.text
            elif (child.get('wit') == '#a' or
                    child.get('wit') == '#a2'):
                ms_reading = child
                ms_text = ms_reading.text
            elif child.get('wit') == '#g':
                g_reading = child
                g_text = g_reading.text
            else:
                print(('[philologist.py/'
                       'set_lem_based_on_db_3elements_bonetti_and_garufi]'
                       ' I think that app <app> {} belongs to case'
                       ' 3elements3variants_bonetti_and_garufi, but I can\'t'
                       ' find the Bonetti, MS and Garufi readings in the'
                       ' <app>').format(a))

        ####################################################
        # Decide if the <app> corresponds to the DB record #
        ####################################################

        for r in self.decisions3:

            # If the print (Bonetti) reading text in <app> is the same
            # of the print reading text in the DB record...
            # ('strip' is for readings/DB cells with space)
            if(str(r['print']).strip() == b_text.strip()

               # and the MS A or MS A2 text reading
               # matches that of the DB record
               and (str(r['msa']).strip() == ms_text.strip()
                    or str(r['msa2']).strip() == ms_text.strip())

               # and the extra Garufi text reading
               # matches that of the DB record
               and str(r['g']).strip() == g_text.strip()

               # and we are in the right <p>...
               and (r['xmlid'] == a['xmlid']
                    # ...or the DB decision is to be applied in all cases
                    or r['xmlid'] == 'all')):

                ###################################
                # Set @subtype and @cert of <app> #
                ###################################

                # Set @type
                # (DB tables decisions2 and decisions3 always have a 'type')
                expanded_type = self.type_expansion[r['type']]
                a['app'].set('type', expanded_type)

                # Remove previous @subtype from <app>, if any
                if 'subtype' in a['app'].attrib:
                    a['app'].attrib.pop('subtype')

                # Set @subtype
                # If there is a subtype in the DB, set it in <app>
                if r['subtype'] is not None and r['subtype'] is not '':
                    a['app'].set('subtype', r['subtype'])

                # Set @cert="high"
                a['app'].set('cert', 'high')

                ############################
                # Set <lem> and <rdg> tags #
                ############################

                # Set all children of <app> to <rdg> to start with:
                for child in app:
                    self.make_rdg(child)

                if (r['lem_if_not_print'] == 'msa' or
                        r['lem_if_not_print'] == 'msa2'):
                    self.make_lem(ms_reading)
                elif r['lem_if_not_print'] == 'g':
                    self.make_lem(g_reading)
                # This should never be the case:
                #  if r['lem_is_not_print'] == 'mso':
                else:
                    print(('[philologist.py/'
                           'set_lem_based_on_db_3elements_bonetti_and_garufi]'
                           ' I can\'t find the variant to choose in the DB'
                           ' table. I\'m working on <app> {}. DB column'
                           'lem_if_not_print has «{}»').format(
                               a, r['lem_if_not_print']))

    def set_all_lems_based_on_db(self):
        '''Read DB table and decide <lem> for the <app>s
            that match a DB record '''

        for a in self.appdict():

            if (a['appStruct'] == '2elements2variants'
                    or a['appStruct'] == '2elements3variants'):
                self.set_lem_based_on_db_2elements(a)
            elif a['appStruct'] == '3elements3variants':
                # 42 cases
                self.set_lem_based_on_db_3elements(a)
            elif a['appStruct'] == '3elements3variants_bonetti_and_garufi':
                # Very few cases
                self.set_lem_based_on_db_3elements_bonetti_and_garufi(a)

    def handle_case_variants(self):
        ''' If the variant is of case, change its structure, from
            <app subtype="case">
                <lem wit="#a">Occidentis</lem>
                <rdg wit="#b #o">occidentis</rdg>
            </app>
            to
            <app subtype="case">
                <lem resp="#pm">Occidentis</lem>
                <rdg wit="#a #b #o">occidentis</rdg>
            </app>
            Assumptions: 1. <lem> has uppercase; 2. <lem> it is a MS reading;
                3. print reading is in a <rdg>; 4. <app> only has 2 children
                (though the MSS can be three, if we are in 2-bravo)
        '''
        apps_with_case_subtype = [a for a in self.appdict() if a['subtype'] ==
                                  'case']
        for a in apps_with_case_subtype:
            app = a['app']
            if len(app) > 2:
                print(('[philologist.py/handle_case_variants] <app> {}'
                       ' with @subtype=case has more than 2 children'
                       ' and I can\'t handle it.').format(a))
            else:
                print_child = a['printReading']  # an XML element
                non_print_child = self.find_non_print_child_in_two(
                    app, print_child)  # another XML element
                # Check that we are in the situation of the above assumptions
                # (about 90 cases / 123 cases of case)
                if (non_print_child.tag == '{%s}lem' % ns['t'] and
                        non_print_child.text.istitle() and
                        print_child.tag == '{%s}rdg' % ns['t']):
                    # Change <rdg wit="#b #o">occidentis</rdg> to
                    # <rdg wit="#b #o #a">occidentis</rdg>
                    non_print_wit = non_print_child.get('wit')  # probably '#a'
                    old_print_wit = print_child.get('wit')  # e.g. '#b #o'
                    # It will become (e.g.) '#b #o #a':
                    new_print_wit = ' '.join([old_print_wit, non_print_wit])
                    print_child.set('wit', new_print_wit)
                    # Change <lem wit=#a">Occidentis</rdg> to
                    # <lem resp="#pm">Occidentis</rdg>
                    non_print_child.attrib.pop('wit')  # remove @wit
                    non_print_child.set('resp', '#pm')  # remove @wit

                # If, instead, we're in a strange situation, do nothing
                # (about 33 cases/123 cases of case: I'll handle them
                #   manually)
                else:
                    if debug:
                        print(('[philologist.py/handle_case_variants] <app>'
                               ' {} has @subtype=case but I can\'t'
                               ' handle it.\n\tPrint text: «{}»\n\tMS text:'
                               ' «{}»').format(
                                   app.attrib, print_child.text,
                                   non_print_child.text))

    def set_type_and_subtype_xml_attrib_in_all_apps(self):
        ''' Set XML TEI @type and @subtype attributes in
            <app> elements of the XML file.
            @subtype will be based on the 'subtype' key in appdict(),
            @type will be derive from subtype, based on DB table
            variant_subtypes.
            This method applies only if <app> (i.e. a['app']) does
            not have a @type (and possibly also @subtype) already set by
            methods such as set_lem_based_on_db_2elements.
            '''
        # Read DB table variant_subtypes and create
        # a dict corresponding_type looking like:
        # {'y': 'ortographic',
        # 'different-punct': 'punctuation'} etc.
        corresponding_type = {}
        for r in self.variant_subtypes:
            my_subtype = r['subtype']
            my_type = r['type']
            corresponding_type[my_subtype] = my_type
        if debug:
            print('\n---\n')
            for x in corresponding_type:
                print('«{}»\t→\t«{}»'.format(x, corresponding_type[x]))

        for a in self.appdict():
            # <app> has @type only if it has been set by a method
            # such as set_lem_based_on_db_2elements. It that's the
            # case, @type (and possibly also @subtype, if present in
            # the decisions2 or decisions3 DB table) has/have been set
            # by that method, so don't set them here.
            # If, instead, there is no @type...
            if 'type' not in a['app'].attrib:
                # Set @subtype
                a['app'].set('subtype', a['subtype'])
                # ...and the corresponding @type derived from DB table
                # variant_subtypes
                my_type = corresponding_type[a['subtype']]
                a['app'].set('type', my_type)

            if debug:
                print('\n')
                print('«%s» | «%s» %15s @subtype="%s"' %
                      (a['printText'], a['msaText'], '·', a['subtype']))
                for k in a:
                    print('%s: «%s»' % (k, a[k]))

    def checkout_checked_paragraphs(self):
        ''' For all paragraphs that in table 'paragraphs' of the DB
            have 'checked'=1, 2 or any number higher than 0, in <app>s
            - set cert to high for all
            - set @type and @subtype for those 'unknown' that I left unchanged
            See table 'check_levels' in the DB for the meaning of values of
            field 'checked' in table 'paragraphs'
            '''
        # @types of <app> that have to change:
        type_subst = {'unknown': 'substantial'}

        # Get a list with xmlids of checked paragraphs
        pars = [x['xmlid'] for x in self.paragraphs if x['checked'] > 0]

        for a in self.appdict():
            app = a['app']
            if a['xmlid'] in pars:

                # Set <app cert="high">
                app.set('cert', 'high')

                # Make the substitutions in the dictionaries above:
                for x in type_subst:
                    if x == app.get('type'):
                        app.set('type', type_subst[x])

                # If @subtype remained 'unknown' after the
                # substitutions, remove it (note that currently subtype
                # '3elements3variants' remains with type 'substantial'
                # also after the checkout
                if app.get('subtype') == 'unknown':
                    app.attrib.pop('subtype')

                # Gap in the MS.
                for child in app:
                    txt = child.text
                    # If the textual content is like 'Gap1IllegibleWord'
                    if (txt.startswith('Gap') and txt[3:4].isdigit()):
                        # Replace 'Gap1IllegibleWord' or the like
                        # with '{Gap in the MS: 1 illegible word}'
                        txt = txt.capitalize()
                        # Find the digit part ('1', in the example above)
                        dgt_list = [char for char in txt if char.isdigit()]
                        dgt_string = ''.join(dgt_list)
                        txt = txt.replace(
                            dgt_string, ' in the MS: %s ' % dgt_string)
                        txt = txt.replace('word', ' word')
                        txt = '{%s}' % txt
                        child.text = txt
                        # I'll set type and subtype through the DB

    def put_lem_as_1st_in_app_and_beautify_app(self):
        ''' 1. part: In the TEI DTD, <lem> must be the first child of <app>.
                This method puts <lem> first
            2. part: Beautify markup around app:
                - </app> is always followed by a space.
                  If </app> is followed by space and punctuation "</app> .",
                  remove the space
            '''

        # This tuple includes punctuation chars before which
        # there should be no space
        punct = ('!', ')', ',', '.', ':', ';', '?', ']', '}')

        for a in self.appdict():
            app = a['app']
            # 1. part
            for child in app:
                # If the child is a <lem>:
                if child.tag == '{%s}lem' % ns['t']:
                    if app.index(child) > 0:
                        # Move <lem> as first child of <app:
                        app.insert(0, child)
                        # Pretty print:
                        child.tail = '\n   '
                        app[-1].tail = '\n'
            # 2. part
            char1 = app.tail[0]  # 1st character after </app>
            char2 = app.tail[1]  # 2st character after </app>
            if char1 == ' ' and char2 in punct:
                app.tail = app.tail[1:]  # Remove 1st char (space)

    def beautify_paragraphs(self):
        ''' Pretty print the beginning of each <p> (see below
            for details) '''
        pars = self.juxtaBody.findall('.//t:%s' % ('p'), ns)
        for p in pars:
            if p.text.strip() == '':
                '''In the output, if opening tag <p> has no actual text
                afterwards, but only two "\n\n" (i.e. an empty line) and
                an opening tag <app>, change "\n\n"  to "\n" '''
                p.text = '\n'
            elif p.text.startswith('\n '):
                # 2. part/B
                '''If the first line of text in <p> starts with a space,
                remove the space '''
                p.text = p.text.replace('\n ', '\n')

    def handle_no_collation_paragraphs(self):
        ''' Case 1: not_in_mss
                Those paragraphs (e.g. g179.10-179.11) that are only
                in Bonetti and in no MS (neither A or O): just use the
                text of Bonetti without any <app> and without quotes
            Case 2: not_in_print
               Those paragraphs (g258.1-258.7surplus; i don't know if there
               are others) that are only in the MS (in g258.1-258.7surplus, in
               A2) but are not published by Bonetti: just use my
               transcription from the MS without any <app>
                '''

        # 1. Paragraphs missing in MSS
        # Get a list with xmlids of paragraphs  missing in MSS
        xmlids = [x['xmlid'] for x in self.paragraphs
                  if (x['no_collation'] == 'not_in_mss'
                      or x['no_collation'] == 'not_in_print')]
        for x in xmlids:
            # print('\nxmlid = ', x)  # debug
            par = self.juxtaBody.find('.//t:p[@xml:id="%s"]' % (x), ns)
            # par can be None (not found) because we are in the
            # wrong chunk (e.g. the xmlid is in m2-alfa, but the script
            # is processing m2-bravo
            if par is not None:
                if len(par) > 1:
                    # Normally those <p>s should include no text
                    # and only one <app>
                    print(('[philologist.py handle_no_collation_paragraphs]'
                           ' Attention: no-collation paragraph {} has more'
                           ' than one <app> child').format(x))
                else:
                    # Get new text for <p>
                    new_text = ''.join(par.itertext())
                    # Strip existing '\n' (they are too many), then add '\n'
                    # before and after
                    new_text = '\n%s\n' % new_text.strip()
                    # Remove Bonetti's quotes
                    new_text = new_text.replace('"', '')
                    # Empty <p> (remove <app> and its children)
                    for c in par:
                        par.remove(c)
                    # Add '\n' before and after, then attribute new text
                    # directly to <p>
                    par.text = '\n%s\n' % new_text.strip()

    def handle_print_edition_headings(self):
        ''' Empty those paragraphs (e.g. b062heading, v-b298a or v-b298b)
            that only include Garufi's or Bonetti's headers (e.g.
            "Romoaldi II archiepiscopi salernitani annales" '''
        xmlids = [x['xmlid'] for x in self.paragraphs
                  if x['no_collation'] == 'heading']
        for x in xmlids:
            # print('\nxmlid = ', x)  # debug
            par = self.juxtaBody.find('.//t:p[@xml:id="%s"]' % (x), ns)
            # par can be None (not found) because we are in the
            # wrong chunk (e.g. the xmlid is in m2-alfa, but the script
            # is processing m2-bravo
            if par is not None:
                # Empty <p> (remove <app> and its children)
                for c in par:
                    par.remove(c)
                # Remove par.text, if any
                par.text = ''

    def remove_lb_between_paragraphs(self):
        ''' Sometimes JuxtaCommons inserts some useless <lb/> at the end
            of its output files (such as m2-alfa1.xml). Remove them'''
        lbs = self.juxtaBody.findall('.//t:lb', ns)
        for lb in lbs:
            # Restore empty line between two <p>s
            previous = lb.getprevious()
            if previous.tag == '{%s}p' % ns['t']:
                previous.tail = '\n\n'
            # Remove <lb/>
            lb.getparent().remove(lb)

    def write(self):
        ''' Write my XML juxtaTree to an external file '''
        self.juxtaTree.write(self.outputXmlFile,
                             encoding='UTF-8', method='xml',
                             pretty_print=True, xml_declaration=True)
