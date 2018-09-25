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

@csrf_exempt
def crea_xls_bolla_cliente(request, id_bolla):

    bolla = get_object_or_404(BollaCliente, pk=id_bolla)
    u = request.user 
    if not u.has_perm('anagrafiche._bollaCliente:*'):
        ctx = {}
        ctx['msg'] = 'Non hai i permessi per aprire questa pagina.'
        return render(request, 'anagrafiche/msg.html', ctx)

    ## http://stackoverflow.com/a/27405896/529323
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet()
    sheet.set_paper(9)  # A4
    #sheet.set_margins(0.24, 0.24, 0.47, 0.11)

    # larghezza colonne
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
    
    logo_params =  {
        'x_scale': 0.40,
        'y_scale': 0.65,
    }
    riga = 0
    pagebreaks = []

    for copia in ('MITTENTE', 'DESTINATARIO', 'VETTORE'):

        sheet.merge_range(riga, 0, riga, 9, 'DOCUMENTO DI TRASPORTO (D.d.t.) - COPIA {}'.format(copia), stili['bold-centrato-bg_gray'])

        riga += 2
        sheet.insert_image(riga, 0, "{}anagrafiche/static/img/mrFerro.jpg".format(settings.XLS_IMAGE_PATH), 
            logo_params)

        sheet.merge_range(riga, 5, riga, 9, get_ragione_sociale(bolla.data), stili['bold'])
        riga += 1
        sheet.merge_range(riga, 5, riga, 9, get_indirizzo_proprietario())
        #riga += 1
        #sheet.merge_range(riga, 5, riga, 9, 'Sede operativa: via Lago d\'Iseo, 5 - 24060 Bolgare (BG)')
        riga += 1
        sheet.merge_range(riga, 5, riga, 9, 'Tel. e Fax 035.4499168')
        riga += 1
        sheet.merge_range(riga, 5, riga, 9,'E-mail: info@mrferro.it / amministrazione@mrferro.it')
        riga += 1
        sheet.merge_range(riga, 5, riga, 9, 'Reg. Imp. BG - C.F. E P.IVA 03362370169')
        riga += 2

        #sheet.merge_range('A10:B10', 'ORDINE', stili['bold-centrato-bg_gray'])
        #sheet.merge_range('D10:G10', 'CLIENTE', stili['bold-centrato-bg_gray'])

        dati_cliente = get_dati_entita(bolla.cliente)    
        
        sheet.set_row(riga, 30)
        sheet.write(riga, 0, 'Ditta', stili['italic-bg_gray'])
        sheet.merge_range(riga, 1, riga, 2, dati_cliente['nome_completo'], stili['boxed'])
        sheet.write(riga, 3, 'Tel.', stili['italic-bg_gray'])
        sheet.merge_range(riga, 4, riga, 5, dati_cliente['numero_telefono'], stili['boxed'])
        sheet.merge_range(riga, 6, riga, 7, 'Numero Doc.', stili['italic-bg_gray'])
        sheet.merge_range(riga, 8, riga, 9, bolla.codice, stili['boxed'])
        riga += 1

        sheet.set_row(riga, 30)
        sheet.write(riga, 0, 'Via e N°', stili['italic-bg_gray'])
        sheet.merge_range(riga, 1, riga, 2, dati_cliente['via'], stili['boxed'])
        sheet.write(riga, 3, 'Fax', stili['italic-bg_gray'])
        sheet.merge_range(riga, 4, riga, 5, dati_cliente['numero_fax'], stili['boxed'])
        sheet.merge_range(riga, 6, riga, 7, 'Data', stili['italic-bg_gray'])
        sheet.merge_range(riga, 8, riga, 9, bolla.data, stili['date-left'])
        riga += 1

        sheet.set_row(riga, 30)
        sheet.write(riga, 0, 'Città', stili['italic-bg_gray'])
        sheet.merge_range(riga, 1, riga, 2, dati_cliente['citta_e_pr'], stili['boxed'])
        sheet.write(riga, 3, 'Dest.', stili['italic-bg_gray-no_wrap'])
        sheet.merge_range(riga, 4, riga, 5, bolla.destinazione.get_indirizzo_corto(), stili['boxed'])
        """
        sheet.merge_range('G12:H12', 'Ordine e data ord.', stili['italic-bg_gray'])
        sheet.merge_range('I12:J12', "{} del {}".format(bolla.ordine.codice, bolla.data), stili['boxed'])
        """
        sheet.merge_range(riga, 6, riga, 7, 'Commessa', stili['italic-bg_gray-medium'])
        sheet.merge_range(riga, 8, riga, 9, bolla.commessa.codice, stili['boxed'])
        riga += 1

        """
        sheet.write('A13', 'Alla \nC. A.', stili['italic-bg_gray'])
        sheet.merge_range('B13:C13', ordine.persona_di_riferimento, stili['boxed'])
        sheet.write('D13', 'Mail', stili['italic-bg_gray'])
        sheet.merge_range('E13:F13', dati_cliente['email'], stili['boxed'])
        #sheet.merge_range('G13:J13', '', stili['border-bottom-right'])
        """

        riga += 1
        sheet.set_row(riga, 30)
        sheet.merge_range(riga, 0, riga, 7, 'DESCRIZIONE', stili['bold-centrato-bg_gray'])
        sheet.write(riga, 8, 'UNITÀ DI MISURA', stili['bold-centrato-bg_gray'])
        sheet.write(riga, 9, 'QUANTITÀ', stili['bold-centrato-bg_gray'])
        
        riga += 1
        righe = bolla.righe.all().filter(cancellato=False).order_by('riga_ordine__ordine')
        
        ordine = None
        for r in righe:
            if r.riga_ordine != None and r.riga_ordine.ordine !=ordine:
                # a parte il primo ordine, lascia una riga vuota tra i prodotti di un
                # ordine e l'altro.
                if ordine != None:
                    riga += 1 

                ordine = r.riga_ordine.ordine
                sheet.merge_range(riga, 0, riga, 7, 
                    '    Ordine {} del {}:'.format(ordine.codice, ordine.data.strftime('%d/%m/%Y'))
                    , stili['cella-riga'])
                sheet.write(riga, 8, '', stili['cella-riga'])
                sheet.write(riga, 9, '', stili['cella-riga'])
                riga += 1

            # la lunghezza della descrizione può arrivare a 1000 caratteri. Cerco di prevedere 
            # quando deve essere alta la riga contando i caratteri della descrizione:
            altezza_riga = get_altezza_cella(r.articolo_descrizione)
            sheet.set_row(riga, altezza_riga)
            sheet.merge_range(riga, 0, riga, 7, r.articolo_descrizione, stili['cella-riga'])
            sheet.write(riga, 8, r.get_articolo_unita_di_misura_display(), stili['cella-riga'])
            sheet.write(riga, 9, r.quantita, stili['cella-riga'])
            
            riga += 1

        vettore = bolla.vettore
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 'VETTORE', stili['bold-centrato-bg_gray_small'])
        sheet.merge_range(riga, 5, riga, 9, '', stili['bold-centrato-bg_gray_small'])
        
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 
            '{}'.format(vettore.get_nome_completo() if vettore else ''),
             stili['border-left_small'])
        sheet.merge_range(riga, 5, riga, 6, 'Causale:', stili['border-left_small'])
        sheet.merge_range(riga, 7, riga, 9, 
            '{}'.format(bolla.causale_trasporto.descrizione if bolla.causale_trasporto else ''),
             stili['border-right_small'])
        
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 
            'P. IVA {}'.format(vettore.partita_iva) if vettore else '',
             stili['border-left_small'])
        sheet.merge_range(riga, 5, riga, 6, 'Incoterm:', stili['border-left_small'])
        sheet.merge_range(riga, 7, riga, 9, 
            '{}'.format(bolla.porto.descrizione if bolla.porto else ''),
             stili['border-right_small'])
        
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 
            '{}'.format(vettore.get_indirizzo_in_due_campi(SEDE_LEGALE)[0] if vettore else ''),
             stili['border-left_small'])
        sheet.merge_range(riga, 5, riga, 6, 'Tipo trasporto:', stili['border-left_small'])
        sheet.merge_range(riga, 7, riga, 9, 
            '{}'.format(bolla.trasporto_a_cura.descrizione if bolla.trasporto_a_cura else ''),
             stili['border-right_small'])
        
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 
            '{}'.format(vettore.get_indirizzo_in_due_campi(SEDE_LEGALE)[1] if vettore else ''),
             stili['border-left_small'])
        sheet.merge_range(riga, 5, riga, 6, 'Aspetto esteriore:', stili['border-left_small'])
        sheet.merge_range(riga, 7, riga, 9, 
            '{}'.format(bolla.aspetto_esteriore.descrizione if bolla.aspetto_esteriore else ''),
             stili['border-right_small'])

        #riga += 1
        #sheet.merge_range(riga, 0, riga, 9, 'INFO', stili['bold-centrato-bg_gray_small'])
        riga += 1
        
        if bolla.peso_netto != None and bolla.peso_netto != "0":
            pn = "Peso netto: {}".format(bolla.peso_netto)
        else:
            pn = "Peso netto:"

        if bolla.peso_lordo != None and bolla.peso_lordo != "0":
            pl = "Peso lordo: {}".format(bolla.peso_lordo)
        else:
            pl = "Peso lordo:"

        if bolla.numero_colli != None and bolla.numero_colli != 0:
            nc = "Numero colli: {}".format(bolla.numero_colli)
        else:
            nc = "Numero colli:"

        sheet.merge_range(riga, 0, riga, 2, pn, stili['boxed_small'])
        sheet.merge_range(riga, 3, riga, 5, pl, stili['boxed_small'])
        sheet.merge_range(riga, 6, riga, 9, nc, stili['boxed_small'])
        
        if bolla.note: 
            riga += 1
            sheet.merge_range(riga, 0, riga, 9, 'NOTE', stili['bold-centrato-bg_gray_small'])
            riga += 1
            sheet.merge_range(riga, 0, riga, 9, bolla.note, stili['testo-a-capo-boxed_small'])

        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 'FIRMA CONDUCENTE', stili['bold-centrato-bg_gray_small'])
        sheet.merge_range(riga, 5, riga, 9, 'FIRMA CLIENTE', stili['bold-centrato-bg_gray_small'])
        riga += 1
        sheet.set_row(riga, 30)
        sheet.merge_range(riga, 0, riga, 4, '', stili['boxed'])
        sheet.merge_range(riga, 5, riga, 9, '', stili['boxed'])
        
        riga += 1
        pagebreaks.append(riga)

    # end for usato per creare le 3 copie

    footer1 = '&L&7Documento realizzato con un programma dello Studio Gamma Snc.\nwww.studiogammasnc.it'
    sheet.set_footer(footer1)

    sheet.set_h_pagebreaks(pagebreaks)
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=bolla " + bolla.codice + ".xlsx"
    return response





