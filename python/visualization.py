#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import os

from lint import tosLint
from output import writeToMultiMSTableFile
from detect_combinations import detectCommonAbbrCombinations

os.system('clear')

mss = ['a', 'b', 'c']     # The sigla of the three manuscripts

for x in mss:
    tosLint(x)

for mscombi in [['a', 'b', 'c'],
                ['a', 'b'],
                ['a', 'c'],
                ['b', 'c'],
                ['a'],
                ['b'],
                ['c']]:
    for layercombi in [['gl'],     ['al'],     ['gl', 'al']]:
        writeToMultiMSTableFile(mscombi, layercombi, wbaretext=False)

for m in mss:
    # Choose False if you want a full report of all <abbr>s:
    detectCommonAbbrCombinations(m, quiet=False)
