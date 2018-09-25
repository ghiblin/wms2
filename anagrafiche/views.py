#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from datetime import datetime, date, timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.core.serializers.json import DjangoJSONEncoder

from anagrafiche.models import *
from anagrafiche.forms import *

INVALID_INPUT_STATUS_CODE = 400

def home(request):
    return render(request, 'anagrafiche/home.html', {})


def loginView(request):
    msg = ""
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                #return HttpResponse("Il tuo account è disabilitato.")
                msg = "Il tuo account è disabilitato."
        else:
            # Bad login details were provided. So we can't log the user in.
            #print "Invalid login details: {0}, {1}".format(username, password)
            msg ="Username e/o password non valida."

    ctx = {
        'messaggio': msg
    }
    return render(request, 'anagrafiche/login.html', ctx)


def logout_view(request):
    logout(request)
    return redirect('home')


def menu(request):
    return render(request, 'anagrafiche/menu.html', {})


def status(request):
    context = {}
    user = request.user
    context['permessi'] = user.get_all_permissions()
    context['permessi'] = sorted(context['permessi'])
    context['skip_permission_check'] = settings.SKIP_PERMISSION_CHECK

    return render(request, 'anagrafiche/status.html', context)

@login_required
def testSergio(request):
    """
    test sergio
    """
    context = {}
    return render(request, 'anagrafiche/testSergio.html', context)

# DA CANCELLARE
@login_required
def clienti(request):
    """
    Anagrafiche clienti.
    """
    ### Il modello Cliente è stato cancellato.
    context = {}
    return render(request, 'anagrafiche/clienti.html', context)


# DA CANCELLARE
def cliente(request, idCliente=None):
    """
    Creazione, modifica e dettagli di un cliente.
    JSON.
    """
    if request.method == 'GET':
        cliente = Cliente.objects.get(id=idCliente) 
        return HttpResponse(json.dumps(model_to_dict(cliente), cls=DjangoJSONEncoder), 
            content_type="application/json")
    else:
        idCliente = request.POST.get('id', None)
        if idCliente:
            # il campo 'id' della form non è vuoto, quindi sto facento una 
            # modifica invece che un inserimento
            instance = Cliente.objects.get(id=idCliente)
        else:
            # id vuoto, sto creando un nuovo record
            instance = None
        clienteForm = ClienteForm(request.POST, instance=instance)
        if clienteForm.is_valid():
            clienteForm.save()
            return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
                content_type="application/json")
        else:
            return HttpResponse(json.dumps("error", cls=DjangoJSONEncoder), 
                content_type="application/json", status=INVALID_INPUT_STATUS_CODE)


# DA CANCELLARE
def eliminaCliente(request, idCliente):
    """
    Marca un cliente come eliminato.
    JSON
    """
    cliente = Cliente.objects.get(id=idCliente) 
    cliente.cancellato = True
    cliente.save()
    return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
        content_type="application/json")


# DA CANCELLARE
@login_required
def contiCorrenti(request):
    """
    Anagrafica conti correnti
    """
    conti_correnti = ContoCorrente.objects.get_cc_proprietario_gestionale()
    context = {
        'conti_correnti': conti_correnti,
        'contoCorrenteForm': ContoCorrenteForm()
    }
    return render(request, 'anagrafiche/contiCorrenti.html', context)


# DA CANCELLARE
def contiCorrentiJSON(request):
    """
    Restituisce i cc esistenti in formato JSON.
    """
    1/0 # Fix me!
    commesse = Commessa.objects.tutti()
    result = []
    for c in commesse:
        result.append({
            'id': c.id,
            'codice': c.codice,
            'cliente_id': c.cliente.id,
            'data_apertura': c.data_apertura
        })

    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), \
        content_type="application/json")


