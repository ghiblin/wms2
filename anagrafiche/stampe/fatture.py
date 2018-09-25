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

from anagrafiche.stampe.xlsUtils import crea_stili, get_dati_entita, get_altezza_cella, \
    get_indirizzo_proprietario, get_ragione_sociale

riga = 0
salta_una_riga_dopo_bolle = False
salta_una_riga_dopo_righe_senza_bolle = False


def scrivi_righe_con_bolla(fattura, sheet, stili):
    global riga
    global salta_una_riga_dopo_bolle
    global salta_una_riga_dopo_righe_senza_bolle

    righe = fattura.righe.all().filter(cancellato=False).exclude(riga_bolla__bolla=None).order_by('riga_bolla__bolla')
    if righe: 
        # fa in modo che quando è chiamato l'altro metodo si lasci una riga vuota
        salta_una_riga_dopo_bolle = True

    if salta_una_riga_dopo_righe_senza_bolle:
        riga += 1

    bolla = None
    for r in righe:
        if r.riga_bolla is not None and r.riga_bolla.bolla != bolla:
            # a parte la prima bolla, lascia una riga vuota tra i prodotti di una
            # bolla e l'altra.
            if bolla is not None:
                riga += 1 

            bolla = r.riga_bolla.bolla
            sheet.merge_range(riga, 0, riga, 6, 
                              '    Bolla {} del {}:'.format(bolla.codice, bolla.data.strftime('%d/%m/%Y'))
                              , stili['cella-riga'])
            # sheet.write(riga, 8, '', stili['cella-riga'])
            # sheet.write(riga, 9, '', stili['cella-riga'])
            riga += 1

        # la lunghezza della descrizione può arrivare a 1000 caratteri. Cerco di prevedere 
        # quando deve essere alta la riga contando i caratteri della descrizione:
        altezza_riga = get_altezza_cella(r.articolo_descrizione, caratteri_per_cella=24)
        sheet.set_row(riga, altezza_riga)
        sheet.merge_range(riga, 0, riga, 1, r.articolo_descrizione, stili['cella-riga'])
        sheet.write(riga, 2, r.quantita, stili['cella-riga-centrato'])
        sheet.merge_range(riga, 3, riga, 4, r.articolo_prezzo, stili['cella-riga-soldi-anna'])
        sheet.write(riga, 5, r.totale, stili['cella-riga-soldi-anna'])
        sheet.write(riga, 6, "{} %".format(fattura.aliquota_IVA.percentuale), stili['cella-riga-centrato'])
        riga += 1


def scrivi_righe_senza_bolla(fattura, sheet, stili):
    global riga
    global salta_una_riga_dopo_bolle
    global salta_una_riga_dopo_righe_senza_bolle

    # rispetto all'altro metodo c'è il filtro riga_bolla__bolla=None
    righe = fattura.righe.all().filter(cancellato=False, riga_bolla__bolla=None).order_by('riga_bolla__bolla')
    if righe: 
        # fa in modo che quando è chiamato l'altro metodo si lasci una riga vuota
        salta_una_riga_dopo_righe_senza_bolle = True

    if salta_una_riga_dopo_bolle:
        riga += 1

    bolla = None
    for r in righe:
        if r.riga_bolla is not None and r.riga_bolla.bolla != bolla:
            # a parte la prima bolla, lascia una riga vuota tra i prodotti di una
            # bolla e l'altra.
            if bolla is not None:
                riga += 1 

            bolla = r.riga_bolla.bolla
            sheet.merge_range(riga, 0, riga, 6, 
                              '    Bolla {} del {}:'.format(bolla.codice, bolla.data.strftime('%d/%m/%Y'))
                              , stili['cella-riga'])
            # sheet.write(riga, 8, '', stili['cella-riga'])
            # sheet.write(riga, 9, '', stili['cella-riga'])
            riga += 1

        # la lunghezza della descrizione può arrivare a 1000 caratteri. Cerco di prevedere 
        # quando deve essere alta la riga contando i caratteri della descrizione:
        altezza_riga = get_altezza_cella(r.articolo_descrizione, caratteri_per_cella=24)
        sheet.set_row(riga, altezza_riga)
        sheet.merge_range(riga, 0, riga, 1, r.articolo_descrizione, stili['cella-riga'])
        sheet.write(riga, 2, r.quantita, stili['cella-riga-centrato'])
        sheet.merge_range(riga, 3, riga, 4, r.articolo_prezzo, stili['cella-riga-soldi-anna'])
        sheet.write(riga, 5, r.totale, stili['cella-riga-soldi-anna'])
        sheet.write(riga, 6, "{} %".format(fattura.aliquota_IVA.percentuale), stili['cella-riga-centrato'])
        riga += 1


