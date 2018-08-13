#!/bin/bash
# Fai il lavoro sporco di rinomina e spostamento file per i miei OCR di Garufi
#: ${1?"Attenzione: $0 numero_di_pagina"}

#: ${1?"Inserisci il numero di pagina"}
echo "Tesseract vs. Tesseract non ritagliato"
garufipage=$(<page)
#vim -d g$1t.txt g$1t-rit.txt
vim -d g${garufipage}t.txt g${garufipage}t-rit.txt
