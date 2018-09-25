#!/usr/bin/python
# -*- coding: utf-8 -*-


import io
import json
import xlsxwriter
from datetime import date

from django.conf import settings
from anagrafiche.models import *
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from anagrafiche.stampe.xlsUtils import crea_stili, get_dati_entita, \
    get_altezza_cella, get_indirizzo_proprietario, get_ragione_sociale


@csrf_exempt
def crea_xls_preventivo_cliente(request, id_preventivo):

    preventivo = get_object_or_404(PreventivoCliente, pk=id_preventivo)

    u = request.user 
    if not u.has_perm('anagrafiche._preventivoCliente:*'):
        ctx = {}
        ctx['msg'] = 'Non hai i permessi per aprire questa pagina.'
        return render(request, 'anagrafiche/msg.html', ctx)

    # http://stackoverflow.com/a/27405896/529323
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet()
    sheet.set_paper(9)  # A4
    # sheet.set_margins(0.24, 0.24, 0.47, 0.11)

    # larghezza colonne
    """
    sheet.set_column('A:A', 12) #1.24
    sheet.set_column('B:B', 13) #1.33
    sheet.set_column('C:C', 14) #1.43
    sheet.set_column('D:D', 15) #1.53
    sheet.set_column('E:E', 16) #1.63   
    sheet.set_column('F:F', 17) #1.72
    sheet.set_column('G:G', 18) #1.82
    sheet.set_column('A:A', 19) #1.92
    sheet.set_column('B:B', 20) #2.01
    """
    sheet.set_column('A:A', 5)
    sheet.set_column('B:B', 12)
    sheet.set_column('C:C', 7)
    sheet.set_column('D:D', 4)
    sheet.set_column('E:E', 9)
    sheet.set_column('F:F', 13)
    sheet.set_column('G:G', 4)
    sheet.set_column('H:H', 4)
    sheet.set_column('I:I', 11)
    sheet.set_column('J:J', 11)

    stili = crea_stili(workbook)

    sheet.merge_range('A1:J1', 'PREVENTIVO', stili['bold-centrato-bg_gray'])

    logo_params =  {
        'x_scale': 0.40,
        'y_scale': 0.65,
    }
    sheet.insert_image("A3", "{}anagrafiche/static/img/mrFerro.jpg".format(settings.XLS_IMAGE_PATH), 
        logo_params)

    sheet.merge_range('F3:J3', get_ragione_sociale(preventivo.data), stili['bold'])
    sheet.merge_range('F4:J4', get_indirizzo_proprietario())
    # sheet.merge_range('F5:J5', '')
    sheet.merge_range('F5:J5', 'Tel. e Fax 035.4499168')
    sheet.merge_range('F6:J6', 'E-mail: info@mrferro.it / amministrazione@mrferro.it')
    sheet.merge_range('F7:J7', 'Reg. Imp. BG - C.F. E P.IVA 03362370169')

    # sheet.merge_range('A10:B10', 'ORDINE', stili['bold-centrato-bg_gray'])
    # sheet.merge_range('D10:G10', 'CLIENTE', stili['bold-centrato-bg_gray'])

    dati_cliente = get_dati_entita(preventivo.cliente)    
    
    riga = 8
    sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Ditta', stili['italic-bg_gray'])
    # sheet.merge_range('B10:C10', dati_cliente['nome_completo'], stili['boxed'])
    sheet.merge_range(riga, 1, riga, 2, dati_cliente['nome_completo'], stili['boxed'])
    sheet.write(riga, 3, 'Tel.', stili['italic-bg_gray'])
    sheet.merge_range(riga, 4, riga, 5, dati_cliente['numero_telefono'], stili['boxed'])
    sheet.merge_range(riga, 6, riga, 7, 'Preventivo', stili['italic-bg_gray-no_wrap'])
    sheet.merge_range(riga, 8, riga, 9, preventivo.codice, stili['boxed'])

    riga += 1
    sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Via e N°', stili['italic-bg_gray'])
    sheet.merge_range(riga, 1, riga, 2, dati_cliente['via'], stili['boxed'])
    sheet.write(riga, 3, 'Fax', stili['italic-bg_gray'])
    sheet.merge_range(riga, 4, riga, 5, dati_cliente['numero_fax'], stili['boxed'])
    sheet.merge_range(riga, 6, riga, 7, 'Data', stili['italic-bg_gray'])
    sheet.merge_range(riga, 8, riga, 9, preventivo.data, stili['date-left'])
    
    riga += 1
    sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Città', stili['italic-bg_gray'])
    sheet.merge_range(riga, 1, riga, 2, dati_cliente['citta_e_pr'], stili['boxed'])
    sheet.write(riga, 3, 'Cant.', stili['italic-bg_gray-no_wrap'])
    sheet.merge_range(riga, 4, riga, 5, preventivo.destinazione.get_indirizzo_corto(), stili['boxed'])
    sheet.merge_range(riga, 6, riga+1, 7, 'Oggetto', stili['italic-bg_gray'])
    sheet.merge_range(riga, 8, riga+1, 9, preventivo.oggetto, stili['boxed'])
    
    riga += 1
    sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Alla \nC. A.', stili['italic-bg_gray'])
    sheet.merge_range(riga, 1, riga, 2, preventivo.persona_di_riferimento, stili['boxed'])
    sheet.write(riga, 3, 'Mail', stili['italic-bg_gray'])
    sheet.merge_range(riga, 4, riga, 5, dati_cliente['email'], stili['boxed'])
    # sheet.merge_range('G13:J13', '', stili['border-bottom-right'])

    riga += 2
    sheet.set_row(riga, 30)
    sheet.merge_range(riga, 0, riga, 5, 'DESCRIZIONE', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 6, 'UM', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 7, 'QTA', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 8, 'PREZZO UNITARIO', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 9, 'IMPORTO', stili['bold-centrato-bg_gray'])

    righe = preventivo.righe.all().filter(cancellato=False)
    riga +=1
    for r in righe:
        # la lunghezza della descrizione può arrivare a 1000 caratteri. Cerco di prevedere 
        # quando deve essere alta la riga contando i caratteri della descrizione:
        altezza_riga = get_altezza_cella(r.articolo_descrizione)
        sheet.set_row(riga, altezza_riga)
        sheet.merge_range(riga, 0, riga, 5, r.articolo_descrizione, stili['cella-riga'])
        # sheet.write(riga, 0, r.articolo_descrizione, stili['cella-riga'])
        sheet.write(riga, 6, r.get_articolo_unita_di_misura_display(), stili['cella-riga'])
        sheet.write(riga, 7, r.quantita, stili['cella-riga'])
        sheet.write(riga, 8, r.articolo_prezzo, stili['cella-riga-soldi'])
        sheet.write(riga, 9, r.totale, stili['cella-riga-soldi'])
        riga += 1

    # box(workbook, sheet, 15, 0, riga, 9)
    if preventivo.totale_su_stampa:
        sheet.write(riga, 8, 'TOTALE', stili['boxed-bold'])
        sheet.write(riga, 9, preventivo.totale, stili['boxed-soldi-bold'])
    else:
        riga -= 1

    riga += 2
    sheet.write(riga, 0, 'Il presente preventivo ha validità un mese dalla data di emissione', stili['bold_small'])
    riga += 1
    sheet.write(riga, 0, 'I prezzi si intendono I.V.A. esclusa - Prezzi F.Co Ns. magazzino', stili['small'])

    riga += 1
    sheet.merge_range(riga, 0, riga, 9, 'CONDIZIONI DI PAGAMENTO', stili['bold-centrato-bg_gray_small'])
    riga += 1
    sheet.merge_range(riga, 0, riga, 9, preventivo.pagamento.descrizione, stili['boxed_small'])

    riga += 1
    sheet.merge_range(riga, 0, riga, 9, 'DOCUMENTAZIONE PROGETTUALE', stili['bold-centrato-bg_gray_small'])
    riga += 1
    if preventivo.disegni_costruttivi:
        disegni_costruttivi = 'Disegni costruttivi a carico del cliente: sì'
    else:
        disegni_costruttivi = 'Disegni costruttivi a carico del cliente: no'
    sheet.merge_range(riga, 0, riga, 4, disegni_costruttivi, stili['boxed_small'])
    if preventivo.relazione_di_calcolo:
        relazione_di_calcolo = 'Relazione di calcolo a carico del cliente: sì'
    else:
        relazione_di_calcolo = 'Relazione di calcolo a carico del cliente: no'
    sheet.merge_range(riga, 5, riga, 9, relazione_di_calcolo, stili['boxed_small'])

    riga += 1
    sheet.merge_range(riga, 0, riga, 9, 'CARATTERISTICHE PRODOTTO/LAVORAZIONE', stili['bold-centrato-bg_gray_small'])
    riga += 1
    sheet.merge_range(riga, 0, riga, 2, "Tipo di acciaio: {}".format(preventivo.tipo_di_acciaio), stili['boxed_small'])
    sheet.merge_range(riga, 3, riga, 5, "Spessori: {}".format(preventivo.spessori), stili['boxed_small'])
    sheet.merge_range(riga, 6, riga, 9, "Zincatura: {}".format(preventivo.zincatura), stili['boxed_small'])
    riga += 1
    sheet.merge_range(riga, 0, riga, 2, "Classe di esecuzione: {}".format(preventivo.classe_di_esecuzione),
                      stili['boxed_small'])
    sheet.merge_range(riga, 3, riga, 5, "WPS: {}".format(preventivo.wps), stili['boxed_small'])
    sheet.merge_range(riga, 6, riga, 9, "Verniciatura: {}".format(preventivo.verniciatura), stili['boxed_small'])
    riga += 1
    sheet.set_row(riga, 22)
    sheet.merge_range(riga, 0, riga, 9, ('Qualora il cliente/progettista non espliciti la Classe di Esecuzione dei ' +
                      'prodotti, {} applica la Classe di Esecuzione EXC 2 come previsto dalla norma EN 1090-1.')
                      .format(get_ragione_sociale(preventivo.data)), stili['testo-a-capo-boxed_small'])

    if preventivo.note: 
        riga += 1
        sheet.merge_range(riga, 0, riga, 9, 'NOTE', stili['bold-centrato-bg_gray_small'])
        riga += 1
        sheet.merge_range(riga, 0, riga, 9, preventivo.note, stili['testo-a-capo-boxed_small'])

    riga += 1
    sheet.merge_range(riga, 0, riga, 9, 'CONDIZIONI GENERALI DI FORNITURA', stili['bold-centrato-bg_gray_small'])
    riga += 1
    """
    sheet.set_row(riga, 22)
    sheet.merge_range(riga, 0, riga, 9, 'Per tutto quanto non espressamente indicato nel presente preventivo si fa
    riferimento alle condizioni generali di fornitura M72-01-02.',
        stili['testo-a-capo-boxed_small'])
    """
    sheet.set_row(riga, 36)
    sheet.merge_range(riga, 0, riga, 9, 'Eventuali certificazioni e/o dichiarazioni dovranno essere richieste in fase' +
                      ' di preventivo e verranno rilasciate solo a completo pagamento della fattura finale.\nPer ' +
                      'tutto quanto non espressamente indicato nel presente preventivo si fa riferimento alle ' +
                      'condizioni generali di fornitura M72-01-02.',
        stili['testo-a-capo-boxed_small'])

    riga += 1
    sheet.set_row(riga, 22)
    sheet.merge_range(riga, 0, riga, 9, 'Vi preghiamo di voler sottoscrivere per accettazione il presente preventivo, '
                      + 'indicando Vs. ragione sociale corretta e, se necessario, banca d\'appoggio.',
        stili['testo-a-capo_small'])
    riga += 1
    sheet.merge_range(riga, 0, riga, 9, 'Così facendo ci permette di eseguire tempestivamente i lavori confermati.',
                      stili['small'])

    riga += 1
    sheet.merge_range(riga, 4, riga, 5, 'Firma per accettazione', stili['testo-centrato_small'])
    sheet.merge_range(riga, 7, riga, 9, 'Il Responsabile tecnico', stili['testo-centrato_small'])

    riga += 1
    sheet.set_row(riga, 10)

    riga += 1
    data_str = preventivo.data.strftime("%d/%m/%y")
    sheet.merge_range(riga, 0, riga, 2, 'Bolgare (Bg), lì {}'.format(data_str), stili['small'] )
    sheet.merge_range(riga, 4, riga, 5, '______________________________', stili['testo-centrato_small'])
    sheet.merge_range(riga, 7, riga, 9, '______________________________', stili['testo-centrato_small'])

    footer1 = '&L&7Documento realizzato con un programma dello Studio Gamma Snc.\nwww.studiogammasnc.it&R&7Pagina &P' \
              + ' di &N\n'
    # footer1 = '&"Tahoma,Bold"&4&Kff0000Hello, World!'
    sheet.set_footer(footer1)

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=preventivo " + preventivo.codice + ".xlsx"
    return response


