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
        self.variant_types_and_subtypes = my_database_import.import_table(
            dbpath,
            dbname,
            'variant_types_and_subtypes')

        # This dictionary will be used by a method that will be
        # repeated many times. It expands abbreviations of 'type'
        # field in DB tables decisions2 and decisions3
        self.type_expansion = {
            's': 'substantial',
            'o': 'orthography',
            'p': 'punctuation',
            'u': 'unknown'
        }

    def set_a2_for_additions(self):
        ''' In sections that are additions by hand2, replace wit="a" with
            wit="a2" '''

        # Create a list with the xml:id's of those <p>s
        additions_xmlids = [x['xmlid'] for x in self.paragraphs
                            if x['xmlid'] == 1]

        # All <p>s in the XML document
        pars = self.juxtaBody.findall('.//t:%s' % ('p'), ns)

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
                    (e.g. 'y-subtype'), inherited from method
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
                    wit = wit_value.split()  # A list
                    if ('#%s' % self.printSiglum) in wit:
                        printReading = rdg
                    if ('#%s' % self.msaSiglum) in wit:  # Not elif
                        msaReading = rdg
                    if ('#%s' % self.msa2Siglum) in wit:  # Not elif
                        msa2Reading = rdg
                    if ('#%s' % self.msoSiglum) in wit:  # Not elif
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
                app_struct = '2elements2variants'
            # If we are in that chunk, there must be 3 variants
            # (1. print, 2. A or A2, 3. O)
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

            # In this 3rd case, I'll do without function
            # variantComparison() and create the dict anew
            elif app_struct == '3elements3variants':
                myComp = {'r1': '',
                          'r2': '',
                          'subtype': '3elements3variants-subtype'}

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
            {'missing-in-ms-subtype': 124,
            'missing-in-print-vs-punct-in-ms-subtype': 252 etc.}
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
            subtype is 3elements3variants-subtype, which has preferred
            reading 'p' (i.e. print), which is handled very simply and
            effectively, so this method also works in that case'''

        # Decide <lem> and set @cert based on DB
        # table variant_types_and_subtypes:

        for a in self.appdict():
            for myRow in self.variant_types_and_subtypes:

                # E.g.: 'different-punct-subtype':
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
                               ' read table variant_types_and_subtypes'
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
            if(r['print'] == my_print_text

               # and the MS reading text in the DB record is
               # the MS A reading text or MS A2 reading text
               # or MS O reading text in <app>
               and r['ms'] == my_non_print_text

               # and we are in the right <p>...
               and (r['xmlid'] == a['xmlid']
                    # ...or the DB decision is to be applied in all cases
                    or r['xmlid'] == 'all')):

                ###################################
                # Set @subtype and @cert of <app> #
                ###################################

                # Set @type
                # (DB table decisions2 and decisions3 always have a 'type')
                expanded_type = self.type_expansion[r['type']]
                a['app'].set('type', expanded_type)

                # Remove previous @subtype from <app>, if any
                if 'subtype' in a['app'].attrib:
                    a['app'].attrib.pop('subtype')

                # Set @subtype
                # (in most cases DB table decisions2 and decisions3
                #  won't have a 'subtype')
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
                           'I don\'t understand the «{}» field '
                           'in the DB record for app {} {}. ').format(
                               r['action'], a['app'], a['app'].attrib))

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
            if(r['print'] == my_print_text

               # and the MS A or MS A2 text reading
               # matches that of the DB record
               and (r['msa'] == a['msaText']
                    or r['msa2'] == a['msa2Text'])

               # and the MS O text reading
               # matches that of the DB record
               and r['mso'] == a['msoText']

               # and we are in the right <p>...
               and (r['xmlid'] == a['xmlid']
                    # ...or the DB decision is to be applied in all cases
                    or r['xmlid'] == 'all')):

                ###################################
                # Set @subtype and @cert of <app> #
                ###################################

                # Set @type
                # (DB table decisions2 and decisions3 always have a 'type')
                expanded_type = self.type_expansion[r['type']]
                a['app'].set('type', expanded_type)

                # Remove previous @subtype from <app>, if any
                if 'subtype' in a['app'].attrib:
                    a['app'].attrib.pop('subtype')

                # Set @subtype
                # (in most cases DB table decisions2 and decisions3
                #  won't have a 'subtype')
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

                # 'correct' rdg is in one of the mss
                if r['action'] == 'm':

                    # Identify "correct" MS element and text
                    # based on on the 'lem' column in the decisions3 table
                    db_lem = r['lem']
                    my_correct_ms_rdg = None
                    if db_lem == 'msa':
                        my_correct_ms_rdg = a['msaReading']
                    elif db_lem == 'msa2':
                        my_correct_ms_rdg = a['msa2Reading']
                    elif db_lem == 'mso':
                        my_correct_ms_rdg = a['msoReading']
                    if my_correct_ms_rdg is None:
                        # Good debug message:
                        print(('\n[philologist.py/'
                               'set_lem_based_on_db_3elements]'
                               ' I can\'t find the "correct" MS reading'
                               ' in {},\nparagraph {}, \n<{}> {}.'
                               ' \nThe print reading is <{}> {}'
                               ' \nwith text «{}»\n').format(
                                   self.juxtaSiglum, self.parent_xmlid(a),
                                   etree.QName(a).localname, a.attrib,
                                   etree.QName(a['printReading']).localname,
                                   a['printReading'].attrib,
                                   a['printReading'].text))

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

                # 'correct' rdg is my conjecture
                elif r['action'] == 'conj':
                    # If there will be such a case, I'll write the code for it
                    pass

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

    def set_type_and_subtype_xml_attrib_in_all_apps(self):
        ''' Set XML TEI @type and @subtype attributes in
            <app> elements of the XML file.
            @subtype will be based on the 'subtype' key in appdict(),
            @type will be derive from subtype, based on DB table
            variant_types_and_subtypes.
            This method applies only if <app> (i.e. a['app']) does
            not have a @type (and possibly also @subtype) already set by
            methods such as set_lem_based_on_db_2elements.
            '''
        # Read DB table variant_types_and_subtypes and create
        # a dict corresponding_type looking like:
        # {'y-subtype': 'ortographic,
        # 'different-punct-subtype': 'punctuation'} etc.
        corresponding_type = {}
        for r in self.variant_types_and_subtypes:
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
                # variant_types_and_subtypes
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
            have 'checked'=1, in <app>s
            - set cert to high for all
            - set @type and @subtype for those 'unknown' that I left unchanged
            '''
        # @types of <app> that have to change:
        type_subst = {'unknown': 'substantial'}
        # @subtypes of <app> that have to change
        # (this is empty so far. I might populate it at some point):
        subtype_subst = {}

        # Get a list with xmlids of checked paragraphes
        pars = [x['xmlid'] for x in self.paragraphs if x['checked'] == 1]

        for a in self.appdict():
            if a['xmlid'] in pars:

                # Set <app cert="high">
                a['app'].set('cert', 'high')

                # Make the substitutions in the dictionaries above:
                for x in type_subst:
                    if x == a['app'].get('type'):
                        a['app'].set('type', type_subst[x])
                for y in type_subst:
                    if y == a['app'].get('subtype'):
                        a['app'].set('subtype', subtype_subst[y])

                # If @subtype remained 'unknown-subtype' after the
                # substitutions, remove it
                if a['app'].get('subtype') == 'unknown-subtype':
                    a['app'].attrib.pop('subtype')

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

    def write(self):
        ''' Write my XML juxtaTree to an external file '''
        self.juxtaTree.write(self.outputXmlFile,
                             encoding='UTF-8', method='xml',
                             pretty_print=True, xml_declaration=True)
