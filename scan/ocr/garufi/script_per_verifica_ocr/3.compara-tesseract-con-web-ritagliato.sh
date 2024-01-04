#!/bin/bash
# Fai il lavoro sporco di rinomina e spostamento file per i miei OCR di Garufi
#: ${1?"Attenzione: $0 numero_di_pagina"}
echo "Tesseract vs. Web ritagliato"
#: ${1?"Inserisci il numero di pagina"}
garufipage=$(<page)
#vim -d g$1t.txt g$1w-rit.txt
vim -d g${garufipage}t.txt g${garufipage}w-rit.txt