@csrf_exempt
def crea_xls_preventivo_fornitore(request, id_preventivo):

    preventivo = get_object_or_404(PreventivoFornitore, pk=id_preventivo)

    u = request.user 
    if not u.has_perm('anagrafiche._preventivoFornitore:*'):
        ctx = {}
        ctx['msg'] = 'Non hai i permessi per aprire questa pagina.'
        return render(request, 'anagrafiche/msg.html', ctx)

    # http://stackoverflow.com/a/27405896/529323
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet()
    sheet.set_paper(9)  # A4
    # sheet.set_margins(0.24, 0.24, 0.47, 0.11)

    # larghezza colonne
    """
    sheet.set_column('A:A', 12) #1.24
    sheet.set_column('B:B', 13) #1.33
    sheet.set_column('C:C', 14) #1.43
    sheet.set_column('D:D', 15) #1.53
    sheet.set_column('E:E', 16) #1.63   
    sheet.set_column('F:F', 17) #1.72
    sheet.set_column('G:G', 18) #1.82
    sheet.set_column('A:A', 19) #1.92
    sheet.set_column('B:B', 20) #2.01
    """
    sheet.set_column('A:A', 5)
    sheet.set_column('B:B', 12)
    sheet.set_column('C:C', 7)
    sheet.set_column('D:D', 4)
    sheet.set_column('E:E', 9)
    sheet.set_column('F:F', 13)
    sheet.set_column('G:G', 4)
    sheet.set_column('H:H', 4)
    sheet.set_column('I:I', 11)
    sheet.set_column('J:J', 11)

    stili = crea_stili(workbook)

    sheet.merge_range('A1:J1', 'RICHIESTA PREVENTIVO FORNITORE', stili['bold-centrato-bg_gray'])

    logo_params =  {
        'x_scale': 0.40,
        'y_scale': 0.65,
    }
    sheet.insert_image("A3", "{}anagrafiche/static/img/mrFerro.jpg".format(settings.XLS_IMAGE_PATH), 
        logo_params)

    sheet.merge_range('F3:J3', get_ragione_sociale(preventivo.data), stili['bold'])
    sheet.merge_range('F4:J4', get_indirizzo_proprietario())
    # sheet.merge_range('F5:J5', 'Sede operativa: via Lago d\'Iseo, 5 - 24060 Bolgare (BG)')
    sheet.merge_range('F5:J5', 'Tel. e Fax 035.4499168')
    sheet.merge_range('F6:J6', 'E-mail: info@mrferro.it / amministrazione@mrferro.it')
    sheet.merge_range('F7:J7', 'Reg. Imp. BG - C.F. E P.IVA 03362370169')

    # sheet.merge_range('A10:B10', 'ORDINE', stili['bold-centrato-bg_gray'])
    # sheet.merge_range('D10:G10', 'CLIENTE', stili['bold-centrato-bg_gray'])

    dati_fornitori = get_dati_entita(preventivo.fornitore)    

    riga = 8
    sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Ditta', stili['italic-bg_gray'])
    sheet.merge_range(riga, 1, riga, 2, dati_fornitori['nome_completo'], stili['boxed'])
    sheet.write(riga, 3, 'Tel.', stili['italic-bg_gray'])
    sheet.merge_range(riga, 4, riga, 5, dati_fornitori['numero_telefono'], stili['boxed'])
    sheet.merge_range(riga, 6, riga, 7, 'Preventivo', stili['italic-bg_gray-no_wrap'])
    sheet.merge_range(riga, 8, riga, 9, preventivo.codice, stili['boxed'])
    
    riga += 1
    sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Via e N°', stili['italic-bg_gray'])
    sheet.merge_range(riga, 1, riga, 2, dati_fornitori['via'], stili['boxed'])
    sheet.write(riga, 3, 'Fax', stili['italic-bg_gray'])
    sheet.merge_range(riga, 4, riga, 5, dati_fornitori['numero_fax'], stili['boxed'])
    sheet.merge_range(riga, 6, riga, 7, 'Data', stili['italic-bg_gray'])
    sheet.merge_range(riga, 8, riga, 9, preventivo.data, stili['date-left'])
    
    riga += 1
    sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Città', stili['italic-bg_gray'])
    sheet.merge_range(riga, 1, riga, 2, dati_fornitori['citta_e_pr'], stili['boxed'])
    sheet.write(riga, 3, 'Cant.', stili['italic-bg_gray-no_wrap'])
    sheet.merge_range(riga, 4, riga, 5, preventivo.destinazione.get_indirizzo_corto(), stili['boxed'])
    sheet.merge_range(riga, 6, riga+1, 7, 'Ns. Commessa', stili['italic-bg_gray-medium'])
    # i preventivi possono avere commessa nulla; forse sarebbe meglio rendere il campo obbligatorio
    # ma per ora uso questo workaround:
    codice_commessa = preventivo.commessa.codice if preventivo.commessa else ''
    sheet.merge_range(riga, 8, riga+1, 9, codice_commessa, stili['boxed'])
    
    riga += 1
    sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Alla \nC. A.', stili['italic-bg_gray'])
    sheet.merge_range(riga, 1, riga, 2, preventivo.persona_di_riferimento, stili['boxed'])
    sheet.write(riga, 3, 'Mail', stili['italic-bg_gray'])
    sheet.merge_range(riga, 4, riga, 5, dati_fornitori['email'], stili['boxed'])
    # sheet.merge_range('G13:J13', '', stili['border-bottom-right'])
    
    riga += 1
    sheet.write(riga, 0,
                'Inserire il codice della nostra commessa su tutta la Vs. documentazione (Ddt, fatture, ecc.).',
                stili['small'])

    riga +=2
    sheet.set_row(riga, 30)
    sheet.merge_range(riga, 0, riga, 5, 'DESCRIZIONE', stili['bold-centrato-bg_gray'])
    sheet.merge_range(riga, 6, riga, 7, 'U. M.', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 8, 'QUANTITÀ', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 9, 'CONSEGNA', stili['bold-centrato-bg_gray'])

    righe = preventivo.righe.all().filter(cancellato=False)
    riga +=1
    for r in righe:
        # la lunghezza della descrizione può arrivare a 1000 caratteri. Cerco di prevedere 
        # quando deve essere alta la riga contando i caratteri della descrizione:
        altezza_riga = get_altezza_cella(r.articolo_descrizione)
        sheet.set_row(riga, altezza_riga)
        sheet.merge_range(riga, 0, riga, 5, r.articolo_descrizione, stili['cella-riga'])
        sheet.merge_range(riga, 6, riga, 7, r.get_articolo_unita_di_misura_display(), stili['cella-riga'])
        # sheet.write(riga, 0, r.articolo_descrizione, stili['cella-riga'])
        sheet.write(riga, 8, r.quantita, stili['cella-riga'])
        sheet.write(riga, 9, r.data_consegna, stili['cella-riga-data'])
        riga += 1

    riga += 2
    sheet.write(riga, 0, 'I prezzi si intendono I.V.A. esclusa - Prezzi F.Co Ns. magazzino.', stili['small'])
    # Issue sulla certificazione ferro è in sospeso:
    # riga += 1
    # sheet.write(riga, 0, 'Tutto il ferro fornito deve essere certificato 3.1.', stili['small'])
    riga += 1
    sheet.set_row(riga, 28)
    sheet.merge_range(riga, 0, riga, 9, 'DOCUMENTI RICHIESTI - si chiede di inviare sempre le dichiarazioni di ' +
                      'conformità dei materiali richiesti - Tutti i prodotti devono recare la marcatura CE ai sensi ' +
                      'del DPR 246/93 e al D.M. 14/01/2008.', stili['testo-a-capo_small'])

    riga += 1
    sheet.merge_range(riga, 0, riga, 9, 'CONDIZIONI DI PAGAMENTO', stili['bold-centrato-bg_gray_small'])
    riga += 1
    sheet.merge_range(riga, 0, riga, 9, preventivo.pagamento.descrizione, stili['boxed_small'])

    if preventivo.note: 
        riga += 1
        sheet.merge_range(riga, 0, riga, 9, 'NOTE', stili['bold-centrato-bg_gray_small'])
        riga += 1
        sheet.merge_range(riga, 0, riga, 9, preventivo.note, stili['testo-a-capo-boxed_small'])

    """
    riga += 1
    sheet.merge_range(riga, 0, riga, 9, 'CONDIZIONI GENERALI DI FORNITURA', stili['bold-centrato-bg_gray_small'])
    riga += 1
    sheet.set_row(riga, 22)
    sheet.merge_range(riga, 0, riga, 9, 'Per tutto quanto non espressamente indicato nel presente preventivo si fa '
    + ' riferimento alle condizioni generali di fornitura M72-01-02.',
        stili['testo-a-capo-boxed_small'])
    """

    riga += 1
    sheet.set_row(riga, 22)
    sheet.merge_range(riga, 0, riga, 9, 'Vi preghiamo di inviarci preventivo per i seguenti articoli.',
                      stili['testo-a-capo_small'])
    """
    riga += 1
    sheet.merge_range(riga, 0, riga, 9, 'Così facendo ci permette di eseguire tempestivamente i lavori confermati.',
    stili['small'])
    """

    riga += 2
    sheet.merge_range(riga, 4, riga, 5, 'Firma per accettazione', stili['testo-centrato_small'])
    sheet.merge_range(riga, 7, riga, 9, 'Il Responsabile tecnico', stili['testo-centrato_small'])

    riga += 1
    sheet.set_row(riga, 10)

    riga += 1
    data_str = preventivo.data.strftime("%d/%m/%y")
    sheet.merge_range(riga, 0, riga, 2, 'Bolgare (Bg), lì {}'.format(data_str), stili['small'] )
    sheet.merge_range(riga, 4, riga, 5, '______________________________', stili['testo-centrato_small'])
    sheet.merge_range(riga, 7, riga, 9, '______________________________', stili['testo-centrato_small'])

    footer1 = '&L&7Documento realizzato con un programma dello Studio Gamma Snc.\nwww.studiogammasnc.it&R&7Pagina &P' \
              + ' di &N\n'
    sheet.set_footer(footer1)

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=preventivo " + preventivo.codice + ".xlsx"
    return response



