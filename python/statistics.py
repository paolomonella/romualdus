#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' This module makes textual statistics,
    then appends them to the <front> of chronicon.xml'''

# import my_database_import
# import variant_subtype
# import operator
from lxml import etree
from myconst import ns, xmlpath, chronicon_output_file
from myconst import stats_template, stats_filled


def insertnum(ancestor, number, n):
    ''' Insert the number provided in the 2nd argument
        as text of the <num> with @n whose value is provided in the
        'n' argument, and as value of its @value attribute.
        Example: if it's
        insert(tree, 4, 's-subst')
        then change <num n="s-subst"/> to <num n="s-subst">4</seg> '''

    e = ancestor.find('.//t:num[@n="%s"]' % n, ns)
    number_str = str(number)
    e.text = number_str
    e.set('value', number_str)


def recalculate_statistics():

    # Parse stats_template file and find div
    template_path = '%s%s' % (xmlpath, stats_template)
    template_tree = etree.parse(template_path)
    div = template_tree.find('.//t:div[@n="statistics"]', ns)
    print(div)

    # Parse stats_filled file
    filled_path = '%s%s' % (xmlpath, stats_filled)
    filled_tree = etree.parse(filled_path)
    old_filled_div = filled_tree.find('.//t:div[@n="statistics"]', ns)
    old_filled_div.getparent().remove(old_filled_div)
    filled_root = filled_tree.getroot()

    '''
    # Empty <div> of stats_filled
    for child in div:
        div.getparent().remove(div)
    # Move contents of template <div>
    # into <div> of stats_filled
    for child in template_div:
        div.append(child)
        '''
    filled_root.append(div)

    # Import chronicon.xml
    chronicon_path = '%s%s' % (xmlpath, chronicon_output_file)
    tree = etree.parse('%s%s' % (xmlpath, chronicon_path))

    # Total of <app> elements
    number = len(tree.findall('.//t:app', ns))
    insertnum(div, number, 's-app')

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
    v = v + s_orth

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
    s_perc_orth = "%.1f" % (s_orth / v * 100)
    insertnum(div, s_perc_orth, 's-perc-orth')

    ############
    # Subtypes #
    ############

    # Subtypes of type substantive

    s_num_num = len(tree.findall('.//t:app[@subtype="%s"]' % 'num-num', ns))
    print(s_num_num)
    insertnum(div, s_num_num, 's-num-num')

    s_perc_num_num = "%.1f" % (s_num_num / v * 100)
    insertnum(div, s_perc_num_num, 's-perc-num-num')

    s_missing_in_ms = len(tree.findall('.//t:app[@subtype="%s"]'
                                       % 'missing-in-ms', ns))
    insertnum(div, s_missing_in_ms, 's-missing-in-ms')

    '''
    s_perc_missing_in_ms
    's-perc-missing-in-ms'

    s_missing_in_print = len(tree.findall('.//t:app[@subtype="%s"]'
        % 's-missing-in-print', ns))
    insertnum(div, s_missing_in_print, 's-missing-in-print')

    s_perc_missing_in_print
    's-perc-missing-in-print'

    s_fs = len(tree.findall('.//t:app[@subtype="%s"]' % 's-fs', ns))
    insertnum(div, s_fs, 's-fs')

    s_perc_fs
    's-perc-fs'

    # Subsubtypes of subtype orthographic

    s_y = len(tree.findall('.//t:app[@subtype="%s"]' % 's-y', ns))
    insertnum(div, s_y, 's-y')

    s_perc_y
    's-perc-y'

    s_v = len(tree.findall('.//t:app[@subtype="%s"]' % 's-v', ns))
    insertnum(div, s_v, 's-v')

    s_perc_v
    's-perc-v'

    s_j = len(tree.findall('.//t:app[@subtype="%s"]' % 's-j', ns))
    insertnum(div, s_j, 's-j')

    s_perc_j
    's-perc-j'

    s_ae = len(tree.findall('.//t:app[@subtype="%s"]' % 's-ae', ns))
    insertnum(div, s_ae, 's-ae')

    s_perc_ae
    's-perc-ae'

    s_h = len(tree.findall('.//t:app[@subtype="%s"]' % 's-h', ns))
    insertnum(div, s_h, 's-h')

    s_perc_h
    's-perc-h'

    s_n_pn = len(tree.findall('.//t:app[@subtype="%s"]' % 's-n-pn', ns))
    insertnum(div, s_n, 's-n-pn')

    s_perc_n_pn
    's-perc-n-pn'

    s_hi_y = len(tree.findall('.//t:app[@subtype="%s"]' % 's-hi-y', ns))
    insertnum(div, s_hi_y, 's-hi-y')

    s_perc_hi-y
    's-perc-hi-y'

    s_num-word = len(tree.findall('.//t:app[@subtype="%s"]'
    % 's-num-word', ns))
    insertnum(div, s_num, 's-num-word')

    s_perc_num-word
    's-perc-num-word'

    s_case = len(tree.findall('.//t:app[@subtype="%s"]' % 's-case', ns))
    insertnum(div, s_case, 's-case')

    s_perc_case
    's-perc-case'

    s_tc = len(tree.findall('.//t:app[@subtype="%s"]' % 's-tc', ns))
    insertnum(div, s_tc, 's-tc')

    s_perc_tc
    's-perc-tc'

    s_double = len(tree.findall('.//t:app[@subtype="%s"]' % 's-double', ns))
    insertnum(div, s_double, 's-double')

    s_perc_double
    's-perc-double'

    s_ph = len(tree.findall('.//t:app[@subtype="%s"]' % 's-ph', ns))
    insertnum(div, s_ph, 's-ph')

    s_perc_ph
    's-perc-ph'

    s_cq = len(tree.findall('.//t:app[@subtype="%s"]' % 's-cq', ns))
    insertnum(div, s_cq, 's-cq')

    s_perc_cq
    's-perc-cq'

    s_mpn = len(tree.findall('.//t:app[@subtype="%s"]' % 's-mpn', ns))
    insertnum(div, s_mpn, 's-mpn')

    s_perc_mpn
    's-perc-mpn'

    s_tz = len(tree.findall('.//t:app[@subtype="%s"]' % 's-tz', ns))
    insertnum(div, s_tz, 's-tz')

    s_perc_tz
    's-perc-tz'

    s_cz = len(tree.findall('.//t:app[@subtype="%s"]' % 's-cz', ns))
    insertnum(div, s_cz, 's-cz')

    s_perc_cz
    's-perc-cz'

    s_ck = len(tree.findall('.//t:app[@subtype="%s"]' % 's-ck', ns))
    insertnum(div, s_ck, 's-ck')

    s_perc_ck
    's-perc-ck'

    s_word-segmentation = len(tree.findall('.//t:app[@subtype="%s"]'
        % 's-word-segmentation', ns))
    insertnum(div, s_word, 's-word-segmentation')

    s_perc_word-segmentation
    's-perc-word-segmentation'

    s_ch = len(tree.findall('.//t:app[@subtype="%s"]' % 's-ch', ns))
    insertnum(div, s_ch, 's-ch')

    s_perc_ch
    's-perc-ch'

    s_pb = len(tree.findall('.//t:app[@subtype="%s"]' % 's-pb', ns))
    insertnum(div, s_pb, 's-pb')

    s_perc_pb
    's-perc-pb'

    s_dm-mm = len(tree.findall('.//t:app[@subtype="%s"]' % 's-dm-mm', ns))
    insertnum(div, s_dm, 's-dm-mm')

    s_perc_dm-mm
    's-perc-dm-mm'

    s_mn = len(tree.findall('.//t:app[@subtype="%s"]' % 's-mn', ns))
    insertnum(div, s_mn, 's-mn')

    s_perc_mn
    's-perc-mn'

    s_ncx = len(tree.findall('.//t:app[@subtype="%s"]' % 's-ncx', ns))
    insertnum(div, s_ncx, 's-ncx')

    s_perc_ncx
    's-perc-ncx'
    '''

    # Write tree to output file stats_filled.xml
    # (warning: I'm overwriting the file)
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
