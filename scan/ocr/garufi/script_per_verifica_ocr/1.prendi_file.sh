#!/bin/bash
# Fai il lavoro sporco di rinomina e spostamento file per i miei OCR di Garufi
#: ${1?"Attenzione: $0 numero_di_pagina"}

: ${1?"Inserisci il numero di pagina"}
echo $1 > page
echo "Prendo i file da collazionare"
cp -v A[1-4]*/g$1* .
python3.6 sostituzioni.py