@csrf_exempt
def crea_xls_bolla_fornitore(request, id_bolla):

    bolla = get_object_or_404(BollaFornitore, pk=id_bolla)
    u = request.user 
    if not u.has_perm('anagrafiche._bollaFornitore:*'):
        ctx = {}
        ctx['msg'] = 'Non hai i permessi per aprire questa pagina.'
        return render(request, 'anagrafiche/msg.html', ctx)

    ## http://stackoverflow.com/a/27405896/529323
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet()
    sheet.set_paper(9)  # A4
    #sheet.set_margins(0.24, 0.24, 0.47, 0.11)

    # larghezza colonne
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
    
    logo_params =  {
        'x_scale': 0.40,
        'y_scale': 0.65,
    }
    riga = 0
    pagebreaks = []

    for copia in ('MITTENTE', 'DESTINATARIO', 'VETTORE'):

        sheet.merge_range(riga, 0, riga, 9, 'DOCUMENTO DI TRASPORTO (D.d.t.) - COPIA {}'.format(copia), stili['bold-centrato-bg_gray'])

        riga += 2
        sheet.insert_image(riga, 0, "{}anagrafiche/static/img/mrFerro.jpg".format(settings.XLS_IMAGE_PATH), 
            logo_params)

        sheet.merge_range(riga, 5, riga, 9, get_ragione_sociale(bolla.data), stili['bold'])
        riga += 1
        sheet.merge_range(riga, 5, riga, 9, get_indirizzo_proprietario())
        #riga += 1
        #sheet.merge_range(riga, 5, riga, 9, 'Sede operativa: via Lago d\'Iseo, 5 - 24060 Bolgare (BG)')
        riga += 1
        sheet.merge_range(riga, 5, riga, 9, 'Tel. e Fax 035.4499168')
        riga += 1
        sheet.merge_range(riga, 5, riga, 9,'E-mail: info@mrferro.it / amministrazione@mrferro.it')
        riga += 1
        sheet.merge_range(riga, 5, riga, 9, 'Reg. Imp. BG - C.F. E P.IVA 03362370169')
        riga += 2

        #sheet.merge_range('A10:B10', 'ORDINE', stili['bold-centrato-bg_gray'])
        #sheet.merge_range('D10:G10', 'CLIENTE', stili['bold-centrato-bg_gray'])

        dati_fornitore = get_dati_entita(bolla.fornitore)    
        
        sheet.set_row(riga, 30)
        sheet.write(riga, 0, 'Ditta', stili['italic-bg_gray'])
        sheet.merge_range(riga, 1, riga, 2, dati_fornitore['nome_completo'], stili['boxed'])
        sheet.write(riga, 3, 'Tel.', stili['italic-bg_gray'])
        sheet.merge_range(riga, 4, riga, 5, dati_fornitore['numero_telefono'], stili['boxed'])
        sheet.merge_range(riga, 6, riga, 7, 'Numero Doc.', stili['italic-bg_gray'])
        sheet.merge_range(riga, 8, riga, 9, bolla.codice, stili['boxed'])
        riga += 1

        sheet.set_row(riga, 30)
        sheet.write(riga, 0, 'Via e N°', stili['italic-bg_gray'])
        sheet.merge_range(riga, 1, riga, 2, dati_fornitore['via'], stili['boxed'])
        sheet.write(riga, 3, 'Fax', stili['italic-bg_gray'])
        sheet.merge_range(riga, 4, riga, 5, dati_fornitore['numero_fax'], stili['boxed'])
        sheet.merge_range(riga, 6, riga, 7, 'Data', stili['italic-bg_gray'])
        sheet.merge_range(riga, 8, riga, 9, bolla.data, stili['date-left'])
        riga += 1

        sheet.set_row(riga, 30)
        sheet.write(riga, 0, 'Città', stili['italic-bg_gray'])
        sheet.merge_range(riga, 1, riga, 2, dati_fornitore['citta_e_pr'], stili['boxed'])
        sheet.write(riga, 3, 'Dest.', stili['italic-bg_gray-no_wrap'])
        sheet.merge_range(riga, 4, riga, 5, bolla.destinazione.get_indirizzo_corto(), stili['boxed'])
        """
        sheet.merge_range('G12:H12', 'Ordine e data ord.', stili['italic-bg_gray'])
        sheet.merge_range('I12:J12', "{} del {}".format(bolla.ordine.codice, bolla.data), stili['boxed'])
        """
        sheet.merge_range(riga, 6, riga, 7, 'Commessa', stili['italic-bg_gray-medium'])
        sheet.merge_range(riga, 8, riga, 9, bolla.commessa.codice, stili['boxed'])
        riga += 1

        """
        sheet.write('A13', 'Alla \nC. A.', stili['italic-bg_gray'])
        sheet.merge_range('B13:C13', ordine.persona_di_riferimento, stili['boxed'])
        sheet.write('D13', 'Mail', stili['italic-bg_gray'])
        sheet.merge_range('E13:F13', dati_fornitore['email'], stili['boxed'])
        #sheet.merge_range('G13:J13', '', stili['border-bottom-right'])
        """

        riga += 1
        sheet.set_row(riga, 30)
        sheet.merge_range(riga, 0, riga, 7, 'DESCRIZIONE', stili['bold-centrato-bg_gray'])
        sheet.write(riga, 8, 'UNITÀ DI MISURA', stili['bold-centrato-bg_gray'])
        sheet.write(riga, 9, 'QUANTITÀ', stili['bold-centrato-bg_gray'])
        
        riga += 1
        righe = bolla.righe.all().filter(cancellato=False).order_by('riga_ordine__ordine')
        
        ordine = None
        for r in righe:
            if r.riga_ordine != None and r.riga_ordine.ordine !=ordine:
                # a parte il primo ordine, lascia una riga vuota tra i prodotti di un
                # ordine e l'altro.
                if ordine != None:
                    riga += 1 

                ordine = r.riga_ordine.ordine
                sheet.merge_range(riga, 0, riga, 7, 
                    '    Ordine {} del {}:'.format(ordine.codice, ordine.data.strftime('%d/%m/%Y'))
                    , stili['cella-riga'])
                sheet.write(riga, 8, '', stili['cella-riga'])
                sheet.write(riga, 9, '', stili['cella-riga'])
                riga += 1

            # la lunghezza della descrizione può arrivare a 1000 caratteri. Cerco di prevedere 
            # quando deve essere alta la riga contando i caratteri della descrizione:
            altezza_riga = get_altezza_cella(r.articolo_descrizione)
            sheet.set_row(riga, altezza_riga)
            sheet.merge_range(riga, 0, riga, 7, r.articolo_descrizione, stili['cella-riga'])
            sheet.write(riga, 8, r.get_articolo_unita_di_misura_display(), stili['cella-riga'])
            sheet.write(riga, 9, r.quantita, stili['cella-riga'])
            
            riga += 1

        vettore = bolla.vettore
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 'VETTORE', stili['bold-centrato-bg_gray_small'])
        sheet.merge_range(riga, 5, riga, 9, '', stili['bold-centrato-bg_gray_small'])
        
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 
            '{}'.format(vettore.get_nome_completo() if vettore else ''),
             stili['border-left_small'])
        sheet.merge_range(riga, 5, riga, 6, 'Causale:', stili['border-left_small'])
        sheet.merge_range(riga, 7, riga, 9, 
            '{}'.format(bolla.causale_trasporto.descrizione if bolla.causale_trasporto else ''),
             stili['border-right_small'])
        
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 
            'P. IVA {}'.format(vettore.partita_iva) if vettore else '',
             stili['border-left_small'])
        sheet.merge_range(riga, 5, riga, 6, 'Incoterm:', stili['border-left_small'])
        sheet.merge_range(riga, 7, riga, 9, 
            '{}'.format(bolla.porto.descrizione if bolla.porto else ''),
             stili['border-right_small'])
        
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 
            '{}'.format(vettore.get_indirizzo_in_due_campi(SEDE_LEGALE)[0] if vettore else ''),
             stili['border-left_small'])
        sheet.merge_range(riga, 5, riga, 6, 'Tipo trasporto:', stili['border-left_small'])
        sheet.merge_range(riga, 7, riga, 9, 
            '{}'.format(bolla.trasporto_a_cura.descrizione if bolla.trasporto_a_cura else ''),
             stili['border-right_small'])
        
        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 
            '{}'.format(vettore.get_indirizzo_in_due_campi(SEDE_LEGALE)[1] if vettore else ''),
             stili['border-left_small'])
        sheet.merge_range(riga, 5, riga, 6, 'Aspetto esteriore:', stili['border-left_small'])
        sheet.merge_range(riga, 7, riga, 9, 
            '{}'.format(bolla.aspetto_esteriore.descrizione if bolla.aspetto_esteriore else ''),
             stili['border-right_small'])

        #riga += 1
        #sheet.merge_range(riga, 0, riga, 9, 'INFO', stili['bold-centrato-bg_gray_small'])
        riga += 1
        
        if bolla.peso_netto != None and bolla.peso_netto != "0":
            pn = "Peso netto: {}".format(bolla.peso_netto)
        else:
            pn = "Peso netto:"

        if bolla.peso_lordo != None and bolla.peso_lordo != "0":
            pl = "Peso lordo: {}".format(bolla.peso_lordo)
        else:
            pl = "Peso lordo:"

        if bolla.numero_colli != None and bolla.numero_colli != 0:
            nc = "Numero colli: {}".format(bolla.numero_colli)
        else:
            nc = "Numero colli:"

        sheet.merge_range(riga, 0, riga, 2, pn, stili['boxed_small'])
        sheet.merge_range(riga, 3, riga, 5, pl, stili['boxed_small'])
        sheet.merge_range(riga, 6, riga, 9, nc, stili['boxed_small'])

        if bolla.causale_trasporto.is_conto_lavorazione():
            riga += 1
            sheet.set_row(riga, 26)
            frase_verniciatura = ('Verniciare secondo la norma EN ISO 12944 in classe di ' \
                + 'corrosività "{}" ed in conformità alla ns. IO7401 rev.01. Allegare ' \
                + 'dichiarazione di conformità.').format(bolla.classe_di_corrosivita)
            sheet.merge_range(riga, 0, riga, 9, frase_verniciatura, stili['testo-a-capo-boxed_small'])
            riga += 1
            frase_zincatura = 'Zincare in accordo alla norma ISO 1461 e in conformità alla ns. ' \
                + 'IO7401 rev.01 e allegare dichiarazione di conformità.'
            sheet.merge_range(riga, 0, riga, 9, frase_zincatura, stili['testo-a-capo-boxed_small'])


        if bolla.note: 
            riga += 1
            sheet.merge_range(riga, 0, riga, 9, 'NOTE', stili['bold-centrato-bg_gray_small'])
            riga += 1
            sheet.merge_range(riga, 0, riga, 9, bolla.note, stili['testo-a-capo-boxed_small'])



        riga += 1
        sheet.merge_range(riga, 0, riga, 4, 'FIRMA CONDUCENTE', stili['bold-centrato-bg_gray_small'])
        sheet.merge_range(riga, 5, riga, 9, 'FIRMA CLIENTE', stili['bold-centrato-bg_gray_small'])
        riga += 1
        sheet.set_row(riga, 30)
        sheet.merge_range(riga, 0, riga, 4, '', stili['boxed'])
        sheet.merge_range(riga, 5, riga, 9, '', stili['boxed'])
        
        riga += 1
        pagebreaks.append(riga)

    # end for usato per creare le 3 copie

    footer1 = '&L&7Documento realizzato con un programma dello Studio Gamma Snc.\nwww.studiogammasnc.it'
    sheet.set_footer(footer1)

    sheet.set_h_pagebreaks(pagebreaks)
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=bolla " + bolla.codice + ".xlsx"
    return response