@csrf_exempt
def crea_xls_fattura_cliente(request, id_fattura):
    
    # deve essere definita prima della funzione scrivi_righe_con_bolla che usa questa variabile
    global riga 
    global salta_una_riga_dopo_bolle
    global salta_una_riga_dopo_righe_senza_bolle

    # reset delle variabili globali o si hanno problemi stampando più di una fattura
    riga = 0
    salta_una_riga_dopo_bolle = False
    salta_una_riga_dopo_righe_senza_bolle = False

    fattura = get_object_or_404(FatturaCliente, pk=id_fattura)
    u = request.user 
    if not u.has_perm('anagrafiche._fatturaCliente:*'):
        ctx = {}
        ctx['msg'] = 'Non hai i permessi per aprire questa pagina.'
        return render(request, 'anagrafiche/msg.html', ctx)

    # fattura.aliquota_IVA.percentuale
    if not fattura.aliquota_IVA:
        ctx = {}
        ctx['msg'] = 'Seleziona un\'aliquota IVA prima di stampare la fattura.'
        return render(request, 'anagrafiche/msg.html', ctx)

    # http://stackoverflow.com/a/27405896/529323
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet()
    sheet.set_paper(9)  # A4
    # sheet.set_margins(0.24, 0.24, 0.47, 0.11)

    # larghezza colonne
    sheet.set_column('A:A', 15)
    sheet.set_column('B:B', 26)
    sheet.set_column('C:C', 5)
    sheet.set_column('D:D', 11)
    sheet.set_column('E:E', 3)
    sheet.set_column('F:F', 13)
    sheet.set_column('G:G', 9)

    stili = crea_stili(workbook)
    
    logo_params = {
        'x_scale': 0.40,
        'y_scale': 0.65,
    }
    
    pagebreaks = []

    sheet.merge_range(riga, 0, riga, 6, 'FATTURA COMMERCIALE', stili['bold-centrato-bg_gray'])

    riga += 2
    sheet.insert_image(riga, 0, "{}anagrafiche/static/img/mrFerro.jpg".format(settings.XLS_IMAGE_PATH), logo_params)
    sheet.merge_range(riga, 3, riga, 6, get_ragione_sociale(fattura.data), stili['bold'])
    riga += 1
    sheet.merge_range(riga, 3, riga, 6, get_indirizzo_proprietario(), stili['c8'])
    # riga += 1
    # sheet.merge_range(riga, 3, riga, 6, 'Sede operativa: via Lago d\'Iseo, 5 - 24060 Bolgare (BG)',
    #    stili['c8'])
    riga += 1
    sheet.merge_range(riga, 3, riga, 6, 'Tel. e Fax 035.4499168', stili['c8'])
    riga += 1
    sheet.merge_range(riga, 3, riga, 6, 'E-mail: info@mrferro.it / amministrazione@mrferro.it', stili['c8'])
    riga += 1
    sheet.merge_range(riga, 3, riga, 6, 'Reg. Imp. BG - C.F. E P.IVA 03362370169', stili['c8'])
    riga += 2

    # sheet.merge_range('A10:B10', 'ORDINE', stili['bold-centrato-bg_gray'])
    # sheet.merge_range('D10:G10', 'CLIENTE', stili['bold-centrato-bg_gray'])

    dati_cliente = get_dati_entita(fattura.cliente)    
    
    sheet.merge_range(riga, 0, riga, 1, 'FATTURA COMMERCIALE', stili['bold-centrato-bg_gray'])
    sheet.merge_range(riga, 3, riga, 6, 'CLIENTE', stili['bold-centrato-bg_gray'])
    riga += 1

    # sheet.set_row(riga, 30)
    sheet.write(riga, 0, 'Fattura nr.', stili['boxed_c11_italic_shrinked'])
    sheet.write(riga, 1, fattura.codice, stili['shrinked_c11_boxed'])
    sheet.write(riga, 3, 'Spett.le', stili['boxed_c11_italic_shrinked'])
    sheet.merge_range(riga, 4, riga, 6, fattura.cliente.get_nome_completo(), stili['shrinked_c11_boxed'])
    riga += 1

    via_sede_legale, paese_sede_legale = fattura.cliente.get_indirizzo_in_due_campi(SEDE_LEGALE)
    sheet.write(riga, 0, 'Data', stili['boxed_c11_italic_shrinked'])
    sheet.write(riga, 1, fattura.data, stili['date_left_boxed'])
    sheet.write(riga, 3, 'Sede Legale', stili['boxed_c11_italic_shrinked'])
    sheet.merge_range(riga, 4, riga, 6, fattura.cliente.get_indirizzo(SEDE_LEGALE), stili['shrinked_c11_boxed'])
    riga += 1
    
    sheet.write(riga, 0, 'Vs. Ordine nr.', stili['boxed_c11_italic_shrinked'])
    sheet.write(riga, 1, fattura.riferimento_cliente, stili['shrinked_c11_boxed'])
    sheet.write(riga, 3, 'Sede Amm.', stili['boxed_c11_italic_shrinked'])
    sheet.merge_range(riga, 4, riga, 6, fattura.cliente.get_indirizzo(SEDE_AMMINISTRATIVA),
                      stili['shrinked_c11_boxed'])
    riga += 1

    if fattura.commessa:
        sheet.write(riga, 0, 'Commessa', stili['boxed_c11_italic_shrinked'])
        sheet.write(riga, 1, fattura.commessa.codice, stili['shrinked_c11_boxed'])
    else:
        via_sede_amm, paese_sede_amm = fattura.cliente.get_indirizzo_in_due_campi(SEDE_AMMINISTRATIVA)
        sheet.write(riga, 0, 'Modalità di pagamento', stili['boxed_c11_italic_shrinked'])
        sheet.write(riga, 1, fattura.pagamento.__str__(), stili['shrinked_c11_boxed'])
    sheet.write(riga, 3, 'P. IVA', stili['boxed_c11_italic_shrinked'])
    sheet.merge_range(riga, 4, riga, 6, fattura.cliente.partita_iva, 
                      stili['shrinked_c11_boxed'])
    riga += 1

    # Tolto il campo 'Scadenze' (come da richiesta di Anna) perché è inutile se non è valorizzato.
    # sheet.write(riga, 0, 'Scadenze', stili['boxed_c11_italic_shrinked'])
    # sheet.write(riga, 1, '', stili['shrinked_c11_boxed'])

    # Se alla riga sopra abbiamo scritto la commessa, qua dobbiamo scrivere i dettagli di pagamento. Altrimenti lascimao
    # le due celle della sezione di sinistra vuote
    if fattura.commessa:
        via_sede_amm, paese_sede_amm = fattura.cliente.get_indirizzo_in_due_campi(SEDE_AMMINISTRATIVA)
        sheet.write(riga, 0, 'Modalità di pagamento', stili['boxed_c11_italic_shrinked'])
        sheet.write(riga, 1, fattura.pagamento.__str__(), stili['shrinked_c11_boxed'])

    sheet.write(riga, 3, 'Cod. Fiscale', stili['boxed_c11_italic_shrinked'])
    sheet.merge_range(riga, 4, riga, 6, fattura.cliente.codice_fiscale, 
                      stili['shrinked_c11_boxed'])
    riga += 1

    riga += 1
    sheet.set_row(riga, 30)
    sheet.merge_range(riga, 0, riga, 1, 'DESCRIZIONE', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 2, 'Q.TÀ', stili['bold-centrato-bg_gray'])
    sheet.merge_range(riga, 3, riga, 4, 'PREZZO UNITARIO', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 5, 'IMPORTO', stili['bold-centrato-bg_gray'])
    sheet.write(riga, 6, 'IVA %', stili['bold-centrato-bg_gray'])

    riga += 1

    # ci sono tre casi da testare: solo righe senza bolle, solo righe appartenenti a bolle, 
    # righe con e senza bolle.
    # righe solo senza bolle:     vedere Fattura FC160007
    # righe solo con bolle:       vedere Fattura FC160016
    # righe con e senza bolle:    vedere Fattura FC160012 (poi diventerà FC160205 credo)

    if settings.STAMPA_PRIMA_BOLLE_SU_FATTURA:
        scrivi_righe_con_bolla(fattura, sheet, stili)
        scrivi_righe_senza_bolla(fattura, sheet, stili)
    else:
        scrivi_righe_senza_bolla(fattura, sheet, stili)
        scrivi_righe_con_bolla(fattura, sheet, stili)

    """
    righe = fattura.righe.all().filter(cancellato=False).order_by('riga_bolla__bolla')
    
    bolla = None
    for r in righe:
        if r.riga_bolla != None and r.riga_bolla.bolla != bolla:
            # a parte la prima bolla, lascia una riga vuota tra i prodotti di una
            # bolla e l'altra.
            if bolla != None:
                riga += 1 

            bolla = r.riga_bolla.bolla
            sheet.merge_range(riga, 0, riga, 6, 
                '    Bolla {} del {}:'.format(bolla.codice, bolla.data.strftime('%d/%m/%Y'))
                , stili['cella-riga'])
            #sheet.write(riga, 8, '', stili['cella-riga'])
            #sheet.write(riga, 9, '', stili['cella-riga'])
            riga += 1

        # la lunghezza della descrizione può arrivare a 1000 caratteri. Cerco di prevedere 
        # quando deve essere alta la riga contando i caratteri della descrizione:
        altezza_riga = get_altezza_cella(r.articolo_descrizione, caratteri_per_cella=24)
        sheet.set_row(riga, altezza_riga)
        sheet.merge_range(riga, 0, riga, 1, r.articolo_descrizione, stili['cella-riga'])
        sheet.write(riga, 2, r.quantita, stili['cella-riga-centrato'])
        sheet.merge_range(riga, 3, riga, 4, r.articolo_prezzo, stili['cella-riga-soldi-anna'])
        sheet.write(riga, 5, r.totale, stili['cella-riga-soldi-anna'])
        sheet.write(riga, 6, "{} %".format(fattura.aliquota_IVA.percentuale), 
            stili['cella-riga-centrato'])
        riga += 1
    """

    """
    if fattura.note: 
        riga += 1
        sheet.merge_range(riga, 0, riga, 9, 'NOTE', stili['bold-centrato-bg_gray_small'])
        riga += 1
        sheet.merge_range(riga, 0, riga, 9, fattura.note, stili['testo-a-capo-boxed_small'])
    """

    # sheet.write(riga, 1, "CONTRIBUTO AMBIENTALE CONAI ASSOLTO", stili['shrinked'])
    sheet.merge_range(riga, 1, riga, 2, "CONTRIBUTO AMBIENTALE CONAI ASSOLTO", stili['shrinked'])
    sheet.merge_range(riga, 3, riga, 4, 'IMPONIBILE', stili['imponibile'])
    sheet.merge_range(riga, 5, riga, 6, fattura.imponibile, stili['imponibile_value'])

    if fattura.imponibile_netto != fattura.imponibile:
        riga += 1
        sheet.merge_range(riga, 3, riga, 4, 'IMP. SCONTATO', stili['iva'])
        sheet.merge_range(riga, 5, riga, 6, fattura.imponibile_netto, stili['imponibile_value'])
    
    riga += 1
    if fattura.aliquota_IVA.percentuale != 0:
        # scrivi il totale dell'IVA
        sheet.merge_range(riga, 3, riga, 4, 'IVA {}%'.format(fattura.aliquota_IVA.percentuale), stili['iva'])
        sheet.merge_range(riga, 5, riga, 6, fattura.totale_iva, stili['iva_value'])
    else:
        # scrivi l'esenzione IVA
        sheet.set_row(riga, 30)
        sheet.merge_range(riga, 3, riga, 4, '', stili['iva'])
        sheet.merge_range(riga, 5, riga, 6, fattura.aliquota_IVA.descrizione, stili['iva_esenzione'])
    riga += 1
    sheet.set_row(riga, 30)
    sheet.merge_range(riga, 3, riga, 4, 'TOTALE\nFATTURA', stili['totale_fattura'])
    sheet.merge_range(riga, 5, riga, 6, fattura.totale, stili['totale_fattura_value'])
    
    footer1 = '&L&7Documento realizzato con un programma dello Studio Gamma Snc.\nwww.studiogammasnc.it&R&7Pagina &P' \
              + ' di &N\n'
    sheet.set_footer(footer1)

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=fattura " + fattura.codice + ".xlsx"
    return response
