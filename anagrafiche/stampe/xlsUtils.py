#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import date

from anagrafiche.models import CONTATTO_TEL_UFFICIO, CONTATTO_FAX, \
    CONTATTO_EMAIL, SEDE_AMMINISTRATIVA, SEDE_LEGALE, Entita

GRAY_10 = 'E6E6E6'
SALMONE = 'FDEADA'

DATA_CAMBIO_RAGIONE_SOCIALE = date(2016, 11, 17)
RAGIONE_SOCIALE_NUOVA = Entita.objects.proprietario().ragione_sociale if Entita.objects.proprietario_exists() \
    else "MR FERRO S.R.L."
RAGIONE_SOCIALE_VECCHIA = 'MR Ferro S.A.S. di Ruggeri Claudio & C.'


def crea_stili(workbook):
    """
    Funzione helper per creare e riutilizzare gli stili in documenti diversi.
    """

    # I bordi possono assumere i seguenti valori:
    # 1 - bordo normale
    # 2 - bordo un po' più spesso
    # 7 - bordo molto spesso

    stili = {}

    stili['c8'] = workbook.add_format({
        'font_size': 8
    })
    stili['small'] = workbook.add_format({
        'font_size': 9
    })
    stili['10'] = workbook.add_format({
        'font_size': 10
    })
    stili['wrap-10'] = workbook.add_format({
        'text_wrap': 1,
        'valign': 'top',
        'font_size': 10,
    })
    stili['medium_sinistra'] = workbook.add_format({
        'font_size': 20,
        'bold': 1,
        'align': 'left',
    })
    stili['big'] = workbook.add_format({
        'font_size': 28,
        'bold': 1,
        'align': 'center',
    })
    stili['bold-centrato'] = workbook.add_format({
        'bold': 1,
        'align': 'center'
    })
    stili['bold-centrato-bg_pink'] = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'font_size': 20,
        'fg_color': SALMONE
    })
    stili['bold-centrato-bg_pink-data'] = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'fg_color': SALMONE,
        'font_size': 20,
        'num_format': 'dd/mm/yyyy'
    })
    stili['bold-centrato-bg_gray'] = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'border': 7,
        'fg_color': GRAY_10,
        'text_wrap': 1
    })
    stili['bold-centrato-bg_gray_small'] = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'border': 7,
        'fg_color': GRAY_10,
        'text_wrap': 1,
        'font_size': 9
    })
    stili['bold-centrato-bg_gray-10'] = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'border': 7,
        'fg_color': GRAY_10,
        'text_wrap': 1,
        'font_size': 10
    })
    stili['boxed-bold'] = workbook.add_format({
        'bold': True,
        'border': 7
    })
    stili['bold'] = workbook.add_format({
        'bold': True
    })
    stili['bold_small'] = workbook.add_format({
        'bold': True,
        'font_size': 9
    })
    stili['bold-10'] = workbook.add_format({
        'bold': True,
        'font_size': 10
    })
    stili['bold-15'] = workbook.add_format({
        'font_size': 15,
        'bold': 1
    })
    stili['italic'] = workbook.add_format({'italic': True})
    stili['italic-bg_gray'] = workbook.add_format({
        'italic': True,
        'border': 7,
        'fg_color': GRAY_10,
        'text_wrap': 1,
        'valign': 'top'
    })
    stili['italic-bg_gray-medium'] = workbook.add_format({
        'italic': True,
        'border': 7,
        'fg_color': GRAY_10,
        'text_wrap': 1,
        'valign': 'top',
        'font_size': 10
    })
    stili['italic-bg_gray-no_wrap'] = workbook.add_format({
        'italic': True,
        'border': 7,
        'fg_color': GRAY_10,
        'valign': 'top'
    })
    stili['boxed'] = workbook.add_format({
        'border': 7,
        'text_wrap': 1,
        'valign': 'top'
    })
    stili['boxed_small'] = workbook.add_format({
        'border': 7,
        'text_wrap': 1,
        'valign': 'top',
        'font_size': 9
    })
    stili['boxed_small_italic'] = workbook.add_format({
        'italic': True,
        'font_size': 11,
        'border': 7
    })
    stili['boxed-10'] = workbook.add_format({
        'border': 7,
        'text_wrap': 1,
        'valign': 'top',
        'font_size': 10,
    })
    stili['border-left_small'] = workbook.add_format({
        'left': 7,
        'text_wrap': 1,
        'valign': 'top',
        'font_size': 9
    })
    stili['border-right_small'] = workbook.add_format({
        'right': 7,
        'text_wrap': 1,
        'valign': 'top',
        'font_size': 9
    })
    stili['border-right'] = workbook.add_format({
        'right': 7,
        'text_wrap': 1,
        'valign': 'top'
    })
    stili['border-bottom-right'] = workbook.add_format({
        'right': 7,
        'bottom': 7
    })
    # date = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    stili['date-left'] = workbook.add_format({
        'num_format': 'dd/mm/yyyy', 
        'align': 'left',
        'valign': 'top',
        'border': 7
        })
    stili['date_left_boxed'] = workbook.add_format({
        'num_format': 'dd/mm/yyyy', 
        'align': 'left',
        'border': 7
        })
    stili['date-right'] = workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'right'})

    stili['cella-riga'] = workbook.add_format({
        'text_wrap': 1,
        'valign': 'bottom',
        'border': 7   # bisognerebbe usare 4 per ottenere una linea dotted, ma stampato risulta una linea spessa
    })
    stili['cella-riga-8'] = workbook.add_format({
        'text_wrap': 1,
        'valign': 'bottom',
        'border': 7,   # bisognerebbe usare 4 per ottenere una linea dotted, ma stampato risulta una linea spessa
        'font_size': 8
    })
    stili['cella-riga-centrato'] = workbook.add_format({
        'text_wrap': 1,
        'valign': 'bottom',
        'align': 'center',
        'border': 7   # bisognerebbe usare 4 per ottenere una linea dotted, ma stampato risulta una linea spessa
    })
    stili['cella-riga-soldi'] = workbook.add_format({
        'text_wrap': 1,
        'valign': 'bottom',
        'num_format': '#,##0.00€',
        'border': 7
    })
    stili['cella-riga-soldi-8'] = workbook.add_format({
        'text_wrap': 1,
        'valign': 'bottom',
        'num_format': '#,##0.00000€',  # 5 cifre decimali
        'border': 7,
        'font_size': 8
    })
    stili['cella-riga-soldi-anna'] = workbook.add_format({
        'text_wrap': 1,
        'valign': 'bottom',
        'num_format': '_-"€ "* #,##0.00_-;_-"€ "* -#,##0.00_-;_-"€ "* -??_-;_-@_-',
        'border': 7
    })
    stili['cella-riga-data'] = workbook.add_format({
        'text_wrap': 1,
        'valign': 'bottom',
        'num_format': 'dd/mm/yyyy', 
        'align': 'right',
        'border': 7   # bisognerebbe usare 4 per ottenere una linea dotted, ma stampato risulta una linea spessa
    })

    stili['soldi'] = workbook.add_format({'num_format': '#,##0.00€'})
    stili['boxed-soldi-bold'] = workbook.add_format({
        'num_format': '#,##0.00€', 
        'bold': True,
        'border': 7
    })
    stili['boxed-soldi'] = workbook.add_format({
        'num_format': '#,##0.00€', 
        'border': 7
    })
    stili['boxed-percentuale'] = workbook.add_format({
        'num_format': '0.00%', 
        'border': 7
    })
    stili['boxed-2decimali'] = workbook.add_format({
        'num_format': '0.00', 
        'border': 7
    })
    stili['soldi-bold'] = workbook.add_format({'num_format': '#,##0.00€', 'bold': 1})
    # questo stile credo non sia usato:
    stili['percentuale'] = workbook.add_format({'num_format': '#,##0%'})
    stili['testo-centrato'] = workbook.add_format({
        'align': 'center'
    })
    stili['testo-centrato'] = workbook.add_format({
        'align': 'center'
    })
    stili['testo-centrato_small'] = workbook.add_format({
        'align': 'center',
        'font_size': 9
    })
    stili['testo-a-capo'] = workbook.add_format({
        'text_wrap': 1
    })
    stili['testo-a-capo_small'] = workbook.add_format({
        'text_wrap': 1,
        'font_size': 9
    })
    stili['testo-a-capo-boxed'] = workbook.add_format({
        'text_wrap': 1, 
        'border': 7
    })
    stili['testo-a-capo-boxed_small'] = workbook.add_format({
        'text_wrap': 1, 
        'border': 7,
        'font_size': 9
    })
    stili['bordo_sotto'] = workbook.add_format({
        'bottom': 7
    })
    stili['boxed_c11_italic_shrinked'] = workbook.add_format({
        'shrink': 1,
        'font_size': 11,
        'italic': 1,
        'border': 7
    })
    stili['shrinked_c11_boxed'] = workbook.add_format({
        'shrink': 1,
        'font_size': 11,
        'border': 7
    })
    stili['shrinked'] = workbook.add_format({
        'shrink': 1
    })
    stili['bordo_a_u'] = workbook.add_format({
        'bottom': 7,
        'left': 7,
        'right': 7
    })

    # totali nelle fatture:
    stili['imponibile'] = workbook.add_format({
        'bottom': 7,
        'right': 7,
        'top': 1,
        'left': 1,
        'bold': 1,
        'align': 'center'
    })
    stili['imponibile_value'] = workbook.add_format({
        'top': 1,
        'right': 1,
        'bottom': 7,
        'left': 7,
        'bold': 1,
        'num_format': '_-"€ "* #,##0.00_-;_-"€ "* -#,##0.00_-;_-"€ "* -??_-;_-@_-'
    })
    stili['iva'] = workbook.add_format({
        'top': 7,
        'right': 7,
        'bottom': 7,
        'left': 1,
        'bold': 1,
        'align': 'center'
    })
    stili['iva_value'] = workbook.add_format({
        'top': 7,
        'right': 1,
        'bottom': 7,
        'left': 7,
        'bold': 1,
        'num_format': '_-"€ "* #,##0.00_-;_-"€ "* -#,##0.00_-;_-"€ "* -??_-;_-@_-'
    })
    stili['iva_esenzione'] = workbook.add_format({
        'top': 7,
        'right': 7,
        'bottom': 7,
        'left': 1,
        'bold': 1,
        'align': 'left',
        'text_wrap': 1
    })
    stili['totale_fattura'] = workbook.add_format({
        'top': 7,
        'right': 7,
        'bottom': 1,
        'left': 1,
        'bold': 1,
        'align': 'center',
        'text_wrap': 1
    })
    stili['totale_fattura_value'] = workbook.add_format({
        'top': 7,
        'right': 1,
        'bottom': 1,
        'left': 7,
        'bold': 1,
        'num_format': '_-"€ "* #,##0.00_-;_-"€ "* -#,##0.00_-;_-"€ "* -??_-;_-@_-',
        'valign': 'bottom'
    })

    return stili


