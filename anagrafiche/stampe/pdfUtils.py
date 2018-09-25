#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import json
import xlsxwriter
from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
#from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

#from django.views.decorators.csrf import csrf_exempt


from anagrafiche.models import *

GRAY_10 = 'E6E6E6'

@login_required
def crea_pdf_preventivo_cliente(request, id_preventivo):
    """
    Crea una pagina html che rappresenta un Preventivo clienti e che 
    può essere facilmente stampata.
    """
    preventivo = get_object_or_404(PreventivoCliente, pk=id_preventivo)
    righe = preventivo.righe.filter(cancellato=False)
    
    context = {
        'preventivo': preventivo,
        'righe': righe,
        'telefono_ufficio': '02 90422176',
        'fax_ufficio': '02 900123456',
        'email_ufficio': 'info@prova.it',
    }
    return render(request, 'anagrafiche/pdf/preventivoCliente.html', context)