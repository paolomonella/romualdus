#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module makes textual statistics,
    then appends them to the <front> of chronicon.xml

     Possible to-do's:
    - Add characters count? (already in the teiHeader)
    - Count 'num' and 'rs' (and 'hi'?) in transcription files
    - <pb>: how many words per page
    '''

from lxml import etree
from myconst import ns, xmlpath, chronicon_output_file
from myconst import stats_template, stats_filled
from string import punctuation


def insertnum(ancestor, number, n):
    ''' Insert the number provided in the 2nd argument
        as text of the <num> with @n whose value is provided in the
        'n' argument, and as value of its @value attribute.
        Example: if it's
        insert(tree, 4, 's-subst')
        then change <num n="s-subst"/> to <num n="s-subst">4</seg> '''

    elements = ancestor.findall('.//t:num[@n="%s"]' % n, ns)
    if elements is []:
        print(('Subtype {} not found'
              '').format(n))
    number_str = str(number)
    for e in elements:
        e.text = number_str
        e.set('value', number_str)


def text_strip_punct(element):
    text_in_el = ' '.join(element.itertext())
    for punct in punctuation:
        text_in_el = text_in_el.replace(punct, '')
    return text_in_el


'''
def count_words_in_tagname(my_tree, tagname):
'''
''' Example: if tagname is '<lem>, count how
        many words are in the text are tagged with <lem>
        in all document '''
'''
    my_words = []
    my_elements = my_tree.findall('.//t:%s' % tagname, ns)
    for my_element in my_elements:
        my_text = text_strip_punct(my_element)
        my_words = my_text.split()  # A list
        for my_word in my_words:
            my_words.append(my_word)
    length_my_words = len(my_words)
    return length_my_words
