#!/bin/bash
# Fai il lavoro sporco di rinomina e spostamento file per i miei OCR di Bonetti
#: ${1?"Attenzione: $0 numero_di_pagina"}
: ${1?"Inserisci il numero di pagina"}
vim -d b$1j-b.txt b$1j-r.txt b$1t-b.txt b$1t-r.txt
