#!/usr/bin/python
# -*- coding: utf-8 -*-

def writeTo2HTMLFiles (siglum, wbaretext=False):
    ''' Output GL and AL to two independent HTML files.
        It only takes the MS siglum as argument. '''

    gall = extractLayers (siglum, baretext=wbaretext)[0] # <div id="GLdiv"> (containing the GL HTML output as a number of HTML <p>s)
    aall = extractLayers (siglum, baretext=wbaretext)[1] # <div id="ALdiv"> (containing the AL HTML output as a number of HTML <p>s)

    # Output GL to independent HTML file
    ghtree = newHTMLTree()
    ghtree.find('.//body').append(gall) # Append <div xml:id="GLdiv"> (gall) to HTML <body>
    # Serialize HTML
    ghtree.write('%s-gl.html' % siglum, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)
    
    # Output AL to independent HTML file
    ahtree = newHTMLTree()
    ahtree.find('.//body').append(aall) # Append XML body (aall) to HTML <body> as <div xml:id="AL"> 
    # Serialize HTML
    ahtree.write('%s-al.html' % siglum, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)


def writeToCSS2colFile (siglum):
    ''' Output GL and AL to one HTML file with a two CSS-created columns (css2col) '''

    gall = extractLayers (siglum)[0] # <div id="GLdiv"> (containing the GL HTML output as a number of HTML <p> elements)
    aall = extractLayers (siglum)[1] # <div id="ALdiv"> (containing the AL HTML output as a number of HTML <p> elements)

    css2coltree = newHTMLTree()

    # Append XML body (gall) to HTML <body> as <div xml:id="GLdiv-css2col"> 
    css2coltree.find('.//body').append(gall)
    css2coltree.find('.//h:div[@id="GLdiv"]', ns).set('id', 'GLdiv-css2col')
    # Append XML body (aall) to HTML <body> as <div xml:id="ALdiv-css2col"> 
    css2coltree.find('.//body').append(aall)
    css2coltree.find('.//h:div[@id="ALdiv"]', ns).set('id', 'ALdiv-css2col')
    # Serialize HTML
    css2coltree.write('%s-css2col.html' % siglum, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)


def writeToOneMSTableFile (siglum, wbaretext=False):
    ''' Output GL and AL of the manuscript with siglum "siglum"
    to one HTML file with an alignment <table> with a cell for each <p> '''

    gall = extractLayers (siglum, baretext=wbaretext)[0] # <div id="GLdiv"> (containing the GL HTML output as a number of HTML <p>s)
    aall = extractLayers (siglum, baretext=wbaretext)[1] # <div id="ALdiv"> (containing the AL HTML output as a number of HTML <p>s)

    tabhtree = newHTMLTree()

    # Create table
    tabbody = tabhtree.find('.//body')
    syntab = etree.SubElement(tabbody, 'table')
    syntab.set('id', 'syntab')
    gids = []   # Create list of <p> IDs for GL (gids: Graphematic IDs)
    for p in gall.findall('.//h:p', ns):
        gids.append(p.get('id'))
        p.set('id', 'graph-%s' % p.get('id'))  # Change ID g3.7-3.16 to graph-g3.7-3.16 to avoid duplicate IDs)
    aids = []   # Create list of <p> IDs for AL (aids: Alphabetic IDs)
    for p in aall.findall('.//h:p', ns):
        aids.append(p.get('id'))
        p.set('id', 'alpha-%s' % p.get('id'))  # Change ID g3.7-3.16 to alpha-g3.7-3.16 to avoid duplicate IDs)
    # Check that the two lists are identical
    if gids != aids:
        print('Beware! The list of IDs for paragraphs in the GL and in the AL are not identical')
    else:
        ids = gids  # I'm creating a new variable just to avoid confusion due to the variable name
    for pid in ids:     # Iterate over the ID list (pid= paragraph ID)
        gp = gall.find('.//h:p[@id="graph-%s"]' % pid,  ns)    # gp: GL paragraph
        ap = aall.find('.//h:p[@id="alpha-%s"]' % pid, ns)    # ap: AL paragraph (corresponding to gp)
        # Add new row to the HTML table 
        tabrow = etree.SubElement(syntab, 'tr')
        tabrow.set('id', 'row-' + pid) # Result: <tr id="row-g3.7-3.16">
        # Add GL cell
        tabgcell = etree.SubElement(tabrow, 'td')   # Add GL cell
        tabgcell.set('class', 'gcell') # Result: <td class="gcell">
        tabgcell.append(gp) # Result: <td class="gcell"><p id="graph-g3.7-3.16">
                            # It's not classy to nest a <p> within a <td> but well...
        tabacell = etree.SubElement(tabrow, 'td')   # Add AL cell
        tabacell.set('class', 'acell')              # Result: <td class="acell">
        tabacell.append(ap) # Result: <td class="acell"><p id="alpha-g3.7-3.16">
    tabhtree.write('%s.html' % siglum, encoding='UTF-8', method='xml', pretty_print=True, xml_declaration=True)
