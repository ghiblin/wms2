#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import json
import xlsxwriter
from datetime import date

from django.conf import settings
from anagrafiche.models import *
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from anagrafiche.stampe.xlsUtils import crea_stili

@csrf_exempt
def crea_xls_commessa(request, id_commessa):

    commessa = get_object_or_404(Commessa, pk=id_commessa)

    ## http://stackoverflow.com/a/27405896/529323
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet()
    sheet.set_paper(8)  # A3
    sheet.set_landscape()

    stili = crea_stili(workbook)

    riga = 0
    sheet.set_row(riga, 34)
    sheet.merge_range(riga, 11, riga, 20, 'MR FERRO S.R.L.', stili['big'])
    
    # la larghezza di default di una colonna è circa 8.
    sheet.set_column('A:A', 12)   # 8 + 4 
    sheet.set_column('M:M', 4)    # 8 - 4

    bandiera_params =  {
        'x_scale': 0.75,
        'y_scale': 0.75,
        'x_offset': 8, 
        'y_offset': 5
    }
    checkbox_params = {
        'x_scale': 0.7,
        'y_scale': 0.7,
        'x_offset': 0, 
        'y_offset': 1
    }
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/bandiera_italiana.jpg".format(settings.XLS_IMAGE_PATH), 
        bandiera_params)
    
    riga += 1
    mr_ferro = Entita.objects.proprietario()
    indirizzo = mr_ferro.get_indirizzo(SEDE_OPERATIVA, 'su_due_righe_con_cap')
    sheet.merge_range(riga, 11, riga, 20, indirizzo[0], stili['testo-centrato'])
    riga += 1
    sheet.merge_range(riga, 11, riga, 20, indirizzo[1], stili['testo-centrato'])

    riga += 2
    sheet.set_row(riga, 24)
    sheet.merge_range(riga, 11, riga, 17, 'SCHEDA DI COMMESSA', stili['medium_sinistra'])    

    #riga += 1
    sheet.write(riga, 18, 'DATA', stili['testo-centrato'])
    sheet.merge_range(riga, 19, riga, 20, 'FIRMA', stili['testo-centrato'])

    riga += 1
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      ORDINE DI LAVORAZIONE REGISTRATO DA OFFICINA', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      RIESAME TECNICO CONTRATTUALE', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      CONTROLLO VISIVO-DIMENSIONALE STRUTTURA', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      CONTROLLO IN PROCESS DELLE SALDATURE', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      RIESAME DI PROGETTO/REQUISITI PER SALDATURA', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      WPS APPLICABILE', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])
    riga += 1
    sheet.merge_range(riga, 11, riga, 20, '', \
        stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      DISEGNI/PROGETTO ESECUTIVO', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      CERTIFICATI MATERIALE', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      DOCUMENTI SICUREZZA (POS - DURC - ecc.)', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      SEQUENZA DI MONTAGGIO', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      ISTRUZIONI DI MONTAGGIO', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])


    riga += 1
    sheet.write(riga, 18, 'DATA ESEC.', stili['testo-centrato'])
    sheet.merge_range(riga, 19, riga, 20, 'FIRMA', stili['testo-centrato'])

    riga += 1
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      CONTROLLO DI SALDATURA INIZIALE', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.insert_image(riga, 11, "{}anagrafiche/static/img/checkbox.jpg".format(settings.XLS_IMAGE_PATH), 
        checkbox_params)
    sheet.merge_range(riga, 11, riga, 17, '      TIPO DI CONTROLLO []VT []PT []MT [] RT []UT []...', \
        stili['bordo_sotto'])
    sheet.write(riga, 18, '', stili['bordo_a_u'])
    sheet.merge_range(riga, 19, riga, 20, '', stili['bordo_sotto'])

    riga += 2
    sheet.merge_range(riga, 11, riga, 20, 'PRODOTTO', stili['bold-centrato'])
    riga += 1
    sheet.set_row(riga, 24)
    sheet.merge_range(riga, 11, riga, 20, commessa.prodotto, stili['bold-centrato-bg_pink'])
    
    riga += 1
    sheet.merge_range(riga, 11, riga, 20, 'COMMESSA', stili['bold-centrato'])
    riga += 1
    sheet.set_row(riga, 24)
    sheet.merge_range(riga, 11, riga, 20, commessa.codice, stili['bold-centrato-bg_pink'])
    
    riga += 1
    sheet.merge_range(riga, 11, riga, 20, 'COMMITTENTE', stili['bold-centrato'])
    riga += 1
    sheet.set_row(riga, 24)
    sheet.merge_range(riga, 11, riga, 20, commessa.cliente.get_nome_completo(), stili['bold-centrato-bg_pink'])
    
    riga += 1
    sheet.merge_range(riga, 11, riga, 20, 'DATA APERTURA', stili['bold-centrato'])
    riga += 1
    sheet.set_row(riga, 24)
    sheet.merge_range(riga, 11, riga, 20, commessa.data_apertura, stili['bold-centrato-bg_pink-data'])

    riga += 2
    sheet.merge_range(riga, 11, riga, 20, 'RIF. PROGETTO: ', stili['boxed'])
    riga += 1
    sheet.set_row(riga, 24)
    sheet.merge_range(riga, 11, riga, 20, 'RIF. PROGETTO: ', stili['boxed'])


    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=scheda commessa " \
        + commessa.codice + ".xlsx"
    return response
