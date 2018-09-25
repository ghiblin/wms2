#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging

from datetime import date
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout

from rest_framework import permissions, viewsets, status, filters, views
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from anagrafiche.models import *
from .apiPermissions import * #IsAuthorOfPost
from .apiSerializers import * #PostSerializer
from .apiFilters import *
from .apiViews import *
from django.core.files.base import ContentFile

logger = logging.getLogger('django')

class FornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Entita.objects.fornitori()
    serializer_class = FornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('vettore',)

    def get_permissions(self):
        # in questo caso 'baro' perché non passo il modello Entita ma la 
        # stringa 'fornitore'. In questo modo posso distinguere i permessi
        # per fornitori e clienti anche se il modello è unico.
        return (MyCustomPerm('fornitore', self.action) ,)

    def perform_destroy(self, serializer):
        # cancellazione logica, non fisica
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # perform_create is called before the model of this view is saved.
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello
        next_codice = Entita.objects.next_codice(FORNITORE_PREFIX)
        instance = serializer.save(codice=next_codice, is_supplier=True)
        return super(FornitoreViewSet, self).perform_create(serializer)

    @list_route()
    def get_tipo(self, request):
        # Perché non si può usare url_path nel decoratore per indicare
        # un altro url da assegnare all'api:
        # https://github.com/chibisov/drf-extensions/pull/73
        my_dict = [{'id':k, 'descrizione': v} for (k,v) in TIPO_PERSONA_CHOICES]
        return Response(my_dict, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def anche_cliente(self, request, pk=None):
        """
        Modifica un fornitore per farlo diventare anche un cliente.
        """
        fornitore = get_object_or_404(Entita, pk=pk)
        fornitore.is_client = True
        fornitore.save()
        serializer = ClienteSerializer(fornitore)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PreventivoFornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = PreventivoFornitore.objects.non_cancellati()
    serializer_class = PreventivoFornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = PreventivoFornitoreFilter

    def get_permissions(self):
        return (MyCustomPerm('preventivoFornitore', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = PreventivoFornitore.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(PreventivoFornitoreViewSet, self).perform_create(serializer)

    """
    def list(self, request):
        kwargs = {}
        preventivo_id = request.GET.get('preventivo_id', None)
        cliente_id = request.GET.get('cliente_id', None)
        accettato = request.GET.get('accettato', None)
        
        if cliente_id:
            kwargs['cliente__id'] = cliente_id
        if preventivo_id:
            kwargs['id'] = preventivo_id
        if accettato:
            accettato = accettato in ['true', '1', 'True']
            kwargs['accettato'] = accettato
        queryset = self.queryset.filter(**kwargs)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    """

    @detail_route(methods=['post'])
    def duplica(self, request, pk=None):
        """
        Serve ad duplicare un preventivo fornitore con tutte le sue righe e dettagli.
        """
        preventivo_da_clonare = get_object_or_404(PreventivoFornitore, pk=pk)
        
        #print("preventivo vecchio: id={}, codice={}, data={}".format(preventivo_da_clonare.id, preventivo_da_clonare.codice, preventivo_da_clonare.data))
        #for r in preventivo_da_clonare.righe.all():
        #    print("riga vecchia: id={}, quantità={}, articolo={}, descrizione={}, cancellato={}".format(r.id, r.quantita, r.articolo, r.articolo_descrizione, r.cancellato))

        preventivo_nuovo = get_object_or_404(PreventivoFornitore, pk=pk)
        # resettando l'id e salvando si crea un altro record che ha gli stessi campi...
        preventivo_nuovo.id = None
        preventivo_nuovo.save()
        preventivo_nuovo.data = date.today()
        preventivo_nuovo.codice = PreventivoFornitore.objects.next_codice()
        preventivo_nuovo.accettato = False
        preventivo_nuovo.save()
        
        #print("preventivo nuovo: id={}, codice={}".format(preventivo_nuovo.id, preventivo_nuovo.codice))
        #print("preventivo nuovo: data={}".format(preventivo_nuovo.data))
        for r in preventivo_da_clonare.righe.non_cancellati():
            rn = RigaPreventivoFornitore()
            rn.preventivo = preventivo_nuovo
            rn.articolo = r.articolo
            rn.articolo_descrizione = r.articolo_descrizione
            rn.articolo_prezzo = r.articolo_prezzo
            rn.sconto_percentuale = r.sconto_percentuale
            rn.articolo_unita_di_misura = r.articolo_unita_di_misura
            rn.accettata = False
            rn.quantita = r.quantita
            rn.totale = r.totale
            rn.note = r.note
            rn.save()
        preventivo_nuovo.aggiorna_totale()

        #for r in preventivo_nuovo.righe.all():
        #    print("riga nuova: id={}, quantità={}, articolo={}, descrizione={}".format(r.id, r.quantita, r.articolo, r.articolo_descrizione))

        serializer = PreventivoFornitoreSerializer(preventivo_nuovo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RigaPreventivoFornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = RigaPreventivoFornitore.objects.non_cancellati()
    serializer_class = RigaPreventivoFornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('preventivo',)

    def get_permissions(self):
        return (MyCustomPerm('rigaPreventivoFornitore', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()
        serializer.preventivo.aggiorna_totale()
    
    def perform_create(self, serializer):
        # perform_create is called before the model of this view is saved.
        # Ricordarsi di settare il campo 'totale' come read_only
        # nel serializer del modello 
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        instance = serializer.save(totale=totale)
        instance.preventivo.aggiorna_totale()
        return super(RigaPreventivoFornitoreViewSet, self).perform_create(serializer)
    
    def perform_update(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        instance = serializer.save(totale=totale)
        instance.preventivo.aggiorna_totale()
        return super(RigaPreventivoFornitoreViewSet, self).perform_update(serializer)


class OrdineFornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = OrdineFornitore.objects.non_cancellati()
    serializer_class = OrdineFornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = OrdineFornitoreFilter

    def get_permissions(self):
        return (MyCustomPerm('ordineFornitore', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = OrdineFornitore.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(OrdineFornitoreViewSet, self).perform_create(serializer)
 
    ## da rivedere
    @detail_route(methods=['post'])
    def crea_righe_da_preventivo(self, request, pk=None):
        """
        Serve ad aggiungere righe ordine ad un ordine già esistente selezionando
        le righe di un preventivo.
        """
        preventivi_da_aggiornare = set()
        ordine = get_object_or_404(OrdineFornitore, pk=pk)
        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_preventivo_fornitore[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe preventivo non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)

        for id_riga_preventivo in lista_righe:
            riga_preventivo = get_object_or_404(RigaPreventivoFornitore, 
                pk=id_riga_preventivo)            
            if riga_preventivo.preventivo.cancellato:
                return Response({"error": "Il preventivo è stato cancellato."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.preventivo.fornitore != ordine.fornitore:
                return Response({"error": "Il fornitore del preventivo è diverso dal fornitore dell'ordine."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.accettata:
                return Response({"error": ("La riga preventivo con id {}" +
                        " fa già parte di un altro ordine.").format(
                        riga_preventivo.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)

        lista_righe_create = []
        totale_righe_create = 0
        for id_riga_preventivo in lista_righe:
            riga_preventivo = get_object_or_404(RigaPreventivoFornitore, 
                pk=id_riga_preventivo)

            riga_ordine = RigaOrdineFornitore()
            riga_ordine.ordine = ordine
            riga_ordine.preventivo = riga_preventivo.preventivo
            riga_ordine.riga_preventivo = riga_preventivo
            # commessa ?
            riga_ordine.articolo = riga_preventivo.articolo
            riga_ordine.articolo_codice_fornitore = riga_preventivo.articolo_codice_fornitore
            riga_ordine.articolo_descrizione = riga_preventivo.articolo_descrizione
            riga_ordine.articolo_prezzo = riga_preventivo.articolo_prezzo
            riga_ordine.sconto_percentuale = riga_preventivo.sconto_percentuale
            riga_ordine.articolo_unita_di_misura = riga_preventivo.articolo_unita_di_misura
            riga_ordine.quantita = riga_preventivo.quantita
            riga_ordine.data_consegna = riga_preventivo.data_consegna
            riga_ordine.totale = riga_preventivo.totale
            totale_righe_create += riga_ordine.totale
            riga_ordine.note = riga_preventivo.note
            riga_ordine.save()
            lista_righe_create.append(riga_ordine)

            riga_preventivo.accettata=True
            riga_preventivo.save()

            preventivi_da_aggiornare.add(riga_preventivo.preventivo)

        ordine.totale += totale_righe_create
        ordine.save()

        for preventivo in preventivi_da_aggiornare:
            preventivo.aggiorna_stato()

        serializer = RigaOrdineFornitoreSerializer(lista_righe_create, 
            many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def crea_ordine_da_righe_preventivo(self, request):
        preventivi_da_aggiornare = set()

        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_preventivo_fornitore[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe preventivo non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)
        id_commessa = request.POST.get('commessa', None)
        if not id_commessa:
            return Response({"error": "Commessa non specificata."}, 
                status=status.HTTP_400_BAD_REQUEST)
        # uso filter invece di get:
        commessa = Commessa.objects.filter(pk=id_commessa)
        if commessa:
            commessa = commessa[0]
        else:
            return Response({"error": "La commessa specificata non esiste."}, 
                status=status.HTTP_400_BAD_REQUEST)
        if commessa.cancellato:
            return Response({"error": "La commessa specificata non è valida."}, 
                status=status.HTTP_400_BAD_REQUEST)
        

        fornitore_preventivo = None
        for id_riga_preventivo in lista_righe:
            riga_preventivo = get_object_or_404(RigaPreventivoFornitore, 
                pk=id_riga_preventivo)
            # utilizzo la prima riga preventivo ricevuta per estrarre dei 
            # dati che utilizzo nella creazione dell'ordine
            if fornitore_preventivo == None:
                fornitore_preventivo = riga_preventivo.preventivo.fornitore
                oggetto_preventivo = riga_preventivo.preventivo.oggetto
                pagamento_preventivo = riga_preventivo.preventivo.pagamento
                persona_di_riferimento_preventivo = riga_preventivo.preventivo.persona_di_riferimento
                destinazione_preventivo = riga_preventivo.preventivo.destinazione
                aliquota_IVA_preventivo = riga_preventivo.preventivo.aliquota_IVA
            
            if (riga_preventivo.preventivo.commessa is not None) \
                    and riga_preventivo.preventivo.commessa != commessa:
                # non si può usare lo stesso preventivo per ordini diversi a meno che
                # la commessa associata agli ordini sia sempre la stessa
                return Response({"error": "Non si può usare lo stesso preventivo per commesse diverse."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.preventivo.fornitore != fornitore_preventivo:
                return Response({"error": "Righe preventivo appartengono a preventivi di diversi fornitori."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.preventivo.cancellato:
                return Response({"error": ("La riga preventivo con id {}" +
                        " fa parte di un preventivo cancellato.").format(
                        riga_preventivo.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.accettata:
                return Response({"error": ("La riga preventivo con id {}" +
                        " fa già parte di un altro ordine.").format(
                        riga_preventivo.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)

        ordine = OrdineFornitore()
        ordine.data = date.today()
        # ordine.data_ordine_fornitore =... non metto niente, credo che vada riempita a mano.
        ordine.codice = OrdineFornitore.objects.next_codice()
        # ordine.codice_ordine_fornitore = ... non metto niente, credo che vada riempito a mano.
        ordine.fornitore = fornitore_preventivo
        ordine.commessa = commessa
        ordine.oggetto = oggetto_preventivo
        ordine.pagamento = pagamento_preventivo
        ordine.persona_di_riferimento = persona_di_riferimento_preventivo
        ordine.destinazione = destinazione_preventivo
        ordine.aliquota_IVA = aliquota_IVA_preventivo
        ordine.save()

        totale_righe_create = 0
        for id_riga_preventivo in lista_righe:
            riga_preventivo = get_object_or_404(RigaPreventivoFornitore, 
                pk=id_riga_preventivo)
            riga_ordine = RigaOrdineFornitore()
            riga_ordine.ordine = ordine
            riga_ordine.preventivo = riga_preventivo.preventivo
            riga_ordine.riga_preventivo = riga_preventivo
            # commessa ?
            riga_ordine.articolo = riga_preventivo.articolo
            riga_ordine.articolo_codice_fornitore = riga_preventivo.articolo_codice_fornitore
            riga_ordine.articolo_descrizione = riga_preventivo.articolo_descrizione
            riga_ordine.articolo_prezzo = riga_preventivo.articolo_prezzo
            riga_ordine.sconto_percentuale = riga_preventivo.sconto_percentuale
            riga_ordine.articolo_unita_di_misura = riga_preventivo.articolo_unita_di_misura
            riga_ordine.quantita = riga_preventivo.quantita
            riga_ordine.data_consegna = riga_preventivo.data_consegna
            riga_ordine.totale = riga_preventivo.totale
            totale_righe_create += riga_ordine.totale
            riga_ordine.note = riga_preventivo.note
            riga_ordine.save()
            preventivi_da_aggiornare.add(riga_preventivo.preventivo)

            riga_preventivo.accettata = True
            riga_preventivo.save()

        # probabilmente basta l'uguale perché l'ordine viene creato da 0 ed il
        # totale inizialmente è 0:
        ordine.totale += totale_righe_create
        ordine.save()

        for preventivo in preventivi_da_aggiornare:
            preventivo.aggiorna_stato()
            preventivo.imposta_commessa(commessa)

        serializer = OrdineFornitoreSerializer(ordine)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RigaOrdineFornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = RigaOrdineFornitore.objects.non_cancellati()
    serializer_class = RigaOrdineFornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # rispetto a RigaOrdineCliente sono stati tolti i campi 'commessa' e 'preventivo'
    # che erano superflui
    filter_fields = ('ordine', 'articolo',  ) 

    def get_permissions(self):
        return (MyCustomPerm('rigaOrdineFornitore', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()
        serializer.ordine.aggiorna_totale()
    
    def perform_create(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        #commessa = serializer.validated_data['ordine'].commessa
        #instance = serializer.save(totale=totale, commessa=commessa)
        instance = serializer.save(totale=totale)
        instance.ordine.aggiorna_totale()
        return super(RigaOrdineFornitoreViewSet, self).perform_create(serializer)
    
    def perform_update(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        instance = serializer.save(totale=totale)
        instance.ordine.aggiorna_totale()
        return super(RigaOrdineFornitoreViewSet, self).perform_update(serializer)



class BollaFornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = BollaFornitore.objects.non_cancellati()
    serializer_class = BollaFornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = BollaFornitoreFilter

    def get_permissions(self):
        return (MyCustomPerm('bollaFornitore', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = BollaFornitore.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(BollaFornitoreViewSet, self).perform_create(serializer)
    
    @detail_route(methods=['post'])
    def crea_righe_da_ordine(self, request, pk=None):
        """
        Serve ad aggiungere delle righe ad una bolla già esistente.
        """
        ordini_da_aggiornare = set()
        bolla = get_object_or_404(BollaFornitore, pk=pk)
        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_ordine_fornitore[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe ordine non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)

        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineFornitore, 
                pk=id_riga_ordine)
            if riga_ordine.ordine.cancellato:
                return Response({"error": "L'ordine è stato cancellato."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.ordine.fornitore != bolla.fornitore:
                return Response({"error": "Il fornitore dell'ordine è diverso dal fornitore della bolla."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.bollettata:
                return Response({"error": ("La riga ordine con id {}" +
                        " fa già parte di un'altra bolla.").format(
                        riga_ordine.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)


        carico = TipoMovimento.objects.get_carico()
        magazzino = Commessa.objects.get_magazzino()
        
        lista_righe_create = []
        #totale_righe_create = 0
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineFornitore, 
                pk=id_riga_ordine)

            riga_bolla = RigaBollaFornitore()
            riga_bolla.bolla = bolla
            ###### l'ordine non lo salvo più perché ho già la riga_ordine:
            # riga_bolla.ordine = riga_ordine.ordine 
            riga_bolla.riga_ordine = riga_ordine
            # commessa ? è già settata nella bolla
            riga_bolla.articolo = riga_ordine.articolo
            riga_bolla.articolo_codice_fornitore = riga_ordine.articolo_codice_fornitore
            riga_bolla.articolo_descrizione = riga_ordine.articolo_descrizione
            #riga_bolla.articolo_prezzo = riga_ordine.articolo_prezzo
            riga_bolla.articolo_unita_di_misura = riga_ordine.articolo_unita_di_misura
            riga_bolla.quantita = riga_ordine.quantita
            #riga_bolla.totale = riga_ordine.totale
            #totale_righe_create += riga_bolla.totale
            riga_bolla.note = riga_ordine.note
            riga_bolla.save()
            lista_righe_create.append(riga_bolla)

            riga_ordine.bollettata=True
            riga_ordine.save()

            movimento = Movimento()
            movimento.lotto = bolla
            movimento.articolo = riga_ordine.articolo
            movimento.tipo_movimento = carico
            movimento.autore = request.user
            movimento.quantita = riga_ordine.quantita
            movimento.unita_di_misura = riga_ordine.articolo_unita_di_misura
            movimento.destinazione = magazzino
            movimento.save()
            riga_bolla.carico = movimento
            riga_bolla.save()

            ordini_da_aggiornare.add(riga_ordine.ordine)

        #bolla.totale += totale_righe_create
        #bolla.save()

        for ordine in ordini_da_aggiornare:
            ordine.aggiorna_stato()

        serializer = RigaBollaFornitoreSerializer(lista_righe_create, 
            many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def crea_bolla_da_righe_ordine(self, request):
        ordini_da_aggiornare = set()

        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_ordine_fornitore[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe ordine non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)

        fornitore_ordine = None
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineFornitore, 
                pk=id_riga_ordine)
            # utilizzo la prima riga ordine ricevuta per estrarre dei 
            # dati che utilizzo nella creazione della bolla
            if fornitore_ordine == None:
                commessa_bolla = riga_ordine.ordine.commessa
                fornitore_ordine = riga_ordine.ordine.fornitore
                destinazione_ordine = riga_ordine.ordine.destinazione
                persona_di_riferimento_ordine = riga_ordine.ordine.persona_di_riferimento
                note_ordine = riga_ordine.ordine.note
            if riga_ordine.ordine.commessa != commessa_bolla:
                return Response({"error": "Righe ordine appartengono a ordini con commessa diversa."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            
            if riga_ordine.bollettata:
                return Response({"error": ("La riga ordine con id {}" +
                        " fa già parte di un'altra bolla.").format(
                        riga_ordine.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            
        bolla = BollaFornitore()
        bolla.data = date.today()
        # bolla.data_bolla_fornitore =... non metto niente, credo che vada riempita a mano.
        bolla.codice = BollaFornitore.objects.next_codice()
        #bolla.codice_bolla_fornitore = ... non metto niente, credo che vada riempito a mano.
        bolla.fornitore = fornitore_ordine
        bolla.commessa = commessa_bolla
        bolla.destinazione = destinazione_ordine
        bolla.persona_di_riferimento = persona_di_riferimento_ordine
        bolla.note = note_ordine
        bolla.causale_trasporto_id = BollaFornitore.objects.get_default_causale_trasporto()
        bolla.trasporto_a_cura_id = BollaFornitore.objects.get_default_trasporto_a_cura_di()
        bolla.save()

        carico = TipoMovimento.objects.get_carico()
        magazzino = Commessa.objects.get_magazzino()

        totale_righe_create = 0
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineFornitore, 
                pk=id_riga_ordine)
            riga_bolla = RigaBollaFornitore()
            riga_bolla.bolla = bolla
            riga_bolla.riga_ordine = riga_ordine
            # commessa ? è memorizzata nella bolla
            riga_bolla.articolo = riga_ordine.articolo
            riga_bolla.articolo_codice_fornitore = riga_ordine.articolo_codice_fornitore
            riga_bolla.articolo_descrizione = riga_ordine.articolo_descrizione
            #riga_bolla.articolo_prezzo = riga_ordine.articolo_prezzo
            riga_bolla.articolo_unita_di_misura = riga_ordine.articolo_unita_di_misura
            riga_bolla.quantita = riga_ordine.quantita
            # riga_bolla.data_consegna ???????????
            #riga_bolla.totale = riga_ordine.totale
            #totale_righe_create += riga_bolla.totale
            riga_bolla.note = riga_ordine.note
            riga_bolla.save()
            ordini_da_aggiornare.add(riga_ordine.ordine)

            riga_ordine.bollettata = True
            riga_ordine.save()

            movimento = Movimento()
            movimento.lotto = bolla
            movimento.articolo = riga_ordine.articolo
            movimento.tipo_movimento = carico
            movimento.autore = request.user
            movimento.quantita = riga_ordine.quantita
            movimento.unita_di_misura = riga_ordine.articolo_unita_di_misura
            movimento.destinazione = magazzino
            movimento.save()
            riga_bolla.carico = movimento
            riga_bolla.save()


        #bolla.totale += totale_righe_create
        #bolla.save()

        # settare l'ordine come bollettato?
        for ordine in ordini_da_aggiornare:
            ordine.aggiorna_stato()

        serializer = BollaFornitoreSerializer(bolla)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RigaBollaFornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = RigaBollaFornitore.objects.non_cancellati()
    serializer_class = RigaBollaFornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('bolla', 'articolo')

    def get_permissions(self):
        return (MyCustomPerm('rigaBollaFornitore', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()
        #serializer.bolla.aggiorna_totale()
    
    def perform_create(self, serializer):
        # ricordarsi di settare il campo 'carico' come readonly nel serializer
        # Creo un movimento relativo a questa riga bolla:
        carico = Movimento()
        carico.articolo = serializer.validated_data['articolo']
        carico.lotto = serializer.validated_data['bolla']
        carico.tipo_movimento = TipoMovimento.objects.get_carico()
        carico.autore = self.request.user
        carico.quantita = serializer.validated_data['quantita']
        carico.unita_di_misura = serializer.validated_data['articolo'].unita_di_misura
        carico.destinazione = Commessa.objects.get_magazzino()
        carico.save()
        instance = serializer.save(carico=carico)
        return super(RigaBollaFornitoreViewSet, self).perform_create(serializer)
    
    ### L'aggiornamento dei movimenti quando si modifica una riga bolla è fatto attraverso
    ### il segnale pre_save sulle righe bolle.

    # visto che nella bolla non c'è il prezzo non si deve aggiornare il totale quando
    # si crea, modifica o cancella una riga.


class FatturaFornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = FatturaFornitore.objects.non_cancellati()
    serializer_class = FatturaFornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = FatturaFornitoreFilter

    def get_permissions(self):
        return (MyCustomPerm('fatturaFornitore', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = FatturaFornitore.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(FatturaFornitoreViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        # ogni volta che si modifica una fattura, si resetta il flag 
        # 'da_confermare' a False
        instance = serializer.save(da_confermare=False)
        return super(FatturaFornitoreViewSet, self).perform_update(serializer)        

    
    @detail_route(methods=['post'])
    def crea_righe_da_ordine(self, request, pk=None):
        """
        Serve ad aggiungere delle righe ad una fattura già esistente.
        """
        ordini_da_aggiornare = set()
        fattura = get_object_or_404(FatturaFornitore, pk=pk)
        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_ordine_fornitore[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe ordine non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)

        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineFornitore, 
                pk=id_riga_ordine)
            if riga_ordine.ordine.cancellato:
                return Response({"error": 
                    "L'ordine {} è stato cancellato.".format(riga_ordine.ordine.codice)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.ordine.commessa != fattura.commessa:
                return Response({"error": "La commessa dell'ordine è diversa dalla commessa della fattura."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.fatturata:
                return Response({"error": ("La riga ordine con id {}" +
                        " fa già parte di un'altra fattura.").format(
                        riga_ordine.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.bollettata:
                return Response({"error": ("La riga ordine con id {}" +
                        " fa parte di una bolla.").format(
                        riga_ordine.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)

        lista_righe_create = []
        totale_righe_create = 0
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineFornitore, 
                pk=id_riga_ordine)

            riga_fattura = RigaFatturaFornitore()
            riga_fattura.fattura = fattura
            # riga_fattura.ordine = riga_ordine.ordine
            # l'ordine non lo salvo più perché ho già la riga_ordine
            riga_fattura.riga_ordine = riga_ordine
            # commessa ? è già settata nella fattura
            riga_fattura.articolo = riga_ordine.articolo
            riga_fattura.articolo_codice_fornitore = riga_ordine.articolo_codice_fornitore
            riga_fattura.articolo_descrizione = riga_ordine.articolo_descrizione
            riga_fattura.articolo_prezzo = riga_ordine.articolo_prezzo
            riga_fattura.sconto_percentuale = riga_ordine.sconto_percentuale
            riga_fattura.articolo_unita_di_misura = riga_ordine.articolo_unita_di_misura
            riga_fattura.quantita = riga_ordine.quantita
            riga_fattura.totale = riga_ordine.totale
            totale_righe_create += riga_fattura.totale
            riga_fattura.note = riga_ordine.note
            riga_fattura.save()
            lista_righe_create.append(riga_fattura)

            riga_ordine.fatturata=True
            riga_ordine.save()

            ordini_da_aggiornare.add(riga_ordine.ordine)

        fattura.totale += totale_righe_create
        fattura.save()

        for ordine in ordini_da_aggiornare:
            ordine.aggiorna_campo_fatturato()

        serializer = RigaFatturaFornitoreSerializer(lista_righe_create, 
            many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def crea_fattura_da_righe_ordine(self, request):
        ordini_da_aggiornare = set()

        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_ordine_fornitore[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe ordine non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)

        fornitore_ordine = None
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineFornitore, 
                pk=id_riga_ordine)
            # Utilizzo la prima riga ordine ricevuta per estrarre dei 
            # dati che utilizzo nella creazione della fattura.
            if fornitore_ordine == None:
                commessa_ordine = riga_ordine.ordine.commessa
                fornitore_ordine = riga_ordine.ordine.fornitore
                oggetto_ordine = riga_ordine.ordine.oggetto
                pagamento_ordine = riga_ordine.ordine.pagamento
                sconto_euro_ordine = riga_ordine.ordine.sconto_euro
                sconto_percentuale_ordine = riga_ordine.ordine.sconto_percentuale
                destinazione_ordine = riga_ordine.ordine.destinazione
                persona_di_riferimento_ordine = riga_ordine.ordine.persona_di_riferimento
                aliquota_IVA_ordine = riga_ordine.ordine.aliquota_IVA
                note_ordine = riga_ordine.ordine.note
            if not aliquota_IVA_ordine:
                return Response({"error": "Devi impostare l'aliquota IVA dell'ordine prima di creare la fattura."},
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.ordine.cancellato:
                return Response({"error": 
                    "L'ordine {} è stato cancellato.".format(riga_ordine.ordine.codice)},
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.ordine.commessa != commessa_ordine:
                return Response({"error": "Righe ordine appartengono a ordini con commessa diversa."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.fatturata:
                return Response({"error": ("La riga ordine con id {}" +
                        " fa già parte di un'altra fattura.").format(
                        riga_ordine.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.bollettata:
                return Response({"error": ("La riga ordine con id {}" +
                        " fa parte di una bolla.").format(
                        riga_ordine.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            
        fattura = FatturaFornitore()
        fattura.data = date.today()
        # fattura.data_fattura_fornitore = .... da compilare a mano
        fattura.codice = FatturaFornitore.objects.next_codice()
        # fattura.codice_fattura_fornitore = ... da compilare a mano
        fattura.fornitore = fornitore_ordine
        fattura.commessa = commessa_ordine
        fattura.oggetto = oggetto_ordine
        fattura.pagamento = pagamento_ordine
        fattura.sconto_euro = sconto_euro_ordine
        fattura.sconto_percentuale = sconto_percentuale_ordine
        fattura.destinazione = destinazione_ordine
        fattura.persona_di_riferimento = persona_di_riferimento_ordine
        fattura.aliquota_IVA = aliquota_IVA_ordine
        fattura.note = note_ordine
        fattura.save()

        # totale_righe_create = 0
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineFornitore, 
                pk=id_riga_ordine)
            riga_fattura = RigaFatturaFornitore()
            riga_fattura.fattura = fattura
            riga_fattura.riga_ordine = riga_ordine
            # commessa ? è memorizzata nella fattura
            riga_fattura.articolo = riga_ordine.articolo
            riga_fattura.articolo_codice_fornitore = riga_ordine.articolo_codice_fornitore
            riga_fattura.articolo_descrizione = riga_ordine.articolo_descrizione
            riga_fattura.articolo_prezzo = riga_ordine.articolo_prezzo
            riga_fattura.sconto_percentuale = riga_ordine.sconto_percentuale
            riga_fattura.articolo_unita_di_misura = riga_ordine.articolo_unita_di_misura
            riga_fattura.quantita = riga_ordine.quantita
            # riga_fattura.data_consegna ?????
            riga_fattura.totale = riga_ordine.totale
            # totale_righe_create += riga_fattura.totale
            riga_fattura.note = riga_ordine.note
            riga_fattura.save()
            ordini_da_aggiornare.add(riga_ordine.ordine)

            riga_ordine.fatturata = True
            riga_ordine.save()

        ## oltre al totale, bisogna aggiornare anche i campi imponibile e totale_iva, 
        ## quindi richiamo la funzione aggiorna_totale invece di settare direttamente
        ## la somma dei totali righe:
        # fattura.totale = totale_righe_create
        # fattura.save()
        fattura.aggiorna_totale()


        # settare l'ordine come fatturato?
        for ordine in ordini_da_aggiornare:
            ordine.aggiorna_campo_fatturato()

        serializer = FatturaFornitoreSerializer(fattura)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def crea_righe_da_bolla(self, request, pk=None):
        """
        Serve ad aggiungere delle righe ad una fattura già esistente.
        """
        bolle_da_aggiornare = set()
        fattura = get_object_or_404(FatturaFornitore, pk=pk)
        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_bolla_fornitore[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe bolla non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)

        for id_riga_bolla in lista_righe:
            riga_bolla = get_object_or_404(RigaBollaFornitore, 
                pk=id_riga_bolla)
            if riga_bolla.bolla.cancellato:
                return Response({"error": 
                    "La bolla {} è stata cancellata.".format(riga_bolla.bolla.codice)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_bolla.bolla.commessa != fattura.commessa:
                return Response({"error": "La commessa della bolla è diversa dalla commessa della fattura."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_bolla.fatturata:
                return Response({"error": ("La riga bolla con id {}" +
                        " fa già parte di un'altra fattura.").format(
                        riga_bolla.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_bolla.riga_ordine and riga_bolla.riga_ordine.fatturata:
                return Response({"error": ("La riga bolla con id {}" +
                        " fa riferimento ad un ordine già fatturato (interamente o parzialmente).").format(
                        riga_bolla.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            
        lista_righe_create = []
        totale_righe_create = 0
        
        fattura_da_confermare = False

        for id_riga_bolla in lista_righe:
            riga_bolla = get_object_or_404(RigaBollaFornitore, 
                pk=id_riga_bolla)

            riga_fattura = RigaFatturaFornitore()
            riga_fattura.fattura = fattura
            # la bolla non la memorizzo perché ho già la riga_bolla:
            # riga_fattura.bolla = riga_bolla.bolla
            riga_fattura.riga_bolla = riga_bolla
            riga_fattura.riga_ordine = riga_bolla.riga_ordine
            # commessa ? è già settata nella bolla
            riga_fattura.articolo = riga_bolla.articolo
            riga_fattura.articolo_codice_fornitore = riga_bolla.articolo_codice_fornitore
            riga_fattura.articolo_descrizione = riga_bolla.articolo_descrizione
            if riga_bolla.riga_ordine:
                riga_fattura.articolo_prezzo = riga_bolla.riga_ordine.articolo_prezzo
                riga_fattura.totale = riga_bolla.riga_ordine.totale
            else:
                fattura_da_confermare = True
                riga_fattura.articolo_prezzo = 0
                riga_fattura.totale = 0
            riga_fattura.articolo_unita_di_misura = riga_bolla.articolo_unita_di_misura
            riga_fattura.quantita = riga_bolla.quantita
            
            totale_righe_create += riga_fattura.totale
            riga_fattura.note = riga_bolla.note
            riga_fattura.save()
            lista_righe_create.append(riga_fattura)

            riga_bolla.fatturata=True
            riga_bolla.save()

            bolle_da_aggiornare.add(riga_bolla.bolla)

        fattura.totale += totale_righe_create
        if fattura_da_confermare:
            fattura.da_confermare = True
        # else lascia il valore di fattura.da_confermare che c'era già prima
        fattura.save()

        for bolla in bolle_da_aggiornare:
            bolla.aggiorna_campo_fatturato()

        serializer = RigaFatturaFornitoreSerializer(lista_righe_create, 
            many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def crea_fattura_da_righe_bolla(self, request):
        bolle_da_aggiornare = set()

        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_bolla_fornitore[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe bolla non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)

        fornitore_bolla = None

        fattura_da_confermare = False

        for id_riga_bolla in lista_righe:
            riga_bolla = get_object_or_404(RigaBollaFornitore, 
                pk=id_riga_bolla)
            # Utilizzo la prima riga bolla ricevuta per estrarre dei 
            # dati che utilizzo nella creazione della fattura.
            if fornitore_bolla == None:
                commessa_bolla = riga_bolla.bolla.commessa
                fornitore_bolla = riga_bolla.bolla.fornitore
                oggetto_bolla = riga_bolla.bolla.oggetto
                destinazione_bolla = riga_bolla.bolla.destinazione
                persona_di_riferimento_bolla = riga_bolla.bolla.persona_di_riferimento
                # La bolla non ha l'iva, dobbiamo risalire all'ordine. Se l'ordine 
                # è null perché la bolla è stata creata da 0, usa l'aliquota IVA
                # di default e setta da_confermare = True.
                if riga_bolla.riga_ordine:
                    aliquota_IVA_ordine = riga_bolla.riga_ordine.ordine.aliquota_IVA
                    pagamento_ordine = riga_bolla.riga_ordine.ordine.pagamento
                    sconto_euro_ordine = riga_bolla.riga_ordine.ordine.sconto_euro
                    sconto_percentuale_ordine = riga_bolla.riga_ordine.ordine.sconto_percentuale
                else:
                    fattura_da_confermare = True

                note_bolla = riga_bolla.bolla.note
            if riga_bolla.bolla.cancellato:
                return Response({"error": 
                    "La bolla {} è stata cancellata.".format(riga_bolla.bolla.codice)},
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_bolla.bolla.commessa != commessa_bolla:
                return Response({"error": "Righe bolla appartengono a bolle con commessa diversa."}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_bolla.fatturata:
                return Response({"error": ("La riga bolla con id {}" +
                        " fa già parte di un'altra fattura.").format(
                        riga_bolla.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
            if riga_bolla.riga_ordine and riga_bolla.riga_ordine.fatturata:
                return Response({"error": ("La riga bolla con id {}" +
                        " fa riferimento ad un ordine già fatturato (interamente o parzialmente).").format(
                        riga_bolla.id)}, 
                    status=status.HTTP_400_BAD_REQUEST)
        
        fattura = FatturaFornitore()
        fattura.data = date.today()
        # fattura.data_fattura_fornitore = ... da riempire a mano
        fattura.codice = FatturaFornitore.objects.next_codice()
        # fattura.codice_fattura_fornitore = ... da riempire a mano
        fattura.fornitore = fornitore_bolla
        fattura.commessa = commessa_bolla
        fattura.oggetto = oggetto_bolla
        fattura.destinazione = destinazione_bolla
        fattura.persona_di_riferimento = persona_di_riferimento_bolla
        if not fattura_da_confermare:
            fattura.da_confermare = False
            fattura.aliquota_IVA = aliquota_IVA_ordine
            fattura.pagamento = pagamento_ordine
            fattura.sconto_euro = sconto_euro_ordine
            fattura.sconto_percentuale = sconto_percentuale_ordine
        else:
            fattura.da_confermare = True
            fattura.aliquota_IVA = AliquotaIVA.objects.get_aliquota_default()
            fattura.pagamento = fornitore_bolla.pagamento
            fattura.sconto_euro = 0
            fattura.sconto_percentuale = 0
        fattura.note = note_bolla
        fattura.save()

        # totale_righe_create = 0
        for id_riga_bolla in lista_righe:
            riga_bolla = get_object_or_404(RigaBollaFornitore, 
                pk=id_riga_bolla)
            riga_fattura = RigaFatturaFornitore()
            riga_fattura.fattura = fattura
            riga_fattura.riga_bolla = riga_bolla
            riga_fattura.riga_ordine = riga_bolla.riga_ordine
            # commessa ? è memorizzata nella fattura
            riga_fattura.articolo = riga_bolla.articolo
            riga_fattura.articolo_codice_fornitore = riga_bolla.articolo_codice_fornitore
            riga_fattura.articolo_descrizione = riga_bolla.articolo_descrizione
            if not fattura.da_confermare:
                riga_fattura.articolo_prezzo = riga_bolla.riga_ordine.articolo_prezzo
                riga_fattura.totale = riga_bolla.riga_ordine.totale
            else: 
                riga_fattura.articolo_prezzo = 0
                riga_fattura.totale = 0
            riga_fattura.articolo_unita_di_misura = riga_bolla.articolo_unita_di_misura
            riga_fattura.quantita = riga_bolla.quantita
            # riga_fattura.data_consegna = ???
            # totale_righe_create += riga_fattura.totale
            riga_fattura.note = riga_bolla.note
            riga_fattura.save()
            bolle_da_aggiornare.add(riga_bolla.bolla)

            riga_bolla.fatturata = True
            riga_bolla.save()

        ## oltre al totale, bisogna aggiornare anche i campi imponibile e totale_iva, 
        ## quindi richiamo la funzione aggiorna_totale invece di settare direttamente
        ## la somma dei totali righe:
        # fattura.totale = totale_righe_create
        # fattura.save()
        fattura.aggiorna_totale()

        for bolla in bolle_da_aggiornare:
            bolla.aggiorna_campo_fatturato()

        serializer = FatturaFornitoreSerializer(fattura)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RigaFatturaFornitoreViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = RigaFatturaFornitore.objects.non_cancellati()
    serializer_class = RigaFatturaFornitoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('fattura', 'articolo')

    def get_permissions(self):
        return (MyCustomPerm('rigaFatturaFornitore', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()
        serializer.fattura.aggiorna_totale()

    def perform_create(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        # commessa? viene memorizzata nella fattura, non sulla riga
        instance = serializer.save(totale=totale)
        instance.fattura.aggiorna_totale()
        return super(RigaFatturaFornitoreViewSet, self).perform_create(serializer)
    
    def perform_update(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        instance = serializer.save(totale=totale)
        instance.fattura.aggiorna_totale()
        return super(RigaFatturaFornitoreViewSet, self).perform_update(serializer)









########################################### nested ViewSet:


class FornitoreContoCorrenteViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = ContoCorrente.objects.non_cancellati()
    serializer_class = ContoCorrenteSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita__id=entita_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class FornitoreIndirizzoViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = Indirizzo.objects.non_cancellati()
    serializer_class = IndirizzoSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita__id=entita_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class FornitoreContattoViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = Contatto.objects.non_cancellati()
    serializer_class = ContattoSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita__id=entita_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