# DA CANCELLARE
def contoCorrente(request, id_conto_corrente=None):
    """
    Creazione, modifica e dettagli di un conto corrente.
    JSON
    """
    if request.method == 'GET':
        conto_corrente = ContoCorrente.objects.get(id=id_conto_corrente) 
        return HttpResponse(json.dumps(model_to_dict(conto_corrente), cls=DjangoJSONEncoder), 
            content_type="application/json")
    else:
        id_conto_corrente = request.POST.get('id', None)
        if id_conto_corrente:
            # il campo 'id' della form non è vuoto, quindi sto facento una 
            # modifica invece che un inserimento
            instance = ContoCorrente.objects.get(id=id_conto_corrente)
        else:
            # id vuoto, sto creando un nuovo record
            instance = None
        conto_corrente_form = ContoCorrenteForm(request.POST, instance=instance)
        if conto_corrente_form.is_valid():

            # l'entita associata al cc non è passata nella form. quindi
            # disabilito il reset del campo predefinito:
            # ContoCorrente.objects.resetPredefinito(
            #    conto_corrente_form.cleaned_data['predefinito'])
            conto_corrente_form.save()
            return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
                content_type="application/json")
        else:
            return HttpResponse(json.dumps("error", cls=DjangoJSONEncoder), 
                content_type="application/json", status=INVALID_INPUT_STATUS_CODE)


# DA CANCELLARE
def eliminaContoCorrente(request, id_conto_corrente):
    """
    Marca un cc come eliminato.
    JSON
    """
    conto_corrente = ContoCorrente.objects.get(id=id_conto_corrente) 
    conto_corrente.cancellato = True
    conto_corrente.save()
    return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
        content_type="application/json")


@login_required
def commesse(request):
    """
    Anagrafica commesse
    """
    commesse = Commessa.objects.tutti()
    context = {
        'commesse': commesse,
        'commessaForm': CommessaForm(initial={'data_apertura': date.today()})
    }
    return render(request, 'anagrafiche/commesse.html', context)


def commesseJSON(request):
    """
    Restituisce le commesse esistenti in formato JSON.
    """
    commesse = Commessa.objects.tutti()
    result = []
    for c in commesse:
        result.append({
            'id': c.id,
            'codice': c.codice,
            'cliente_id': c.cliente.id,
            'data_apertura': c.data_apertura
        })

    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), \
        content_type="application/json")


def commessa(request, idCommessa=None):
    """
    Creazione, modifica e dettagli di una commessa.
    JSON
    """
    if request.method == 'GET':
        commessa = Commessa.objects.get(id=idCommessa) 
        return HttpResponse(json.dumps(model_to_dict(commessa), cls=DjangoJSONEncoder), 
            content_type="application/json")
    else:
        idCommessa = request.POST.get('id', None)
        if idCommessa:
            # il campo 'id' della form non è vuoto, quindi sto facento una 
            # modifica invece che un inserimento
            instance = Commessa.objects.get(id=idCommessa)
        else:
            # id vuoto, sto creando un nuovo record
            instance = None
        commessaForm = CommessaForm(request.POST, instance=instance)
        if commessaForm.is_valid():
            commessaForm.save()
            return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
                content_type="application/json")
        else:
            return HttpResponse(json.dumps("error", cls=DjangoJSONEncoder), 
                content_type="application/json", status=INVALID_INPUT_STATUS_CODE)


def eliminaCommessa(request, idCommessa):
    """
    Marca una commessa come eliminata.
    JSON
    """
    commessa = Commessa.objects.get(id=idCommessa) 
    commessa.cancellato = True
    commessa.save()
    return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
        content_type="application/json")


@login_required
def dipendenti(request):
    """
    Pagina con i dipendenti.
    """
    dipendenti = Dipendente.objects.tutti()
    context = {
        'dipendenti': dipendenti,
        'dipendenteForm': DipendenteForm()
    }
    return render(request, 'anagrafiche/dipendenti.html', context)