def get_dati_entita(cliente):
    """
    Restituisce i dati di un'entità (cliente o fornitore).
    """
    dati_entita = {}
    dati_entita['nome_completo'] = cliente.get_nome_completo()
    dati_entita['numero_telefono'] = cliente.get_contatto(CONTATTO_TEL_UFFICIO)
    dati_entita['numero_fax'] = cliente.get_contatto(CONTATTO_FAX)
    dati_entita['via'], dati_entita['citta_e_pr'] = cliente.get_indirizzo_in_due_campi(SEDE_AMMINISTRATIVA)
    # dati_entita['attenzione_di'] = cliente.persona_di_riferimento if cliente.persona_di_riferimento else ""
    dati_entita['email'] = cliente.get_contatto(CONTATTO_EMAIL)
    return dati_entita


def get_indirizzo_proprietario():
    try:
        return Entita.objects.proprietario().get_indirizzo(SEDE_LEGALE, "medio")
    except:
        # errore durante il recupero della sede legale del proprietario
        return ""


def get_altezza_cella(frase, caratteri_per_cella=34):
    # La cella excel può contenere fino a 34 caratteri.
    # da 1 a 34   --> 1 riga
    # da 35 a 68  --> 2 righe
    # ...
    # Usare il carattere 'm' per la conta.
    # Visto che alcuni caratteri sono più piccoli di altri, aumento 
    # il valore di caratteri_per_cella di un tot.
    caratteri_per_cella += 15
    # import pdb; pdb.set_trace()
    righe = len(frase) / caratteri_per_cella
    if righe == int(righe):
        righe = int(righe)
    else:
        righe = int(righe) + 1
    # ogni riga in excel è alta 15
    altezza_cella = righe * 15
    return altezza_cella


def get_ragione_sociale(data):

    if data < DATA_CAMBIO_RAGIONE_SOCIALE:
        return RAGIONE_SOCIALE_VECCHIA
    else:
        return RAGIONE_SOCIALE_NUOVA
