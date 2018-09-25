#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
# import logging

# from datetime import date
# from decimal import Decimal
# from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout

from rest_framework import viewsets, status, filters, views  # permissions
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

# from anagrafiche.models import *
from .apiPermissions import *  # IsAuthorOfPost
from .apiSerializers import *  # PostSerializer
from .apiFilters import *
from .apiPaginator import DefaultPagination
from django.core.files.base import ContentFile
from django.http import HttpResponse

logger = logging.getLogger('django')


class LoggingMixin(object):
    """
    Mixin che logga la risposta dell'API. La risposta contiene anche i dati della request.    
    """

    def finalize_response(self, request, response, *args, **kwargs):
        # import pdb; pdb.set_trace()
        # if request.path == "/api/v1/rigaOrdineClienteSenzaTotale/":
        #     import pdb; pdb.set_trace()
        template = "===================================================================\n" \
            + "{} - {} - {}\n" \
            + "USER = {}\n" \
            + "Request query params = {}\n" \
            + "Request DATA = {}\n" \
            + "Response status code = {}\n" \
            + "Response data = {}\n" \
            + "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
        logger.info(template.format(
            datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            request.META['REQUEST_METHOD'], 
            request.path,
            request._user.username,
            request.query_params,
            request.DATA if hasattr(request, 'DATA') else None,
            response.status_code,
            response.data if hasattr(response, 'data') else None,
        ))

        return super(LoggingMixin, self).finalize_response(request, response, *args, **kwargs)


########################################################################################################################
# login/logout:
########################################################################################################################