def dipendente(request, idDipendente=None):
    """
    Creazione, modifica e dettagli di un Dipendente. 
    Usa JSON.
    """
    if request.method == 'GET':
        dipendente = Dipendente.objects.get(id=idDipendente) 
        return HttpResponse(json.dumps(model_to_dict(dipendente), cls=DjangoJSONEncoder), 
            content_type="application/json")
    else:
        idDipendente = request.POST.get('id', None)
        if idDipendente:
            # il campo 'id' della form non è vuoto, quindi sto facento una 
            # modifica invece che un inserimento
            instance = Dipendente.objects.get(id=idDipendente)
        else:
            # id vuoto, sto creando un nuovo record
            instance = None
        dipendenteForm = DipendenteForm(request.POST, instance=instance)
        if dipendenteForm.is_valid():
            dipendenteForm.save()
            return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
                content_type="application/json")
        else:
            return HttpResponse(json.dumps("error", cls=DjangoJSONEncoder), 
                content_type="application/json", status=INVALID_INPUT_STATUS_CODE)


def eliminaDipendente(request, idDipendente):
    """
    Marca un dipendente come eliminato.
    JSON
    """
    dipendente = Dipendente.objects.get(id=idDipendente) 
    dipendente.cancellato = True
    dipendente.save()
    return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
        content_type="application/json")


def dipendentiEOre(request):
    """
    Restituisce l'elenco dei dipendenti con le ore lavorate nel periodo specificato.
    JSON.
    """
    consuntiviFilterForm = ConsuntiviFilterForm(request.GET)
    if consuntiviFilterForm.is_valid():
        da = consuntiviFilterForm.cleaned_data.get('da', None)
        a = consuntiviFilterForm.cleaned_data.get('a', None)
        as_list = False
        records = Dipendente.objects.get_dipendenti_e_ore(as_list, da, a)
        my_list = []
        for r in records:
            my_list.append({
                'id': r.id,
                'nome': r.nome,
                'cognome': r.cognome,
                'ore_totali': r.ore_totali or 0
                })
        return HttpResponse(json.dumps(my_list, cls=DjangoJSONEncoder), \
            content_type="application/json")
    else:
        return HttpResponse(json.dumps("error", cls=DjangoJSONEncoder), \
            content_type="application/json", status = INVALID_INPUT_STATUS_CODE)
    

@login_required
def consuntivi(request):
    """
    Elenco dei consuntivi.
    """
    data_da = datetime.today() - timedelta(1)
    data_a = datetime.today()
    as_list = False
    dipendenti = Dipendente.objects.get_dipendenti_e_ore(as_list, data_da, data_a)
    filterForm = ConsuntiviFilterForm()
    consuntivoForm = ConsuntivoForm()

    context = {
        'filterForm': filterForm,
        'dipendenti': dipendenti,
        'consuntivoForm': consuntivoForm,
        'data_da': datetime.strftime(data_da, "%Y-%m-%d"),
        'data_a': datetime.strftime(data_a, "%Y-%m-%d")
    }
    return render(request, 'anagrafiche/consuntivi.html', context)


def consuntiviDipendente(request, idDipendente):
    """
    Elenco dei consuntivi di un dipendente.
    JSON
    """
    my_dict = {}
    my_dict['dipendente'] = idDipendente
    my_dict['da'] = request.GET.get('da', None)
    my_dict['a'] = request.GET.get('a', None)
    consuntivi = Consuntivo.objects.filtraConsuntivi(**my_dict)
    my_list = []
    for c in consuntivi:
        my_list.append({
            'id': c.id,
            'data': c.data,
            'ore': c.ore,
            'idCommessa': c.commessa.id,
            'commessa': c.commessa.codice,
            'idTipoLavoro': c.tipo_lavoro.id,
            'tipoLavoro': c.tipo_lavoro.descrizione,
            'importo': round(c.ore * c.dipendente.costo_orario, 2)
        })
    totali = Consuntivo.objects.getTotaliDipendente(**my_dict)

    risultato = {
        'consuntivi': my_list,
        'totali': totali
    }
    return HttpResponse(json.dumps(risultato, cls=DjangoJSONEncoder), 
        content_type="application/json")


