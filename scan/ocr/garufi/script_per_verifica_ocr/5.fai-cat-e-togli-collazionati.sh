#!/bin/bash
# Fai il lavoro sporco di rinomina e spostamento file per i miei OCR di Garufi
#: ${1?"Attenzione: $0 numero_di_pagina"}
#: ${1?"Inserisci il numero di pagina"}
garufipage=$(<page)
cp      ocr_garufi_solo_testo_da_pag_21_alla_fine.txt      backup_ocr_garufi_solo_testo_da_pag_21_alla_fine.txt
#cat g$1t.txt >> ocr_garufi_solo_testo_da_pag_21_alla_fine.txt
cat g${garufipage}t.txt >> ocr_garufi_solo_testo_da_pag_21_alla_fine.txt
#mv g$1* ripostiglio/
mv g$garufipage* ripostiglio/
echo "Ora, con lo script n. 6, controlla che la pagina $(<page) sia stata correttamente inserita nel file OCR complessivo"
