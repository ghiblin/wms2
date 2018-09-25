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

from anagrafiche.stampe.xlsUtils import crea_stili

FORMATO_DATA_ITALIANO = '%d/%m/%Y'
FORMATO_DATA_ITALIANO_CORTO = '%d/%m/%y'

tipo_lavori = TipoLavoro.objects.all()

@csrf_exempt
def crea_xls_consuntivi(request):

    def scriviCliente(cliente):
        crea_xls_consuntivi.riga += 1
        sheet.set_row(crea_xls_consuntivi.riga, 25) # altezza riga
        nome_cliente = ""
        if cliente.is_owner:
            nome_cliente = "COMMESSE INTERNE"
        else:
            nome_cliente = "{} {}".format(cliente.codice, cliente.get_nome_completo())

        sheet.write(crea_xls_consuntivi.riga, 0, nome_cliente, stili['bold-15'])
        crea_xls_consuntivi.riga += 1

    def scriviCommessa(commessa):
        crea_xls_consuntivi.riga += 1
        sheet.write(crea_xls_consuntivi.riga, 0, "Commessa {} - aperta il {}".format(commessa.codice, datetime.strftime(commessa.data_apertura, "%d/%m/%Y")), stili['bold-10'])
        crea_xls_consuntivi.riga += 1
        sheet.write(crea_xls_consuntivi.riga, 0, commessa.prodotto, stili['10'])
        crea_xls_consuntivi.riga += 2


    def scriviIntestazioneTabella():
        sheet.write(crea_xls_consuntivi.riga, 0, 'Data', stili['bold-centrato-bg_gray-10'])
        sheet.write(crea_xls_consuntivi.riga, 1, 'Dipendente', stili['bold-centrato-bg_gray-10'])
        sheet.write(crea_xls_consuntivi.riga, 2, 'Tipo lavoro', stili['bold-centrato-bg_gray-10'])
        sheet.write(crea_xls_consuntivi.riga, 3, 'Ore', stili['bold-centrato-bg_gray-10'])
        sheet.write(crea_xls_consuntivi.riga, 4, 'Note', stili['bold-centrato-bg_gray-10'])
        crea_xls_consuntivi.riga += 1

    def scriviRigaTabella(con):
        sheet.set_row(crea_xls_consuntivi.riga, 30) # altezza riga
        sheet.write(crea_xls_consuntivi.riga, 0, datetime.strftime(con.data, FORMATO_DATA_ITALIANO_CORTO), stili['boxed-10'])
        sheet.write(crea_xls_consuntivi.riga, 1, con.dipendente.getNomeCompleto(), stili['boxed-10'])
        sheet.write(crea_xls_consuntivi.riga, 2, con.tipo_lavoro.descrizione, stili['boxed-10'])
        sheet.write(crea_xls_consuntivi.riga, 3, con.ore, stili['boxed-10'])
        sheet.write(crea_xls_consuntivi.riga, 4, con.note, stili['boxed-10'])
        #  sheet.write(crea_xls_consuntivi.riga, 5, con.commessa.codice, stili['boxed-10'])
        crea_xls_consuntivi.riga +=1

    def scriviTotale():
        for tipo in tipo_lavori:
            if totali_ore_per_tipo[tipo.id] > 0:
                sheet.set_row(crea_xls_consuntivi.riga, 30) # altezza riga
                sheet.write(crea_xls_consuntivi.riga, 2, 'Totale {}'.format(tipo.descrizione.lower()), stili['wrap-10'])
                sheet.write(crea_xls_consuntivi.riga, 3, totali_ore_per_tipo[tipo.id], stili['wrap-10'])
                crea_xls_consuntivi.riga +=1
            # dopo aver scritto il totale di un tipo lavoro, resettalo per la commessa successiva:
            totali_ore_per_tipo[tipo.id] = 0

        crea_xls_consuntivi.riga +=1
        sheet.write(crea_xls_consuntivi.riga, 2, 'Totale ore', stili['bold-10'])
        sheet.write(crea_xls_consuntivi.riga, 3, totale_ore, stili['bold-10'])
        crea_xls_consuntivi.riga +=2

    def resetta_totali_ore_per_tipo():
        for tipo in tipo_lavori:
            totali_ore_per_tipo[tipo.id] = 0


    ## http://stackoverflow.com/a/27405896/529323
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet()
    sheet.set_paper(9)  # A4
    #sheet.set_margins(0.24, 0.24, 0.47, 0.11)

    # larghezza colonne
    sheet.set_column('A:A', 9)
    sheet.set_column('B:B', 16)
    sheet.set_column('C:C', 20)
    sheet.set_column('D:D', 6)
    sheet.set_column('E:E', 32)
    stili = crea_stili(workbook)
    today = datetime.today()
    crea_xls_consuntivi.riga = 0

    u = request.user 
    if not u.has_perm('anagrafiche._consuntivo:*'):
        ctx = {}
        ctx['msg'] = 'Non hai i permessi per creare il report dei consuntivi.'
        return render(request, 'anagrafiche/msg.html', ctx)

    data_inizio = None
    data_fine = None
    data_inizio_str = request.GET.get('data_inizio')
    data_fine_str = request.GET.get('data_fine')

    if data_inizio_str:
        try:
            data_inizio = datetime.strptime(data_inizio_str, '%Y-%m-%d').date()
        except:
            data_inizio = None
            #result = result.filter(data__gte=data_da)

    if data_fine_str:
        try:
            data_fine = datetime.strptime(data_fine_str, '%Y-%m-%d').date()
        except:
            data_fine = None

    if not data_inizio and not data_fine:
        ctx = {}
        ctx['msg'] = 'Impossibile creare il report dei consuntivi. Parametri \'data inizio\' e \'data fine\' non validi. Premi il tasto \'indietro\' del browser.'
        return render(request, 'anagrafiche/msg.html', ctx)
    elif not data_inizio:
        ctx = {}
        ctx['msg'] = 'Impossibile creare il report dei consuntivi. Parametro \'data inizio\' non valido. Premi il tasto \'indietro\' del browser.'
        return render(request, 'anagrafiche/msg.html', ctx)
    elif not data_fine:
        ctx = {}
        ctx['msg'] = 'Impossibile creare il report dei consuntivi. Parametro \'data fine\' non valido. Premi il tasto \'indietro\' del browser.'
        return render(request, 'anagrafiche/msg.html', ctx)


    sheet.merge_range(crea_xls_consuntivi.riga, 0, crea_xls_consuntivi.riga, 4, 'REPORT CONSUNTIVI AL {}'.format(datetime.strftime(today, FORMATO_DATA_ITALIANO)), 
        stili['bold-centrato-bg_gray-10'])
    crea_xls_consuntivi.riga += 1


    consuntivi = Consuntivo.objects.non_cancellati().filter(data__gte=data_inizio, data__lte=data_fine) \
        .order_by('commessa__cliente__codice', 'commessa', 'data', 'dipendente__nome', 'tipo_lavoro__descrizione')

    cliente_attuale = None
    commessa_attuale = None

    totale_ore_gia_scritto = True
    totale_ore = 0
    totali_ore_per_tipo = {}       # crea l'oggetto
    resetta_totali_ore_per_tipo()  # assicurati che ci sia un indice per ogni tipo lavoro

    for con in consuntivi:
        if con.commessa.cliente != cliente_attuale:
            if not totale_ore_gia_scritto:
                scriviTotale()
                totale_ore_gia_scritto = True
            scriviCliente(con.commessa.cliente)

        if con.commessa != commessa_attuale:
            if not totale_ore_gia_scritto:
                scriviTotale()
                totale_ore_gia_scritto = True
            scriviCommessa(con.commessa)
            totale_ore = 0 # resetta il contatore delle ore per ogni commessa.
            resetta_totali_ore_per_tipo()
            scriviIntestazioneTabella()
            totale_ore_gia_scritto = False # dopo ogni inizio di tabella va scritta anche una fine

        scriviRigaTabella(con)
        totale_ore += con.ore
        totali_ore_per_tipo[con.tipo_lavoro.id] += con.ore
        cliente_attuale = con.commessa.cliente
        commessa_attuale = con.commessa


    # scrivi il totale dell'ultima tabella (senza scrivere nulla nel caso non ci siano consuntivi).
    if not totale_ore_gia_scritto:    
        scriviTotale()

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=consuntivi da " + data_inizio_str + " a " + data_fine_str + ".xlsx"
    return response
