#!/bin/bash
# Fai il lavoro sporco di rinomina e spostamento file per i miei OCR di Bonetti
#: ${1?"Attenzione: $0 numero_di_pagina"}
: ${1?"Inserisci il numero di pagina"}
mv ../Molinari_OCR_da_bonetti/B$1.txt ../Molinari_OCR_da_bonetti/V$1.txt
mv b$1.txt miei_ocr_bonetti_collazionati_con_molinari/
