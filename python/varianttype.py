#!/usr/bin/python3.6
# -*- coding: utf-8 -*-



from lxml import etree
from myconst import ns
#from collateRomualdus import getVariantType, compareStrings
from collateRomualdus import compareStrings
from collateRomualdus import numeralCheck

verbose = False

xmlfile="../xml/m.xml";
tree = etree.parse(xmlfile);
apps = tree.findall('.//t:app', ns)

# Create and populate 'comparisons', a list of dictionaries (one dict for each <app> in the TEI XML file)
comparisons = []    
for app in apps:
    greading = app.find('.//t:*[@wit="#g"]', ns)
    areading = app.find('.//t:*[@wit="#a"]', ns)
    if greading.text is not None:
        gtext = greading.text
    else:
        gtext = ''
    if areading.text is not None:
        atext = areading.text
    else:
        atext = ''
    if verbose:
        print('\n\ngtext: «%s»' % (gtext))
        print('atext: «%s»' % (atext))

    myComp = compareStrings(gtext, atext)   # A dictionary. Note that the first one is the Garufi text; the second is MS A text
    myComp['app'] = app
    myComp['greading'] = greading
    myComp['areading'] = areading
    myComp['gtext'] = gtext
    myComp['atext'] = atext
    comparisons.append(myComp)

# Count types of variants
typed = []
untyped = []
countedType = []
for c in comparisons:
    if c['type'] != 'unknown':
        typed.append(c)
    else:
        untyped.append(c)
        if verbose:
            print('\n')
            for k in c:
                print('%s: «%s»' % (k, c[k]))

    if c['type'] == 'differentPunctType':
        countedType.append(c)


print('typed:', len(typed))
print('untyped:', len(untyped))
print('countedType:', len(countedType))