def consuntivo(request, idConsuntivo=None):
    """
    Creazione, modifica e dettagli di un consuntivo.
    JSON
    """
    if request.method == 'GET':
        consuntivo = Consuntivo.objects.get(id=idConsuntivo) 
        return HttpResponse(json.dumps(model_to_dict(consuntivo), cls=DjangoJSONEncoder), 
            content_type="application/json")
    else:
        idConsuntivo = request.POST.get('id', None)
        if idConsuntivo:
            # il campo 'id' della form non è vuoto, quindi sto facento una 
            # modifica invece che un inserimento
            instance = Consuntivo.objects.get(id=idConsuntivo)
        else:
            # id vuoto, sto creando un nuovo record
            instance = None
        consuntivoForm = ConsuntivoForm(request.POST, instance=instance)
        if consuntivoForm.is_valid():
            consuntivoForm.save()
            return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
                content_type="application/json")
        else:
            return HttpResponse(json.dumps("error", cls=DjangoJSONEncoder), 
                content_type="application/json", status=INVALID_INPUT_STATUS_CODE)


def eliminaConsuntivo(request, idConsuntivo):
    """
    Marca un consuntivo come eliminato.
    JSON
    """
    consuntivo = Consuntivo.objects.get(id=idConsuntivo) 
    consuntivo.cancellato = True
    consuntivo.save()
    return HttpResponse(json.dumps("ok", cls=DjangoJSONEncoder), 
        content_type="application/json")


@login_required
def costiCommessa(request):
    """
    Pagina con l'elenco delle commesse per mostrare i costi di una 
    commessa.
    """
    filterForm = CostiCommessaFilter(request.GET)
    
    if filterForm.is_valid():
        commesse = Commessa.objects.filtraCommesse(**filterForm.cleaned_data)
    else:
        commesse = Commessa.objects.tutti()

    context = {
        'filterForm': filterForm,
        'commesse': commesse
    }
    return render(request, 'anagrafiche/costiCommessa.html', context)



def costiCommessaSpecifica(request, idCommessa):
    """
    Restituisce i costi associati (per es. i consuntivi) ad una commessa.
    JSON
    """   
    # consuntivi = Consuntivo.objects.filter(commessa=idCommessa) \
    #    .values_list('id', 'data', 'ore', 'dipendente', 'tipo_lavoro')
    # return HttpResponse(json.dumps(list(consuntivi), cls=DjangoJSONEncoder), 
    #    content_type="application/json")

    consuntivi = Consuntivo.objects.getByCommessa(idCommessa)
    my_list = []
    totale_ore = 0
    totale_importi = 0
    for c in consuntivi:
        importo = round(c.ore * c.dipendente.costo_orario, 2)
        totale_ore += c.ore
        totale_importi += importo
        my_list.append({
            'id': c.id,
            'data': c.data,
            'ore': c.ore,
            'nomeDipendente': c.dipendente.getNomeCompleto(),
            'tipoLavoro': c.tipo_lavoro.descrizione,
            'importo': importo
            })
    risultato = {
        'consuntivi': my_list,
        'totali': {
            'totale_ore': totale_ore,
            'totale_importi': totale_importi
        }
    }
    return HttpResponse(json.dumps(risultato, cls=DjangoJSONEncoder), 
        content_type="application/json")
    


def tipiLavoroJSON(request):
    """
    Restituisce i tipi di lavoro in formato JSON.
    """
    tipi_lavoro = TipoLavoro.objects.tutti()
    result = []
    for tl in tipi_lavoro:
        result.append({
            'id': tl.id,
            'descrizione': tl.descrizione
        })
    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), \
        content_type="application/json")