'''


def recalculate_statistics(include_general=False):
    ''' tree is the tree of the chronicon.xml file
        div is the <div> in which statistics must be written '''

    # Parse stats_template file and find div
    template_path = '%s%s' % (xmlpath, stats_template)
    template_tree = etree.parse(template_path)
    div = template_tree.find('.//t:div[@n="statistics"]', ns)

    # Parse stats_filled file
    filled_path = '%s%s' % (xmlpath, stats_filled)
    filled_tree = etree.parse(filled_path)
    old_filled_div = filled_tree.find('.//t:div[@n="statistics"]', ns)
    old_filled_div.getparent().remove(old_filled_div)
    filled_root = filled_tree.getroot()

    filled_root.append(div)

    # Import chronicon.xml
    chronicon_path = '%s%s' % (xmlpath, chronicon_output_file)
    tree = etree.parse('%s%s' % (xmlpath, chronicon_path))

    ################
    # Initializing #
    ################

    # Total of <app> elements
    apps = tree.findall('.//t:app', ns)
    s_apps = len(apps)
    insertnum(div, s_apps, 's-apps')

    #################################
    # Total variants (V) and types #
    #################################

    # Total of actual variants
    v = 0

    # Substantive
    s_subst = len(tree.findall('.//t:app[@type="%s"]' % 'substantive', ns))
    insertnum(div, s_subst, 's-subst')
    v = v + s_subst

    # Transposition (double)
    s_trans_double = len(tree.findall('.//t:app[@type="%s"]'
                                      % 'transposition', ns))
    insertnum(div, s_trans_double, 's-trans-double')

    # Transposition (single)
    s_trans_single = int(s_trans_double / 2)
    insertnum(div, s_trans_single, 's-trans-single')
    v = v + s_trans_single

    # Orthographic
    s_orth = len(tree.findall('.//t:app[@type="%s"]' % 'orthographic', ns))
    insertnum(div, s_orth, 's-orth')

    # Subtype="case"
    s_case = len(tree.findall('.//t:app[@subtype="%s"]' % 'case', ns))

    # Orthographic except case
    s_orth_except_case = s_orth - s_case
    insertnum(div, s_orth_except_case, 's-orth-except-case')
    v = v + s_orth_except_case

    # Gap-in-ms
    s_gap = len(tree.findall('.//t:app[@type="%s"]' % 'gap-in-ms', ns))
    insertnum(div, s_gap, 's-gap')

    # Illegible-in-ms
    s_ill = len(tree.findall('.//t:app[@type="%s"]' % 'illegible-in-ms', ns))
    insertnum(div, s_ill, 's-ill')

    # Punctuation
    s_punct = len(tree.findall('.//t:app[@type="%s"]' % 'punctuation', ns))
    insertnum(div, s_punct, 's-punct')

    # V: total actual variants
    insertnum(div, v, 's-var')

    # Percentages of V (@type's)
    s_perc_subst = "%.1f" % (s_subst / v * 100)
    insertnum(div, s_perc_subst, 's-perc-subst')
    s_perc_trans = "%.1f" % (s_trans_single / v * 100)
    insertnum(div, s_perc_trans, 's-perc-trans')
    s_perc_orth_except_case = "%.1f" % (s_orth_except_case / v * 100)
    insertnum(div, s_perc_orth_except_case,
              's-perc-orth-except-case')

    ############
    # Subtypes #
    ############

    # Subtypes of type substantive

    s_num_num = len(tree.findall('.//t:app[@subtype="%s"]' % 'num-num', ns))
    insertnum(div, s_num_num, 's-num-num')

    s_perc_num_num = "%.1f" % (s_num_num / v * 100)
    insertnum(div, s_perc_num_num, 's-perc-num-num')

    s_missing_in_ms = len(tree.findall('.//t:app[@subtype="%s"]'
                                       % 'missing-in-ms', ns))
    insertnum(div, s_missing_in_ms, 's-missing-in-ms')

    s_perc_missing_in_ms = "%.1f" % (s_missing_in_ms / v * 100)
    insertnum(div, s_perc_missing_in_ms, 's-perc-missing-in-ms')

    s_missing_in_print = len(tree.findall('.//t:app[@subtype="%s"]'
                                          % 'missing-in-print', ns))
    insertnum(div, s_missing_in_print, 's-missing-in-print')

    s_perc_missing_in_print = "%.1f" % (s_missing_in_print / v * 100)
    insertnum(div, s_perc_missing_in_print, 's-perc-missing-in-print')

    s_fs = len(tree.findall('.//t:app[@subtype="%s"]' % 'fs', ns))
    insertnum(div, s_fs, 's-fs')

    s_perc_fs = "%.1f" % (s_fs / v * 100)
    insertnum(div, s_perc_fs, 's-perc-fs')

    # Subsubtypes of subtype orthographic

    s_y = len(tree.findall('.//t:app[@subtype="%s"]' % 'y', ns))
    insertnum(div, s_y, 's-y')

    s_perc_y = "%.1f" % (s_y / v * 100)
    insertnum(div, s_perc_y, 's-perc-y')

    s_ae = len(tree.findall('.//t:app[@subtype="%s"]' % 'ae', ns))
    insertnum(div, s_ae, 's-ae')

    s_perc_ae = "%.1f" % (s_ae / v * 100)
    insertnum(div, s_perc_ae, 's-perc-ae')

    s_h = len(tree.findall('.//t:app[@subtype="%s"]' % 'h', ns))
    insertnum(div, s_h, 's-h')

    s_perc_h = "%.1f" % (s_h / v * 100)
    insertnum(div, s_perc_h, 's-perc-h')

    s_hi_y = len(tree.findall('.//t:app[@subtype="%s"]' % 'hi-y', ns))
    insertnum(div, s_hi_y, 's-hi-y')

    s_perc_hi_y = "%.1f" % (s_hi_y / v * 100)
    insertnum(div, s_perc_hi_y, 's-perc-hi-y')

    s_num_word = len(tree.findall('.//t:app[@subtype="%s"]'
                                  % 'num-word', ns))
    insertnum(div, s_num_word, 's-num-word')

    s_perc_num_word = "%.1f" % (s_num_word / v * 100)
    insertnum(div, s_perc_num_word, 's-perc-num-word')

    # I already calculated s_case above (find 's_case' in this file)

    s_perc_case = "%.1f" % (s_case / v * 100)
    insertnum(div, s_perc_case, 's-perc-case')

    s_tc = len(tree.findall('.//t:app[@subtype="%s"]' % 'tc', ns))
    insertnum(div, s_tc, 's-tc')

    s_perc_tc = "%.1f" % (s_tc / v * 100)
    insertnum(div, s_perc_tc, 's-perc-tc')

    s_double = len(tree.findall('.//t:app[@subtype="%s"]' % 'double', ns))
    insertnum(div, s_double, 's-double')

    s_perc_double = "%.1f" % (s_double / v * 100)
    insertnum(div, s_perc_double, 's-perc-double')

    s_ph = len(tree.findall('.//t:app[@subtype="%s"]' % 'ph', ns))
    insertnum(div, s_ph, 's-ph')

    s_perc_ph = "%.1f" % (s_ph / v * 100)
    insertnum(div, s_perc_ph, 's-perc-ph')

    s_cq = len(tree.findall('.//t:app[@subtype="%s"]' % 'cq', ns))
    insertnum(div, s_cq, 's-cq')

    s_perc_cq = "%.1f" % (s_cq / v * 100)
    insertnum(div, s_perc_cq, 's-perc-cq')

    s_mpn = len(tree.findall('.//t:app[@subtype="%s"]' % 'mpn', ns))
    insertnum(div, s_mpn, 's-mpn')

    s_perc_mpn = "%.1f" % (s_mpn / v * 100)
    insertnum(div, s_perc_mpn, 's-perc-mpn')

    s_tz = len(tree.findall('.//t:app[@subtype="%s"]' % 'tz', ns))
    insertnum(div, s_tz, 's-tz')

    s_perc_tz = "%.1f" % (s_tz / v * 100)
    insertnum(div, s_perc_tz, 's-perc-tz')

    s_cz = len(tree.findall('.//t:app[@subtype="%s"]' % 'cz', ns))
    insertnum(div, s_cz, 's-cz')

    s_perc_cz = "%.1f" % (s_cz / v * 100)
    insertnum(div, s_perc_cz, 's-perc-cz')

    s_ck = len(tree.findall('.//t:app[@subtype="%s"]' % 'ck', ns))
    insertnum(div, s_ck, 's-ck')

    s_perc_ck = "%.1f" % (s_ck / v * 100)
    insertnum(div, s_perc_ck, 's-perc-ck')

    s_word_segmentation = len(tree.findall('.//t:app[@subtype="%s"]'
                                           % 'word-segmentation', ns))
    insertnum(div, s_word_segmentation, 's-word-segmentation')

    s_perc_word_segmentation = "%.1f" % (s_word_segmentation / v * 100)
    insertnum(div, s_perc_word_segmentation, 's-perc-word-segmentation')

    s_ch = len(tree.findall('.//t:app[@subtype="%s"]' % 'ch', ns))
    insertnum(div, s_ch, 's-ch')

    s_perc_ch = "%.1f" % (s_ch / v * 100)
    insertnum(div, s_perc_ch, 's-perc-ch')

    s_pb = len(tree.findall('.//t:app[@subtype="%s"]' % 'pb', ns))
    insertnum(div, s_pb, 's-pb')

    s_perc_pb = "%.1f" % (s_pb / v * 100)
    insertnum(div, s_perc_pb, 's-perc-pb')

    s_dm_mm = len(tree.findall('.//t:app[@subtype="%s"]' % 'dm-mm', ns))
    insertnum(div, s_dm_mm, 's-dm-mm')

    s_perc_dm_mm = "%.1f" % (s_dm_mm / v * 100)
    insertnum(div, s_perc_dm_mm, 's-perc-dm-mm')

    s_mn = len(tree.findall('.//t:app[@subtype="%s"]' % 'mn', ns))
    insertnum(div, s_mn, 's-mn')

    s_perc_mn = "%.1f" % (s_mn / v * 100)
    insertnum(div, s_perc_mn, 's-perc-mn')

    s_ncx = len(tree.findall('.//t:app[@subtype="%s"]' % 'ncx', ns))
    insertnum(div, s_ncx, 's-ncx')

    s_perc_ncx = "%.1f" % (s_ncx / v * 100)
    insertnum(div, s_perc_ncx, 's-perc-ncx')

    # Total of orthographic variants excluding case (OVEC)
    s_ovec = s_orth - s_case
    insertnum(div, s_ovec, 's-ovec')

    ######################################
    # @subtype identified/not identified #
    ######################################

    # @type="substantive"
    subst_elements = tree.findall(
        './/t:app[@type="substantive"]', ns)
    subst_with_subtype = [a for a in subst_elements
                          if a.get('subtype') is not None]
    s_subst_with_subtype = len(subst_with_subtype)
    insertnum(div, s_subst_with_subtype, 's-subst-with-subtype')

    # ...% on SV
    s_perc_subst_with_subtype_on_sv = "%.1f" % (
        s_subst_with_subtype / s_subst * 100)
    insertnum(div, s_perc_subst_with_subtype_on_sv,
              's-perc-subst-with-subtype-on-sv')

    # ...% on V
    s_perc_subst_with_subtype_on_v = "%.1f" % (
        s_subst_with_subtype / v * 100)
    insertnum(div, s_perc_subst_with_subtype_on_v,
              's-perc-subst-with-subtype-on-v')

    # @type="ortographic"
    orth_elements = tree.findall(
        './/t:app[@type="orthographic"]', ns)
    orth_withsubtype_except_case = [
        a for a in orth_elements
        if (a.get('subtype') is not None and
            a.get('subtype') != 'case')]
    s_orth_withsubtype_except_case = len(
        orth_withsubtype_except_case)
    insertnum(div, s_orth_withsubtype_except_case,
              's-orth-withsubtype-except-case')

    # ...% on OVEC
    s_perc_orth_withsubtype_except_case_on_ovec = "%.1f" % (
        s_orth_withsubtype_except_case / s_ovec * 100)
    insertnum(div, s_perc_orth_withsubtype_except_case_on_ovec,
              's-perc-orth-withsubtype-except-case-on-ovec')

    # ...% on V
    s_perc_orth_withsubtype_except_case_on_v = "%.1f" % (
        s_orth_withsubtype_except_case / v * 100)
    insertnum(div, s_perc_orth_withsubtype_except_case_on_v,
              's-perc-orth-withsubtype-except-case-on-v')

    # Total @subtypes for subst and orth, except "case"
    s_found_subtypes = s_subst_with_subtype + \
        s_orth_withsubtype_except_case
    insertnum(div, s_found_subtypes, 's-found-subtypes')

    # ...% on V
    s_perc_found_subtypes = "%.1f" % (
        s_found_subtypes / v * 100)
    insertnum(div, s_perc_found_subtypes, 's-perc-found-subtypes')

    #####################
    # Textual decisions #
    #####################

    s_two_children = s_three_children = 0
    s_lem_print = s_lem_not_print = 0
    s_apps_with_o = s_lems_only_o = 0

    # Actual variant elements (avel)
    bad_types = ['punctuation', 'gap-in-ms', 'illegible-in-ms',
                 'transposition']
    avel = [a for a in apps
            if a.get('type') not in bad_types and
            (a.get('type') != 'orthography' and a.get('subtype') != 'case')]
    # Only add every second transposition (transpositions come in pairs)
    transpositions = tree.findall('.//t:app[@type="transposition"]', ns)
    for t in transpositions:
        i = transpositions.index(t)  # Index
        if (i % 2) == 0:  # Only even numbers
            avel.append(t)

    for a in avel:

        # 2 or 3 children of <app>
        if len(a) == 2:
            s_two_children += 1
        elif len(a) == 3:
            s_three_children += 1

        lem = a.find('.//t:lem', ns)
        # When there are 3 children, this will only find the 1st rdg
        rdg = a.find('.//t:rdg', ns)

        lem_wit = lem.get('wit')
        rdg_wit = rdg.get('wit')

        # <app>s in which MS O is involved
        if (lem_wit is not None and
                ('#o' in lem_wit or '#o' in rdg_wit)):
            s_apps_with_o += 1

        # <lem> is print reading
        if (lem_wit is not None and
                ('#g' in lem_wit or '#b' in lem_wit)):
            s_lem_print += 1
        # <lem> is not print reading, but MS reading
        else:
            s_lem_not_print += 1

    # 2 children in <app>
    insertnum(div, s_two_children, 's-two-children')
    s_perc_two_children = "%.1f" % (
        s_two_children / v * 100)
    insertnum(div, s_perc_two_children, 's-perc-two-children')

    # 3 children in <app>
    insertnum(div, s_three_children, 's-three-children')
    s_perc_three_children = "%.1f" % (
        s_three_children / v * 100)
    insertnum(div, s_perc_three_children, 's-perc-three-children')

    # print/non-print <lem>s
    insertnum(div, s_lem_print, 's-lem-print')
    insertnum(div, s_lem_not_print, 's-lem-not-print')

    # ...and % on V

    s_perc_lem_print = "%.1f" % (
        s_lem_print / v * 100)
    insertnum(div, s_perc_lem_print, 's-perc-lem-print')

    s_perc_lem_not_print = "%.1f" % (
        s_lem_not_print / v * 100)
    insertnum(div, s_perc_lem_not_print, 's-perc-lem-not-print')

    # <app>s including #o somewhere
    insertnum(div, s_apps_with_o, 's-apps-with-o')

    # <app>s in which only MS O provides the 'correct' reading
    lems_only_o = tree.findall('.//t:lem[@wit="#o"]', ns)
    s_lems_only_o = len(lems_only_o)
    insertnum(div, s_lems_only_o, 's-lems-only-o')

    # ...% on all <app>s including #o somewhere
    s_perc_lems_only_o = "%.1f" % (
        s_lems_only_o / s_apps_with_o * 100)
    insertnum(div, s_perc_lems_only_o,
              's-perc-lems-only-o')

    ######################
    # General statistics #
    ######################

    if not include_general:
        # Remove the <div> (child of <div="statistics"> for
        # general statistics from the template file
        gener_subdiv = div.find('.//t:div[@n="general-statistics"]', ns)
        gener_subdiv.getparent().remove(gener_subdiv)

    else:

        all_words = rdg_words = lem_words = []

        pars = tree.findall('.//t:p', ns)
        for p in pars:
            p_text = text_strip_punct(p)
            p_words = p_text.split()  # A list
            for word in p_words:
                all_words.append(word)

        # s_all_words = count_words_in_tagname(tree, 'p')
        s_all_words = len(all_words)

        # Find words in <lem>
        lems = tree.findall('.//t:lem', ns)
        for l in lems:
            l_text = text_strip_punct(l)
            l_words = l_text.split()  # A list
            for word in l_words:
                l_words.append(word)

        # s_lem_words = count_words_in_tagname(tree, 'lem')
        s_lem_words = len(lem_words)

        # Remove words in <rdg> elements from total count
        rdgs = tree.findall('.//t:rdg', ns)
        for r in rdgs:
            r_text = text_strip_punct(r)
            r_words = r_text.split()  # A list
            for word in r_words:
                rdg_words.append(word)

        # s_rdg_words = count_words_in_tagname(tree, 'rdg')
        s_rdg_words = len(rdg_words)

        # Correct the reduplication
        s_all_words_corr = s_all_words - s_rdg_words

        s_perc_lem_words = "%.1f" % (
            s_lem_words / s_all_words_corr * 100)

        if True:
            print(('All words: {}\nIn <lem>: {}\n'
                   'In <rdg>: {}\nWords-lem: {}\n').format(
                       s_all_words, s_lem_words,
                       s_rdg_words, s_all_words_corr))

        insertnum(div, s_all_words_corr, 's-all-words-corr')
        insertnum(div, s_perc_lem_words, 's-lem-words')
        insertnum(div, s_perc_lem_words, 's-perc-lem-words')

    ##############################################
    # Write tree to output file stats_filled.xml #
    # (warning: I'm overwriting the file)        #
    ##############################################

    filled_tree.write(filled_path,
                      encoding='UTF-8', method='xml',
                      pretty_print=True, xml_declaration=True)


def import_statistics():

    # Parse stats_filled.xml
    filled_tree = etree.parse('%s%s' % (xmlpath, stats_filled))
    filled_div = filled_tree.find('.//t:div[@n="statistics"]', ns)

    # Parse chronicon.xml
    chronicon_path = '%s%s' % (xmlpath, chronicon_output_file)
    chronicon_tree = etree.parse('%s%s' % (xmlpath, chronicon_path))
    out_div = chronicon_tree.find('.//t:div[@n="statistics"]', ns)
    out_div.text = '\n\n'

    for child in filled_div:
        out_div.append(child)

    # Write tree to output file template.xml
    # (warning: I'm overwriting the file)
    chronicon_tree.write(chronicon_path,
                         encoding='UTF-8', method='xml',
                         pretty_print=True, xml_declaration=True)