class LoginView(views.APIView):
    # Per ovvie ragioni la classe delle API di login non va loggata.

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        # con python 3 request.body è di tipo byte ma json.load()
        # si aspetta una stringa. quindi devo aggiungere 
        # .decode('utf-8')
        # import pdb; pdb.set_trace()
        # data = json.loads(request.body.decode('utf-8'))
        # username = data.get('username', None)
        # password = data.get('password', None)

        username = request.data['username']
        password = request.data['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                serialized = UserSerializer(user)
                return Response(serialized.data)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username/password combination invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(LoggingMixin, views.APIView):
    # permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        logout(request)
        # we just return an empty response with a 200 status code.
        return Response({}, status=status.HTTP_204_NO_CONTENT)


########################################################################################################################
# Model ViewSet:
########################################################################################################################
class TipoPagamentoViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TipoPagamento.objects.all().order_by('id')
    serializer_class = TipoPagamentoSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (permissions.AllowAny,)


# questa è un'api che non userermo mai ma ci serve per creare
# nested relationships
class ProprietarioViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Entita.objects.filter(is_owner=True)
    serializer_class = ProprietarioSerializer

    def get_permissions(self):
        return (MyCustomPerm('proprietario', self.action) ,)

    def list(self, request):
        if self.queryset.count() == 0:
            return Response({"error": "Record non trovato"}, status=status.HTTP_404_NOT_FOUND)
        if self.queryset.count() > 1:
            return Response({"error": "Impossibile determinare il record appropriato"}, status=status.HTTP_409_CONFLICT)
        proprietario = self.queryset[0]
        serializer = self.serializer_class(proprietario)
        return Response(serializer.data)


class ContoCorrenteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = ContoCorrente.objects.all()
    serializer_class = ContoCorrenteSerializer

    def get_permissions(self):
        return (MyCustomPerm('contoCorrente', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # faccio in modo che ci sia solo un conto predefinito per la stessa entità
        is_predefinito = serializer.validated_data.get('predefinito', False)
        entita = serializer.validated_data['entita']
        ContoCorrente.objects.resetPredefinito(entita, is_predefinito)
        instance = serializer.save()
        return super(ContoCorrenteViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        # faccio in modo che ci sia solo un conto predefinito per la stessa entità
        is_predefinito = serializer.validated_data.get('predefinito', False)
        entita = serializer.validated_data['entita']
        ContoCorrente.objects.resetPredefinito(entita, is_predefinito)
        instance = serializer.save()
        return super(ContoCorrenteViewSet, self).perform_update(serializer)


class IndirizzoViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Indirizzo.objects.non_cancellati()
    serializer_class = IndirizzoSerializer

    def get_permissions(self):
        return (MyCustomPerm('indirizzo', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    @list_route()
    def get_tipo_sede(self, request):
        my_dict = [{'id':k, 'descrizione': v} for (k,v) in TIPO_SEDE_CHOICES]
        return Response(my_dict, status=status.HTTP_200_OK)


class ContattoViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Contatto.objects.non_cancellati()
    serializer_class = ContattoSerializer

    def get_permissions(self):
        return (MyCustomPerm('contatto', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    @list_route()
    def get_tipo_contatto(self, request):
        my_dict = [{'id':k, 'descrizione': v} for (k,v) in TIPO_CONTATTO_CHOICES]
        return Response(my_dict, status=status.HTTP_200_OK)


class CommessaViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Commessa.objects.non_cancellati()
    serializer_class = CommessaSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,)
    filter_class = CommessaFilter
    search_fields = ('cliente__ragione_sociale', 'cliente__cognome')
    pagination_class = DefaultPagination

    # filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    # filter_class = StepPercorsoEsecuzioneFilter
    # ordering_fields = ('id', 'esecuzione', 'stepPercorso')


    def get_permissions(self):
        # elenco commesse --> list
        # dettagli commessa --> retrieve
        # costi commessa --> get_costi
        return (MyCustomPerm('commessa', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # perform_create is called before the model of this view is saved.

        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        next_codice = Commessa.objects.next_codice()
        instance = serializer.save(codice=next_codice)
        return super(CommessaViewSet, self).perform_create(serializer)

    @detail_route()
    def get_costi(self, request, pk=None):
        consuntivi = Consuntivo.objects.getByCommessa(pk)
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
                'importo': importo,
                'note': c.note
                })
        risultato = {
            'consuntivi': my_list,
            'totali': {
                'totale_ore': totale_ore,
                'totale_importi': totale_importi
            }
        }
        return Response(risultato, status=status.HTTP_200_OK)

    @detail_route()
    def get_file(self, request, pk=None):
        """
        Restituisce l'elenco dei file pubblici e privati relativi a questa commessa
        """
        commessa = Commessa.objects.get(pk=pk)

        files = {
            'pubblici': commessa.get_file_pubblici()
        }
        if request.user.has_perm('anagrafiche._commessa:get_file_privato'):
            files['privati'] = commessa.get_file_privati()
        else:
            files['privati'] = []
        return Response(files, status=status.HTTP_200_OK)

    @detail_route()
    def get_file_pubblico(self, request, pk=None,):
        commessa = Commessa.objects.get(pk=pk)
        nome_file = request.GET.get('nome_file')
        path_file = commessa.get_percorso_file_pubblico(nome_file)
        try:
            my_file = open(path_file, 'rb')
            response = HttpResponse(my_file, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(nome_file) 
            return response
        except FileNotFoundError:
            return Response({"non_field_errors": "Il file richiesto non esiste"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route()
    def get_file_privato(self, request, pk=None,):
        # in questo caso il controllo sui permessi è fatto da django rest framework
        commessa = Commessa.objects.get(pk=pk)
        nome_file = request.GET.get('nome_file')
        path_file = commessa.get_percorso_file_privato(nome_file)
        try:
            my_file = open(path_file, 'rb')
            response = HttpResponse(my_file, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(nome_file) 
            return response
        except FileNotFoundError:
            return Response({"non_field_errors": "Il file richiesto non esiste"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def upload_file(self, request, pk=None,):
        commessa = Commessa.objects.get(pk=pk)
        nome_file = request.FILES['myfile'].name
        privato = request.POST.get('privato')
        if privato == "true" and not request.user.has_perm('anagrafiche._commessa:get_file_privato'):
            return Response({"non_field_errors": "Non hai i permessi necessari per caricare un file privato."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        file_content = ContentFile( request.FILES['myfile'].read() )
        result = commessa.scrivi_file(nome_file, privato, file_content)
        if result:
            return Response("creato", status=status.HTTP_200_OK)
        else:
            return Response({"non_field_errors": "Il file richiesto non esiste"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def delete_file(self, request, pk=None,):
        commessa = Commessa.objects.get(pk=pk)
        nome_file = request.POST.get('nome_file')
        privato = request.POST.get('privato')
        user = request.user
        if privato == "true" and not user.has_perm('anagrafiche._commessa:get_file_privato'):
            return Response({"non_field_errors": "Non hai i permessi necessari per cancellare questo file."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        result = commessa.cancella_file(nome_file, privato)
        if result:
            return Response("cancellato", status=status.HTTP_200_OK)
        else:
            return Response({"non_field_errors": "File non cancellato."}, status=status.HTTP_400_BAD_REQUEST)


class DipendenteViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Dipendente.objects.non_cancellati()
    serializer_class = DipendenteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('attivo',)

    def get_permissions(self):
        return (MyCustomPerm('dipendente', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    @list_route()
    def get_ore(self, request):
        da = request.GET.get('da', None)
        a = request.GET.get('a', None)
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
        return Response(my_list, status=status.HTTP_200_OK)


class TipoLavoroViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TipoLavoro.objects.all()
    serializer_class = TipoLavoroSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (permissions.AllowAny,)


class ConsuntivoViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Consuntivo.objects.non_cancellati()
    serializer_class = ConsuntivoSerializer

    def get_permissions(self):
        return (MyCustomPerm('consuntivo', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()


class ClasseArticoloViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ClasseArticolo.objects.all()
    serializer_class = ClasseArticoloSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (permissions.AllowAny,)


class TipoMovimentoViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TipoMovimento.objects.all().order_by('id')
    serializer_class = TipoMovimentoSerializer
    permission_classes = (permissions.AllowAny,)


class ArticoloViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Articolo.objects.non_cancellati()
    serializer_class = ArticoloSerializer

    def get_permissions(self):
        return (MyCustomPerm('articolo', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        # perform_create is called before the model of this view is saved.

        # Ricordarsi di settare il campo 'codice' come read_only
        # nel serializer del modello 
        classe_articolo = serializer.validated_data['classe']
        sigla = classe_articolo.sigla
        next_codice = Articolo.objects.next_codice(sigla)
        instance = serializer.save(codice=next_codice)
        return super(ArticoloViewSet, self).perform_create(serializer)

    @list_route()
    def get_unita_di_misura(self, request):
        my_dict = [{'id':k, 'descrizione': v} for (k,v) in UNITA_MISURA_CHOICES]
        return Response(my_dict, status=status.HTTP_200_OK)


class GiacenzaViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Giacenza.objects.all()
    serializer_class = GiacenzaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = GiacenzaFilter

    def get_permissions(self):
        return (MyCustomPerm('giacenza', self.action) ,)

    """
    Visto che i record sono cancellati fisicamente dal db, non c'è bisogno di fare
    override di perform_destroy

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    visto che non c'è un campo codice non c'è bisogno di fare override di perform_create
    def perform_create(self, serializer):
        ...
    """


class MovimentoViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Movimento.objects.non_cancellati()
    serializer_class = MovimentoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MovimentoFilter

    def get_permissions(self):
        return (MyCustomPerm('movimento', self.action) ,)

    def perform_destroy(self, serializer):
        serializer.cancellato = True
        serializer.save()

    def perform_create(self, serializer):
        """
        Aggiorna la quantità mettendo il segno meno se il tipo movimento è uno scarico.
        """
        # perform_create is called before the model of this view is saved.
        tipo_movimento = serializer.validated_data['tipo_movimento']
        quantita_api = serializer.validated_data['quantita']
        articolo = serializer.validated_data['articolo']

        quantita_reale = Movimento.get_quantita_reale(quantita_api, tipo_movimento)
        instance = serializer.save(
            quantita=quantita_reale, 
            autore=self.request.user,
            unita_di_misura=articolo.get_unita_di_misura_display())
        # il ricalcolo della tabella giacenze e della scorta di magazzino è fatto dalla 
        # pre_save in models.py [TODO]

    def perform_update(self, serializer):
        """
        Aggiorna la quantità mettendo il segno meno se il tipo movimento è uno scarico.
        """
        tipo_movimento = serializer.validated_data['tipo_movimento']
        quantita_api = serializer.validated_data['quantita']
        quantita_reale = Movimento.get_quantita_reale(quantita_api, tipo_movimento)
        articolo = serializer.validated_data['articolo']
        instance = serializer.save(
            quantita=quantita_reale, 
            autore=self.request.user,
            unita_di_misura=articolo.get_unita_di_misura_display())
        # il ricalcolo della tabella giacenze e della scorta di magazzino è fatto dalla 
        # pre_save in models.py [TODO]


class AliquotaIVAViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AliquotaIVA.objects.all().order_by('descrizione')
    serializer_class = AliquotaIVASerializer
    # permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (permissions.AllowAny,)


########################################################################################################################
# Nested ViewSet:
########################################################################################################################
class ProprietarioContoCorrenteViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = ContoCorrente.objects.non_cancellati()
    serializer_class = ContoCorrenteSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita=Entita.objects.proprietario())
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class ProprietarioIndirizzoViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = Indirizzo.objects.non_cancellati()
    serializer_class = IndirizzoSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita=Entita.objects.proprietario())
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class ProprietarioContattoViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = Contatto.objects.non_cancellati()
    serializer_class = ContattoSerializer
    
    def list(self, request, entita_pk=None):
        queryset = self.queryset.filter(entita=Entita.objects.proprietario())
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class DipendenteConsuntivoViewSet(LoggingMixin, viewsets.ViewSet):
    queryset = Consuntivo.objects.non_cancellati()
    serializer_class = ConsuntivoSerializer
    
    def get_permissions(self):
        return (MyCustomPerm('dipendenteConsuntivo', self.action) ,)

    def list(self, request, dipendente_pk=None):
        kwargs = {
            'dipendente__id': dipendente_pk
        }
        da = request.GET.get('da', None)
        a = request.GET.get('a', None)
        if da:
            kwargs['data__gte'] = da
        if a:
            kwargs['data__lte'] = a
        queryset = self.queryset.filter(**kwargs)
        serializer = self.serializer_class(queryset, many=True)
        totale = queryset.aggregate(Sum('ore'))
        return Response({
            'consuntivi': serializer.data,
            'totale_ore': totale['ore__sum'] or 0
        })


"""
class AccountPostsViewSet(viewsets.ViewSet):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer

    def list(self, request, account_username=None):
        queryset = self.queryset.filter(author__username=account_username)
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)
"""

"""
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.order_by('-created_at')
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(), IsAuthorOfPost(),)

    def perform_create(self, serializer):
        #import pdb; pdb.set_trace()
        # perform_create is called before the model of this view is saved.
        instance = serializer.save(author=self.request.user)
        return super(PostViewSet, self).perform_create(serializer)
"""
