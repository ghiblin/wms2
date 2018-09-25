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


class ClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Entita.objects.clienti()
    serializer_class = ClienteSerializer

    def get_permissions(self):
        return (MyCustomPerm('cliente', self.action) ,)

    def perform_destroy(self, serializer):
        # cancellazione logica, non fisica
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # perform_create is called before the model of this view is saved.
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello
        next_codice = Entita.objects.next_codice(CLIENTE_PREFIX)
        instance = serializer.save(codice=next_codice, is_client=True)
        return super(ClienteViewSet, self).perform_create(serializer)

    @list_route()
    def get_tipo(self, request):
        # Perché non si può usare url_path nel decoratore per indicare
        # un altro url da assegnare all'api:
        # https://github.com/chibisov/drf-extensions/pull/73
        my_dict = [{'id':k, 'descrizione': v} for (k,v) in TIPO_PERSONA_CHOICES]
        return Response(my_dict, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def anche_fornitore(self, request, pk=None):
        """
        Modifica un cliente per farlo diventare anche un fornitore.
        """
        cliente = get_object_or_404(Entita, pk=pk)
        cliente.is_supplier = True
        cliente.save()
        serializer = ClienteSerializer(cliente)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PreventivoClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = PreventivoCliente.objects.non_cancellati()
    serializer_class = PreventivoClienteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = PreventivoClienteFilter

    def get_permissions(self):
        return (MyCustomPerm('preventivoCliente', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = PreventivoCliente.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(PreventivoClienteViewSet, self).perform_create(serializer)

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
        Serve ad duplicare un preventivo con tutte le sue righe e dettagli.
        """
        preventivo_da_clonare = get_object_or_404(PreventivoCliente, pk=pk)

        preventivo_nuovo = get_object_or_404(PreventivoCliente, pk=pk)
        # resettando l'id e salvando si crea un altro record che ha gli stessi campi...
        preventivo_nuovo.id = None
        preventivo_nuovo.commessa = None
        preventivo_nuovo.save()
        preventivo_nuovo.data = date.today()
        preventivo_nuovo.codice = PreventivoCliente.objects.next_codice()
        preventivo_nuovo.accettato = False
        preventivo_nuovo.save()
        
        # print("preventivo nuovo: id={}, codice={}".format(preventivo_nuovo.id, preventivo_nuovo.codice))
        # print("preventivo nuovo: data={}".format(preventivo_nuovo.data))
        for r in preventivo_da_clonare.righe.non_cancellati():
            rn = RigaPreventivoCliente()
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

        # for r in preventivo_nuovo.righe.all():
        #    print("riga nuova: id={}, quantità={}, articolo={}, descrizione={}".format(r.id, r.quantita, r.articolo,
        # r.articolo_descrizione))

        serializer = PreventivoClienteSerializer(preventivo_nuovo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RigaPreventivoClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = RigaPreventivoCliente.objects.non_cancellati()
    serializer_class = RigaPreventivoClienteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('preventivo',)

    def get_permissions(self):
        return (MyCustomPerm('rigaPreventivoCliente', self.action) ,)

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
        return super(RigaPreventivoClienteViewSet, self).perform_create(serializer)
    
    def perform_update(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        instance = serializer.save(totale=totale)
        instance.preventivo.aggiorna_totale()
        return super(RigaPreventivoClienteViewSet, self).perform_update(serializer)


class OrdineClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = OrdineCliente.objects.non_cancellati()
    serializer_class = OrdineClienteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = OrdineClienteFilter

    def get_permissions(self):
        return (MyCustomPerm('ordineCliente', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = OrdineCliente.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(OrdineClienteViewSet, self).perform_create(serializer)

    @detail_route(methods=['post'])
    def crea_righe_da_preventivo(self, request, pk=None):
        """
        Serve ad aggiungere righe ordine ad un ordine già esistente selezionando
        le righe di un preventivo.
        """
        preventivi_da_aggiornare = set()
        ordine = get_object_or_404(OrdineCliente, pk=pk)
        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_preventivo_cliente[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe preventivo non specificate."}, status=status.HTTP_400_BAD_REQUEST)

        for id_riga_preventivo in lista_righe:
            riga_preventivo = get_object_or_404(RigaPreventivoCliente, 
                pk=id_riga_preventivo)            
            if riga_preventivo.preventivo.cancellato:
                return Response({"error": "Il preventivo è stato cancellato."}, status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.preventivo.cliente != ordine.cliente:
                return Response({"error": "Il cliente del preventivo è diverso dal cliente dell'ordine."},
                                status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.accettata:
                return Response({"error": "La riga preventivo con id {} fa già parte di un altro ordine.".format(
                        riga_preventivo.id)}, status=status.HTTP_400_BAD_REQUEST)

        lista_righe_create = []
        totale_righe_create = 0
        for id_riga_preventivo in lista_righe:
            riga_preventivo = get_object_or_404(RigaPreventivoCliente, pk=id_riga_preventivo)

            riga_ordine = RigaOrdineCliente()
            riga_ordine.ordine = ordine
            riga_ordine.preventivo = riga_preventivo.preventivo
            riga_ordine.riga_preventivo = riga_preventivo
            # commessa ?
            riga_ordine.articolo = riga_preventivo.articolo
            riga_ordine.articolo_descrizione = riga_preventivo.articolo_descrizione
            riga_ordine.articolo_prezzo = riga_preventivo.articolo_prezzo
            riga_ordine.sconto_percentuale = riga_preventivo.sconto_percentuale
            riga_ordine.articolo_unita_di_misura = riga_preventivo.articolo_unita_di_misura
            riga_ordine.quantita = riga_preventivo.quantita
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

        serializer = RigaOrdineClienteSerializer(lista_righe_create, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def crea_ordine_da_righe_preventivo(self, request):
        preventivi_da_aggiornare = set()

        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_preventivo_cliente[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe preventivo non specificate."}, status=status.HTTP_400_BAD_REQUEST)
        id_commessa = request.POST.get('commessa', None)
        if not id_commessa:
            return Response({"error": "Commessa non specificata."}, status=status.HTTP_400_BAD_REQUEST)
        # uso filter invece di get:
        commessa = Commessa.objects.filter(pk=id_commessa)
        if commessa:
            commessa = commessa[0]
        else:
            return Response({"error": "La commessa specificata non esiste."}, status=status.HTTP_400_BAD_REQUEST)
        if commessa.cancellato:
            return Response({"error": "La commessa specificata non è valida."}, status=status.HTTP_400_BAD_REQUEST)

        cliente_preventivo = None
        for id_riga_preventivo in lista_righe:
            riga_preventivo = get_object_or_404(RigaPreventivoCliente, 
                pk=id_riga_preventivo)
            # utilizzo la prima riga preventivo ricevuta per estrarre dei 
            # dati che utilizzo nella creazione dell'ordine
            if cliente_preventivo == None:
                cliente_preventivo = riga_preventivo.preventivo.cliente
                oggetto_preventivo = riga_preventivo.preventivo.oggetto
                pagamento_preventivo = riga_preventivo.preventivo.pagamento
                persona_di_riferimento_preventivo = riga_preventivo.preventivo.persona_di_riferimento
                destinazione_preventivo = riga_preventivo.preventivo.destinazione
                disegni_costruttivi_preventivo = riga_preventivo.preventivo.disegni_costruttivi
                relazione_di_calcolo_preventivo = riga_preventivo.preventivo.relazione_di_calcolo
                tipo_di_acciaio_preventivo = riga_preventivo.preventivo.tipo_di_acciaio
                spessori_preventivo = riga_preventivo.preventivo.spessori
                zincatura_preventivo = riga_preventivo.preventivo.zincatura
                classe_di_esecuzione_preventivo = riga_preventivo.preventivo.classe_di_esecuzione
                wps_preventivo = riga_preventivo.preventivo.wps
                verniciatura_preventivo = riga_preventivo.preventivo.verniciatura
                aliquota_IVA_preventivo = riga_preventivo.preventivo.aliquota_IVA
            
            if (riga_preventivo.preventivo.commessa is not None) \
                    and riga_preventivo.preventivo.commessa != commessa:
                # non si può usare lo stesso preventivo per ordini diversi a meno che
                # la commessa associata agli ordini sia sempre la stessa
                return Response({"error": "Non si può usare lo stesso preventivo per commesse diverse."},
                                status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.preventivo.cliente != cliente_preventivo:
                return Response({"error": "Righe preventivo appartengono a preventivi di diversi clienti."},
                                status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.preventivo.cancellato:
                return Response({"error": "La riga preventivo con id {} fa parte di un preventivo cancellato.".format(
                        riga_preventivo.id)}, status=status.HTTP_400_BAD_REQUEST)
            if riga_preventivo.accettata:
                return Response({"error": "La riga preventivo con id {} fa già parte di un altro ordine.".format(
                        riga_preventivo.id)}, status=status.HTTP_400_BAD_REQUEST)

        ordine = OrdineCliente()
        ordine.data = date.today()
        ordine.codice = OrdineCliente.objects.next_codice()
        ordine.cliente = cliente_preventivo
        ordine.commessa = commessa
        ordine.oggetto = oggetto_preventivo
        ordine.pagamento = pagamento_preventivo
        ordine.persona_di_riferimento = persona_di_riferimento_preventivo
        ordine.destinazione = destinazione_preventivo
        ordine.disegni_costruttivi = disegni_costruttivi_preventivo
        ordine.relazione_di_calcolo = relazione_di_calcolo_preventivo
        ordine.tipo_di_acciaio = tipo_di_acciaio_preventivo
        ordine.spessori = spessori_preventivo
        ordine.zincatura = zincatura_preventivo
        ordine.classe_di_esecuzione = classe_di_esecuzione_preventivo
        ordine.wps = wps_preventivo
        ordine.verniciatura = verniciatura_preventivo
        ordine.aliquota_IVA = aliquota_IVA_preventivo
        ordine.save()

        totale_righe_create = 0
        for id_riga_preventivo in lista_righe:
            riga_preventivo = get_object_or_404(RigaPreventivoCliente, pk=id_riga_preventivo)
            riga_ordine = RigaOrdineCliente()
            riga_ordine.ordine = ordine
            riga_ordine.preventivo = riga_preventivo.preventivo
            riga_ordine.riga_preventivo = riga_preventivo
            # commessa ?
            riga_ordine.articolo = riga_preventivo.articolo
            riga_ordine.articolo_descrizione = riga_preventivo.articolo_descrizione
            riga_ordine.articolo_prezzo = riga_preventivo.articolo_prezzo
            riga_ordine.sconto_percentuale = riga_preventivo.sconto_percentuale
            riga_ordine.articolo_unita_di_misura = riga_preventivo.articolo_unita_di_misura
            riga_ordine.quantita = riga_preventivo.quantita
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

        serializer = OrdineClienteSerializer(ordine)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RigaOrdineClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = RigaOrdineCliente.objects.non_cancellati()
    serializer_class = RigaOrdineClienteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('ordine', 'preventivo', 'commessa', 'articolo')

    def get_permissions(self):
        return (MyCustomPerm('rigaOrdineCliente', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()
        serializer.ordine.aggiorna_totale()
    
    def perform_create(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        commessa = serializer.validated_data['ordine'].commessa
        instance = serializer.save(totale=totale, commessa=commessa)
        instance.ordine.aggiorna_totale()
        return super(RigaOrdineClienteViewSet, self).perform_create(serializer)
    
    def perform_update(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        instance = serializer.save(totale=totale)
        instance.ordine.aggiorna_totale()
        return super(RigaOrdineClienteViewSet, self).perform_update(serializer)


class OrdineClienteSenzaTotaleViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
    Duplicato readonly di OrdineCliente a cui manca il campo totale nel serializzatore.
    E' utilizzato per permettere la creazione di bolle agli utenti ut.
    """
    queryset = OrdineCliente.objects.non_cancellati()
    serializer_class = OrdineClienteSenzaTotaleSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = OrdineClienteFilter

    def get_permissions(self):
        return (MyCustomPerm('ordineClienteSenzaTotale', self.action) ,)


class RigaOrdineClienteSenzaTotaleViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
    Duplicato readonly di RigaOrdineCliente a cui manca il campo totale nel serializzatore.
    E' utilizzato per permettere la creazione di bolle agli utenti ut.
    """
    queryset = RigaOrdineCliente.objects.non_cancellati()
    serializer_class = RigaOrdineClienteSenzaTotaleSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('ordine', 'preventivo', 'commessa', 'articolo')

    def get_permissions(self):
        return (MyCustomPerm('rigaOrdineClienteSenzaTotale', self.action) ,)


class TipoAspettoEsterioreViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TipoAspettoEsteriore.objects.all()
    serializer_class = TipoAspettoEsterioreSerializer
    permission_classes = (permissions.AllowAny,)


class TipoTrasportoACuraViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TipoTrasportoACura.objects.all()
    serializer_class = TipoTrasportoACuraSerializer
    permission_classes = (permissions.AllowAny,)


class TipoPortoViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TipoPorto.objects.all()
    serializer_class = TipoPortoSerializer
    permission_classes = (permissions.AllowAny,)


class TipoCausaleTrasportoViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TipoCausaleTrasporto.objects.all()
    serializer_class = TipoCausaleTrasportoSerializer
    permission_classes = (permissions.AllowAny,)


class BollaClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = BollaCliente.objects.non_cancellati()
    serializer_class = BollaClienteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = BollaClienteFilter

    def get_permissions(self):
        return (MyCustomPerm('bollaCliente', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = BollaCliente.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(BollaClienteViewSet, self).perform_create(serializer)
    
    @detail_route(methods=['post'])
    def crea_righe_da_ordine(self, request, pk=None):
        """
        Serve ad aggiungere delle righe ad una bolla già esistente.
        """
        ordini_da_aggiornare = set()
        bolla = get_object_or_404(BollaCliente, pk=pk)
        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_ordine_cliente[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe ordine non specificate."}, status=status.HTTP_400_BAD_REQUEST)

        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineCliente, 
                pk=id_riga_ordine)
            if riga_ordine.ordine.cancellato:
                return Response({"error": "L'ordine è stato cancellato."}, status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.ordine.cliente != bolla.cliente:
                return Response({"error": "Il cliente dell'ordine è diverso dal cliente della bolla."},
                                status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.bollettata:
                return Response({"error": "La riga ordine con id {} fa già parte di un'altra bolla.".format(
                        riga_ordine.id)}, status=status.HTTP_400_BAD_REQUEST)

        lista_righe_create = []
        # totale_righe_create = 0
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineCliente, pk=id_riga_ordine)

            riga_bolla = RigaBollaCliente()
            riga_bolla.bolla = bolla
            riga_bolla.ordine = riga_ordine.ordine
            riga_bolla.riga_ordine = riga_ordine
            # commessa ? è già settata nella bolla
            riga_bolla.articolo = riga_ordine.articolo
            riga_bolla.articolo_descrizione = riga_ordine.articolo_descrizione
            # riga_bolla.articolo_prezzo = riga_ordine.articolo_prezzo
            riga_bolla.articolo_unita_di_misura = riga_ordine.articolo_unita_di_misura
            riga_bolla.quantita = riga_ordine.quantita
            # riga_bolla.totale = riga_ordine.totale
            # totale_righe_create += riga_bolla.totale
            riga_bolla.note = riga_ordine.note
            riga_bolla.save()
            lista_righe_create.append(riga_bolla)

            riga_ordine.bollettata=True
            riga_ordine.save()

            ordini_da_aggiornare.add(riga_ordine.ordine)

        # bolla.totale += totale_righe_create
        # bolla.save()

        for ordine in ordini_da_aggiornare:
            ordine.aggiorna_stato()

        serializer = RigaBollaClienteSerializer(lista_righe_create, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def crea_bolla_da_righe_ordine(self, request):
        ordini_da_aggiornare = set()

        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_ordine_cliente[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe ordine non specificate."}, status=status.HTTP_400_BAD_REQUEST)

        cliente_ordine = None
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineCliente, 
                pk=id_riga_ordine)
            # utilizzo la prima riga ordine ricevuta per estrarre dei 
            # dati che utilizzo nella creazione della bolla
            if cliente_ordine == None:
                commessa_bolla = riga_ordine.ordine.commessa
                cliente_ordine = riga_ordine.ordine.cliente
                destinazione_ordine = riga_ordine.ordine.destinazione
                persona_di_riferimento_ordine = riga_ordine.ordine.persona_di_riferimento
                riferimento_cliente_ordine = riga_ordine.ordine.riferimento_cliente
                note_ordine = riga_ordine.ordine.note
            if riga_ordine.ordine.commessa != commessa_bolla:
                return Response({"error": "Righe ordine appartengono a ordini con commessa diversa."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            if riga_ordine.bollettata:
                return Response({"error": "La riga ordine con id {} fa già parte di un'altra bolla.".format(
                        riga_ordine.id)}, status=status.HTTP_400_BAD_REQUEST)
            
        bolla = BollaCliente()
        bolla.data = date.today()
        bolla.codice = BollaCliente.objects.next_codice()
        bolla.cliente = cliente_ordine
        bolla.commessa = commessa_bolla
        bolla.destinazione = destinazione_ordine
        bolla.persona_di_riferimento = persona_di_riferimento_ordine
        bolla.riferimento_cliente = riferimento_cliente_ordine
        bolla.note = note_ordine
        bolla.causale_trasporto_id = BollaCliente.objects.get_default_causale_trasporto()
        bolla.trasporto_a_cura_id = BollaCliente.objects.get_default_trasporto_a_cura_di()
        bolla.save()

        totale_righe_create = 0
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineCliente, 
                pk=id_riga_ordine)
            riga_bolla = RigaBollaCliente()
            riga_bolla.bolla = bolla
            riga_bolla.riga_ordine = riga_ordine
            # commessa ? è memorizzata nella bolla
            riga_bolla.articolo = riga_ordine.articolo
            riga_bolla.articolo_descrizione = riga_ordine.articolo_descrizione
            # riga_bolla.articolo_prezzo = riga_ordine.articolo_prezzo
            riga_bolla.articolo_unita_di_misura = riga_ordine.articolo_unita_di_misura
            riga_bolla.quantita = riga_ordine.quantita
            # riga_bolla.totale = riga_ordine.totale
            # totale_righe_create += riga_bolla.totale
            riga_bolla.note = riga_ordine.note
            riga_bolla.save()

            # la stessa riga_ordine usata per creare la bolla potrebbe essere già
            # stata usata per creare una fattura. Non è il caso d'uso classico
            # ma può capitare.
            if riga_ordine.fatturata:
                # import pdb; pdb.set_trace()
                riga_bolla.fatturata = True
                riga_bolla.save()
                # non so perché ma non posso salvare la riga fattura nell'istanza di riga_bolla
                # ma devo modificare l'istanza di riga_fattura settandoci riga_bolla:
                # riga_bolla.riga_fattura = riga_ordine.riga_fattura
                rf = RigaFatturaCliente.objects.get(pk=riga_ordine.riga_fattura.id)
                rf.riga_bolla = riga_bolla
                rf.save()
            ordini_da_aggiornare.add(riga_ordine.ordine)

            riga_ordine.bollettata = True
            riga_ordine.save()

        # bolla.totale += totale_righe_create
        # bolla.save()
        bolla.aggiorna_campo_fatturato()

        # settare l'ordine come bollettato?
        for ordine in ordini_da_aggiornare:
            ordine.aggiorna_stato()

        serializer = BollaClienteSerializer(bolla)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RigaBollaClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = RigaBollaCliente.objects.non_cancellati()
    serializer_class = RigaBollaClienteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('bolla', 'articolo')

    def get_permissions(self):
        return (MyCustomPerm('rigaBollaCliente', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()
        # serializer.bolla.aggiorna_totale()
    
    # visto che nella bolla non c'è il prezzo non si deve aggiornare il totale
    # quando si crea, modifica o cancella una riga


class FatturaClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = FatturaCliente.objects.non_cancellati()
    serializer_class = FatturaClienteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = FatturaClienteFilter

    def get_permissions(self):
        return (MyCustomPerm('fatturaCliente', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = FatturaCliente.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(FatturaClienteViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        # Ogni volta che si modifica una fattura, si resetta il flag 'da_confermare' a False
        kwargs = {
            'da_confermare': False,
        }

        # se l'utente non seleziona una commessa, forza il reset del campo:
        if 'commessa' not in self.request.data:
            kwargs['commessa'] = None

        instance = serializer.save(**kwargs)
        # instance = serializer.save(da_confermare=False)

        # se l'iva è cambiata, il totale della fattura va aggiornato. Per semplicità ricalcolo il totale tutte le volte:
        instance.aggiorna_totale()

        # return super(FatturaClienteViewSet, self).perform_update(serializer)
        serializer = FatturaClienteSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def crea_righe_da_ordine(self, request, pk=None):
        """
        Serve ad aggiungere delle righe ad una fattura già esistente.
        """
        ordini_da_aggiornare = set()
        fattura = get_object_or_404(FatturaCliente, pk=pk)
        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_ordine_cliente[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe ordine non specificate."}, 
                status=status.HTTP_400_BAD_REQUEST)

        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineCliente, 
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
            riga_ordine = get_object_or_404(RigaOrdineCliente, 
                pk=id_riga_ordine)

            riga_fattura = RigaFatturaCliente()
            riga_fattura.fattura = fattura
            riga_fattura.ordine = riga_ordine.ordine
            riga_fattura.riga_ordine = riga_ordine
            # commessa ? è già settata nella bolla
            riga_fattura.articolo = riga_ordine.articolo
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

        serializer = RigaFatturaClienteSerializer(lista_righe_create, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def crea_fattura_da_righe_ordine(self, request):
        ordini_da_aggiornare = set()

        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_ordine_cliente[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe ordine non specificate."}, status=status.HTTP_400_BAD_REQUEST)

        cliente_ordine = None
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineCliente, 
                pk=id_riga_ordine)
            # Utilizzo la prima riga ordine ricevuta per estrarre dei 
            # dati che utilizzo nella creazione della fattura.
            if cliente_ordine == None:
                commessa_ordine = riga_ordine.ordine.commessa
                cliente_ordine = riga_ordine.ordine.cliente
                oggetto_ordine = riga_ordine.ordine.oggetto
                pagamento_ordine = riga_ordine.ordine.pagamento
                sconto_euro_ordine = riga_ordine.ordine.sconto_euro
                sconto_percentuale_ordine = riga_ordine.ordine.sconto_percentuale
                destinazione_ordine = riga_ordine.ordine.destinazione
                persona_di_riferimento_ordine = riga_ordine.ordine.persona_di_riferimento
                riferimento_cliente_ordine = riga_ordine.ordine.riferimento_cliente
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
                return Response({"error": "La riga ordine con id {} fa già parte di un'altra fattura.".format(
                        riga_ordine.id)}, status=status.HTTP_400_BAD_REQUEST)
            if riga_ordine.bollettata:
                return Response({"error": "La riga ordine con id {} fa parte di una bolla.".format(
                        riga_ordine.id)}, status=status.HTTP_400_BAD_REQUEST)
            
        fattura = FatturaCliente()
        fattura.data = date.today()
        fattura.codice = FatturaCliente.objects.next_codice()
        fattura.cliente = cliente_ordine
        fattura.commessa = commessa_ordine
        fattura.oggetto = oggetto_ordine
        fattura.pagamento = pagamento_ordine
        fattura.sconto_euro = sconto_euro_ordine
        fattura.sconto_percentuale = sconto_percentuale_ordine
        fattura.destinazione = destinazione_ordine
        fattura.persona_di_riferimento = persona_di_riferimento_ordine
        fattura.riferimento_cliente = riferimento_cliente_ordine
        fattura.aliquota_IVA = aliquota_IVA_ordine
        fattura.note = note_ordine
        fattura.save()

        # totale_righe_create = 0
        for id_riga_ordine in lista_righe:
            riga_ordine = get_object_or_404(RigaOrdineCliente, 
                pk=id_riga_ordine)
            riga_fattura = RigaFatturaCliente()
            riga_fattura.fattura = fattura
            riga_fattura.riga_ordine = riga_ordine
            # commessa ? è memorizzata nella fattura
            riga_fattura.articolo = riga_ordine.articolo
            riga_fattura.articolo_descrizione = riga_ordine.articolo_descrizione
            riga_fattura.articolo_prezzo = riga_ordine.articolo_prezzo
            riga_fattura.sconto_percentuale = riga_ordine.sconto_percentuale
            riga_fattura.articolo_unita_di_misura = riga_ordine.articolo_unita_di_misura
            riga_fattura.quantita = riga_ordine.quantita
            riga_fattura.totale = riga_ordine.totale
            # totale_righe_create += riga_fattura.totale
            riga_fattura.note = riga_ordine.note
            riga_fattura.save()
            ordini_da_aggiornare.add(riga_ordine.ordine)

            riga_ordine.fatturata = True
            riga_ordine.save()

        # Oltre al totale, bisogna aggiornare anche i campi imponibile e totale_iva,
        # quindi richiamo la funzione aggiorna_totale invece di settare direttamente
        # la somma dei totali righe:
        # fattura.totale = totale_righe_create
        # fattura.save()
        fattura.aggiorna_totale()

        # settare l'ordine come fatturato?
        for ordine in ordini_da_aggiornare:
            ordine.aggiorna_campo_fatturato()

        serializer = FatturaClienteSerializer(fattura)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def crea_righe_da_bolla(self, request, pk=None):
        """
        Serve ad aggiungere delle righe ad una fattura già esistente.
        """
        bolle_da_aggiornare = set()
        fattura = get_object_or_404(FatturaCliente, pk=pk)
        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_bolla_cliente[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe bolla non specificate."}, status=status.HTTP_400_BAD_REQUEST)

        for id_riga_bolla in lista_righe:
            riga_bolla = get_object_or_404(RigaBollaCliente, 
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
            riga_bolla = get_object_or_404(RigaBollaCliente, pk=id_riga_bolla)

            riga_fattura = RigaFatturaCliente()
            riga_fattura.fattura = fattura
            riga_fattura.bolla = riga_bolla.bolla
            riga_fattura.riga_bolla = riga_bolla
            riga_fattura.riga_ordine = riga_bolla.riga_ordine
            # commessa ? è già settata nella bolla
            riga_fattura.articolo = riga_bolla.articolo
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

        serializer = RigaFatturaClienteSerializer(lista_righe_create, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def crea_fattura_da_righe_bolla(self, request):
        bolle_da_aggiornare = set()
        ordini_da_aggiornare = set()

        # NB: jquery aggiunge "[]" al nome dei parametri mandati come array:
        lista_righe = request.POST.getlist('riga_bolla_cliente[]', [])
        if len(lista_righe) == 0:
            return Response({"error": "Righe bolla non specificate."}, status=status.HTTP_400_BAD_REQUEST)

        cliente_bolla = None

        fattura_da_confermare = False

        for id_riga_bolla in lista_righe:
            riga_bolla = get_object_or_404(RigaBollaCliente, 
                pk=id_riga_bolla)
            # Utilizzo la prima riga bolla ricevuta per estrarre dei 
            # dati che utilizzo nella creazione della fattura.
            if cliente_bolla == None:
                commessa_bolla = riga_bolla.bolla.commessa
                cliente_bolla = riga_bolla.bolla.cliente
                oggetto_bolla = riga_bolla.bolla.oggetto
                destinazione_bolla = riga_bolla.bolla.destinazione
                persona_di_riferimento_bolla = riga_bolla.bolla.persona_di_riferimento
                riferimento_cliente_bolla = riga_bolla.bolla.riferimento_cliente
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
        
        fattura = FatturaCliente()
        fattura.data = date.today()
        fattura.codice = FatturaCliente.objects.next_codice()
        fattura.cliente = cliente_bolla
        fattura.commessa = commessa_bolla
        fattura.oggetto = oggetto_bolla
        fattura.destinazione = destinazione_bolla
        fattura.persona_di_riferimento = persona_di_riferimento_bolla
        fattura.riferimento_cliente = riferimento_cliente_bolla
        if not fattura_da_confermare:
            fattura.da_confermare = False
            fattura.aliquota_IVA = aliquota_IVA_ordine
            fattura.pagamento = pagamento_ordine
            fattura.sconto_euro = sconto_euro_ordine
            fattura.sconto_percentuale = sconto_percentuale_ordine
        else:
            fattura.da_confermare = True
            fattura.aliquota_IVA = AliquotaIVA.objects.get_aliquota_default()
            fattura.pagamento = cliente_bolla.pagamento
            fattura.sconto_euro = 0
            fattura.sconto_percentuale = 0
        fattura.note = note_bolla
        fattura.save()

        # totale_righe_create = 0
        for id_riga_bolla in lista_righe:
            riga_bolla = get_object_or_404(RigaBollaCliente, pk=id_riga_bolla)
            riga_fattura = RigaFatturaCliente()
            riga_fattura.fattura = fattura
            riga_fattura.riga_bolla = riga_bolla
            riga_fattura.riga_ordine = riga_bolla.riga_ordine
            # commessa ? è memorizzata nella fattura
            riga_fattura.articolo = riga_bolla.articolo
            riga_fattura.articolo_descrizione = riga_bolla.articolo_descrizione
            if not fattura.da_confermare:
                riga_fattura.articolo_prezzo = riga_bolla.riga_ordine.articolo_prezzo
                riga_fattura.totale = riga_bolla.riga_ordine.totale
            else: 
                riga_fattura.articolo_prezzo = 0
                riga_fattura.totale = 0

            if riga_bolla.riga_ordine:
                riga_fattura.riga_ordine = riga_bolla.riga_ordine
                riga_bolla.riga_ordine.fatturata = True
                riga_bolla.riga_ordine.save()
                ordini_da_aggiornare.add(riga_bolla.riga_ordine.ordine)

            riga_fattura.articolo_unita_di_misura = riga_bolla.articolo_unita_di_misura
            riga_fattura.quantita = riga_bolla.quantita            
            # totale_righe_create += riga_fattura.totale
            riga_fattura.note = riga_bolla.note
            riga_fattura.save()
            bolle_da_aggiornare.add(riga_bolla.bolla)

            riga_bolla.fatturata = True
            riga_bolla.save()

        # Oltre al totale, bisogna aggiornare anche i campi imponibile e totale_iva,
        # quindi richiamo la funzione aggiorna_totale invece di settare direttamente
        # la somma dei totali righe:
        # fattura.totale = totale_righe_create
        # fattura.save()
        fattura.aggiorna_totale()

        for bolla in bolle_da_aggiornare:
            bolla.aggiorna_campo_fatturato()

        for ordine in ordini_da_aggiornare:
            ordine.aggiorna_campo_fatturato()

        serializer = FatturaClienteSerializer(fattura)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @list_route(methods=['get'])
    def test_sm(self, request):
        """
        Metodo creato per testare facilmente se le transazioni funzionano. Basta aprire l'url
        /api/v1/fatturaCliente/test_sm/.
        La chiamata fallirà perché il secondo oggetto non può essere creato con una descrizione 
        uguale al primo oggetto creato. Poi vedere la tabella TipoLavoro nell'admin e controllare
        se il primo oggetto è stato creato o no.
        Se il primo oggetto è stato creato verificare che nelle impostazioni del database in 
        local_settings è stato impostato 'ATOMIC_REQUESTS': True. Esempio:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'ATOMIC_REQUESTS': True
                ... ecc... 
            }
        }
        Prima di riprovare questa chiamata per vedere se funziona un cambio ai settings, 
        ricordarsi di cancellare a mano dal database il record con la descrizione vuota.
        """
        tl = TipoLavoro()
        tl.descrizione = ""
        tl.save()

        tl2 = TipoLavoro()
        tl2.descrizione = ""
        tl2.save()        

        serializer = TipoLavoroSerializer(tl2)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def dissocia_bolle(self, request, pk=None):
        """
        Dissocia le righe di questa fattura dalle righe bolle utilizzate nel drop.
        """
        fattura = get_object_or_404(FatturaCliente, pk=pk)
        fattura.dissocia_bolle_e_ordini()

        serializer = FatturaClienteSerializer(fattura)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RigaFatturaClienteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = RigaFatturaCliente.objects.non_cancellati()
    serializer_class = RigaFatturaClienteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('fattura', 'articolo')

    def get_permissions(self):
        return (MyCustomPerm('rigaFatturaCliente', self.action) ,)

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
        return super(RigaFatturaClienteViewSet, self).perform_create(serializer)
    
    def perform_update(self, serializer):
        prezzo = serializer.validated_data['articolo_prezzo']
        quantita = serializer.validated_data['quantita']
        sconto_percentuale = serializer.validated_data['sconto_percentuale']
        totale = prezzo * (1-(sconto_percentuale/100)) * quantita
        instance = serializer.save(totale=totale)
        instance.fattura.aggiorna_totale()
        return super(RigaFatturaClienteViewSet, self).perform_update(serializer)


########################################### nested ViewSet:

class ClienteContoCorrenteViewSet(LoggingMixin, viewsets.ViewSet):
    # queryset = ContoCorrente.objects.select_related('entita').non_cancellati()
    queryset = ContoCorrente.objects.non_cancellati()
    serializer_class = ContoCorrenteSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita__id=entita_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    # questo in realtà non serve perché per la creazione/modifica/cancellazione
    # si usa l'api dei conti correnti
    def retrieve(self, request, pk=None, entita_pk=None):
        # GET /cliente/<entita_pk>/contoCorrente/<pk>/
        queryset = ContoCorrente.objects.non_cancellati()
        conto_corrente = get_object_or_404(queryset, pk=pk)
        serializer = ContoCorrenteSerializer(conto_corrente)
        return Response(serializer.data)


class ClienteIndirizzoViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = Indirizzo.objects.non_cancellati()
    serializer_class = IndirizzoSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita__id=entita_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class ClienteContattoViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = Contatto.objects.non_cancellati()
    serializer_class = ContattoSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita__id=entita_pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

