#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import os

from lint import tosLint 
from output import writeToMultiMSTableFile
from detect_combinations import detectCommonAbbrCombinations

os.system('clear')

mss = ['a', 'b', 'c']     # The sigla of the three manuscripts (in the future, it might include 'd' or others)

for x in mss:
    tosLint(x)

for mscombi in [  ['a', 'b', 'c'],  ['a', 'b'],  ['a', 'c'],  ['b', 'c'],  ['a'],  ['b'],  ['c'] ]:
    for layercombi in [     ['gl'],     ['al'],     ['gl', 'al']    ]:
        writeToMultiMSTableFile(mscombi, layercombi, wbaretext=False)

for m in mss:
    detectCommonAbbrCombinations(m, quiet=False) # Choose False if you want a full report of all <abbr>s
