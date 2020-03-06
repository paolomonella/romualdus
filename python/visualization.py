#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import os

from lint import tosLint
from output import writeToMultiMSTableFile
from detect_combinations import detectCommonAbbrCombinations

os.system('clear')

mss = ['a-1and2unified', 'b', 'c']     # The sigla of the three manuscripts

for x in mss:
    tosLint(x)

for mscombi in [['a-1and2unified', 'b', 'c'],
                ['a-1and2unified', 'b'],
                ['a-1and2unified', 'c'],
                ['b', 'c'],
                ['a-1and2unified'],
                ['b'],
                ['c']]:
    for layercombi in [['gl'],     ['al'],     ['gl', 'al']]:
        writeToMultiMSTableFile(mscombi, layercombi, wbaretext=False)

for m in mss:
    # Choose False if you want a full report of all <abbr>s:
    detectCommonAbbrCombinations(m, quiet=False)
