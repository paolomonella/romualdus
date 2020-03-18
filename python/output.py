#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

from lxml import etree

from myconst import htmlpath
from myconst import ns, xml_ns, html_ns
from layers import extractLayers


def newHTMLTree():
    ''' Create a new HTML tree '''

    mynsmap = {None: ns['h']}  # the default namespace (no prefix)
    hroot = etree.Element(html_ns + 'html', nsmap=mynsmap)
    hroot.set(xml_ns + 'lang', 'en')

    # HTML <head> shared by GL and AL
    hhead = etree.SubElement(hroot, 'head')

    # Tweak HTML Header
    csslink = etree.SubElement(hhead, 'link')
    csslink.set('rel', 'stylesheet')
    csslink.set('type', 'text/css')
    csslink.set('href', '../stylesheet.css')
    meta = etree.SubElement(hhead, 'meta')
    meta.set('http-equiv', 'Content-Type')
    meta.set('content', 'text/html; charset=utf-8')

    # HTML <body> shared by GL and AL
    # This is the brand new HTML <body>
    hbody = etree.SubElement(hroot, 'body')

    # Create tree
    htree = etree.ElementTree(hroot)

    return htree


def writeToMultiMSTableFile(mymss, myl, wbaretext=False):
    ''' Output GL and AL of all manuscripts to one HTML file with an alignment
        <table> with a cell for each <p>.
        mymss is a list with the sigla of the MSS to include
        myl is a list with the layer(s) to include
        (it can be ['al'], ['al', 'gl'] or ['gl']).
        The order does not matter'''

    gall = {}
    aall = {}

    for ms in mymss:
        if 'gl' in myl:
            # <div id="GLdiv">:
            gall[ms] = extractLayers(ms, baretext=wbaretext)[0]
            # <div id="aGLdiv"> (bGLdiv, cGLdiv):
            gall[ms].set('id', ms + gall[ms].get('id'))
        if 'al' in myl:
            # <div id="ALdiv">:
            aall[ms] = extractLayers(ms, baretext=wbaretext)[1]
            # <div id="aALdiv"> (bALdiv, cALdiv)
            aall[ms].set('id', ms + aall[ms].get('id'))
            ''' Result: gall = {'a': element_<div id="aGLdiv">,
                                'b': element_<div id="bGLdiv"> etc.}
                        aall = {'a': element_<div id="aALdiv">,
                                'b': element_<div id="bALdiv"> etc.}
                        aall['a']
                            will be element_<div id="aALdiv"> etc.
            '''

    tabhtree = newHTMLTree()

    # Check IDs
    msids = {}
    # For each MS, create a list of GL <p> IDs and one of AL <p> IDs,
    # and check that the two lists are identical:
    for ms in mymss:
        if 'gl' in myl:
            gids = []   # Create list of <p> IDs for GL (gids: Graphematic IDs)
            for p in gall[ms].findall('.//h:p', ns):
                gids.append(p.get('id'))
                # Change <p> ID g3.7-3.16 to b-graph-g3.7-3.16
                # to avoid duplicate IDs):
                p.set('id', '%s-graph-%s' % (ms, p.get('id')))
        if 'al' in myl:
            aids = []   # Create list of <p> IDs for AL (aids: Alphabetic IDs)
            for p in aall[ms].findall('.//h:p', ns):
                aids.append(p.get('id'))
                # Change <p> ID g3.7-3.16 to b-alpha-g3.7-3.16
                # to avoid duplicate IDs):
                p.set('id', '%s-alpha-%s' % (ms, p.get('id')))
        # If I'm processing both GL and AL,
        # check that the two lists are identical:
        if len(myl) > 1:
            if gids != aids:
                print('BEWARE! The list of IDs for paragraphs in the GL \
                      and in the AL are not identical')
                print()
        if 'gl' in myl:
            ''' I'm creating a new variable (ManuScript IDs) just to avoid
            confusion due to the variable name.
            msids['a'] (or msids['b'], etc.)
            will be a list with all IDs of manuscript 'a' (or 'b',
            etc.)'''
            msids[ms] = gids
        else:
            msids[ms] = aids
    # This will be the final list of paragraph IDs (it's the list of
    # the first manuscript in mymss):
    ids = msids[mymss[0]]
    # Check that the lists of IDs are identical for all manuscripts:
    for ms in mymss:
        if msids[ms] != ids:
            print('Beware! The list of paragraph IDs of manuscript %s \
                  does not coincide with that of manuscript A' % ms.upper())
            # If I'll ever receive this warning,
            # I'll write further code to find what ID does not coincide

    # Create table
    tabbody = tabhtree.find('.//body')
    syntab = etree.SubElement(tabbody, 'table')
    syntab.set('id', 'syntab')

    # Table header row
    tabhrow = etree.SubElement(syntab, 'tr')
    tabhrow.set('id', 'row-header')  # Result: <tr id="row-header">
    thll = []       # Table Header Layer List of lists
    if 'gl' in myl:
        thll. append(['gcell', 'Graphematic Layer'])
    if 'al' in myl:
        thll.append(['acell', 'Alphabetic Layer'])
    for ms in mymss:
        for thl in thll:
            # Add table header cell:
            tabhcell = etree.SubElement(tabhrow, 'th')
            # Result of next line:: first <td class="msb gcell">,
            # then <td class="msb acell">:
            tabhcell.set('class', 'ms%s %s' % (ms, thl[0]))
            if ms.lower() == 'a'.lower():
                msNameForTableHeader = 'a'
            else:
                msNameForTableHeader = ms
            #tabhcell.text = 'MS %s' % ms.upper()
            tabhcell.text = 'MS %s' % msNameForTableHeader.upper()
            # Add a line break:
            tabhcellbr = etree.SubElement(tabhcell, 'br')
            tabhcellbr.tail = thl[1]

    # Populate the table
    for pid in ids:     # Iterate over the ID list (pid= paragraph ID)

        # Add new row to the HTML table:
        tabrow = etree.SubElement(syntab, 'tr')
        # Result of next line: <tr id="row-g3.7-3.16">
        tabrow.set('id', 'row-' + pid)

        for ms in mymss:  # Add a <td> for each <p> in each MS for each layer

            if 'gl' in myl:  # Create <td>s for Graphemic Layer
                # gp: GL paragraph
                gp = gall[ms].find('.//h:p[@id="%s-graph-%s"]' % (ms, pid), ns)
                # If the <p> is encoded at the AL only: <p decls="#al">:
                if 'decls' in gp.attrib and gp.get('decls') == '#al':
                    for c in gp:
                        if c.tag == 'span' \
                           and c.get('class') == 'metatext garufi':
                            # Store <span class="metatext garufi">[Garufi 3,2 -
                            # 3,6] </span>:
                            garufiAlOnlySpan = c
                        # Remove all other elements children of <p>:
                        gp.remove(c)
                        garufiAlOnlySpan.tail = \
                            'Encoded at the Alphabetic Layer only'
                        gp.append(garufiAlOnlySpan)
                tabgcell = etree.SubElement(tabrow, 'td')   # Add GL cell
                # Result: <td class="gcell">
                tabgcell.set('class', 'ms%s gcell' % ms)
                # Result: <td class="gcell"><p id="graph-g3.7-3.16">
                # It's not classy to nest a <p> within a <td> but well...
                tabgcell.append(gp)

            if 'al' in myl:  # Create <td>s for Alphabetic Layer
                # ap: AL paragraph (corresponding to gp)
                ap = aall[ms].find('.//h:p[@id="%s-alpha-%s"]' % (ms, pid), ns)
                tabacell = etree.SubElement(tabrow, 'td')   # Add AL cell
                # Result of next line: <td class="acell">:
                tabacell.set('class', 'ms%s acell' % ms)
                # Result of next line:
                # <td class="acell"><p id="alpha-g3.7-3.16">
                tabacell.append(ap)

    htmlfilename = '%stab-ms_%s--layers_%s.html' % (htmlpath,
                                           '_'.join(mymss), '_'.join(myl))
    tabhtree.write(htmlfilename, encoding='UTF-8', method='html',
                   pretty_print=True, xml_declaration=True)
