#!/bin/bash
# Fai il lavoro sporco di rinomina e spostamento file per i miei OCR di Bonetti
#: ${1?"Attenzione: $0 numero_di_pagina"}
: ${1?"Inserisci il numero di pagina"}
cp b$1j-b.txt b$1.txt
mv b$1j-b.txt b$1j-r.txt b$1t-b.txt b$1t-r.txt miei_ocr_bonetti_collazionati_tra_di_loro/
vim -d ../Molinari_OCR_da_bonetti/B$1.txt b$1.txt
