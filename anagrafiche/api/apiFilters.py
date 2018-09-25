#!/usr/bin/python
# -*- coding: utf-8 -*-

import django_filters

from anagrafiche.models import *


class GiacenzaFilter(django_filters.FilterSet):

    class Meta:
        model = Giacenza
        fields = ('lotto', 'lotto__codice', 'articolo', 'lotto__commessa', 'lotto__commessa__codice')


class MovimentoFilter(django_filters.FilterSet):
    data_da = django_filters.MethodFilter(action='filtra_da')
    data_a = django_filters.MethodFilter(action='filtra_a')

    class Meta:
        model = Movimento
        fields = ('articolo', 'articolo__codice', 'lotto', 'lotto__codice', 'data_da', 'data_a', \
            'tipo_movimento', 'autore', 'destinazione', 'destinazione__codice')        

    def filtra_da(self, queryset, value):
        """
        Applica il filtro sul campo 'data' 
        """
        value = value + "T00:00:00Z"
        return queryset.filter(data__gte=value)

    def filtra_a(self, queryset, value):
        """
        Applica il filtro sul campo 'data'
        """
        value = value + "T23:59:59Z"
        return queryset.filter(data__lte=value)



class CommessaFilter(django_filters.FilterSet):
    # Non posso definire i filtri 'da' e 'a' sul campo 'data_apertura' con 
    # il metodo classico:
    #     da = django_filters.DateFilter(name='data_apertura', lookup_type='gte')
    #     a = django_filters.DateFilter(name='data_apertura', lookup_type='lte')
    # perché se viene passato anche il filtro 'codice' allora questi due
    # filtri devono essere ignorati. Quindi li definisco come MethodFilter:
    da = django_filters.MethodFilter(action='filtra_da')
    a = django_filters.MethodFilter(action='filtra_a')
    ## il nome del cliente è memorizzato nel campo 'ragione_sociale' se si tratta di una
    ## persona giuridica e nei campi 'nome' e 'cognome' se si tratta di una persona fisica.
    ## Quindi non posso usare un CharFilter. Aggiungo il SearchFilter in apiViews.py.
    # nome_cliente = django_filters.CharFilter(name="cliente__nome", lookup_type="icontains")

    class Meta:
        model = Commessa
        fields = ('da', 'a', 'codice', 'cliente' )

    
    def filtra_da(self, queryset, value):
        """
        Applica il filtro sul campo 'data_apertura' solo se il filtro 'codice'
        non è valorizzato.
        """
        if 'codice' not in self.data:
            return queryset.filter(data_apertura__gte=value)
        else:
            return queryset

    def filtra_a(self, queryset, value):
        """
        Applica il filtro sul campo 'data_apertura' solo se il filtro 'codice'
        non è valorizzato.
        """
        if 'codice' not in self.data:
            return queryset.filter(data_apertura__lte=value)
        else:
            return queryset

    #&a=2015-09-10



class PreventivoClienteFilter(django_filters.FilterSet):
    da = django_filters.DateFilter(name='data', lookup_type='gte')
    a = django_filters.DateFilter(name='data', lookup_type='lte')
    con_righe = django_filters.MethodFilter(action='filtra_righe')

    class Meta:
        model = PreventivoCliente
        fields = ('codice', 'cliente', 'accettato', 'da', 'a', 'con_righe')

    def filtra_righe(self, queryset, value):
        # il campo generato da extra non può essere filtrato da filter(),
        # quindi per restituire un queryset mi tocca creare una lista di
        # id ed eseguire un'altra query
        qs = queryset.extra(select={"n_righe_valide": "select count(*) from anagrafiche_rigapreventivocliente where anagrafiche_preventivocliente.id = anagrafiche_rigapreventivocliente.preventivo_id and not anagrafiche_rigapreventivocliente.cancellato"})
        ids = []
        for p in qs:
            if p.n_righe_valide > 0:
                ids.append(p.id)
        return PreventivoCliente.objects.filter(id__in=ids)


class OrdineClienteFilter(django_filters.FilterSet):
    da = django_filters.DateFilter(name='data', lookup_type='gte')
    a = django_filters.DateFilter(name='data', lookup_type='lte')
    con_righe = django_filters.MethodFilter(action='filtra_righe')

    class Meta:
        model = OrdineCliente
        fields = ('codice', 'cliente', 'bollettato', 'fatturato', 
            'da', 'a', 'con_righe')

    def filtra_righe(self, queryset, value):
        # il campo generato da extra non può essere filtrato da filter(),
        # quindi per restituire un queryset mi tocca creare una lista di
        # id ed eseguire un'altra query
        qs = queryset.extra(select={"n_righe_valide": "select count(*) from anagrafiche_rigaordinecliente where anagrafiche_ordinecliente.id = anagrafiche_rigaordinecliente.ordine_id and not anagrafiche_rigaordinecliente.cancellato"})
        ids = []
        for p in qs:
            if p.n_righe_valide > 0:
                ids.append(p.id)
        return OrdineCliente.objects.filter(id__in=ids)


class BollaClienteFilter(django_filters.FilterSet):
    da = django_filters.DateFilter(name='data', lookup_type='gte')
    a = django_filters.DateFilter(name='data', lookup_type='lte')
    con_righe = django_filters.MethodFilter(action='filtra_righe')

    class Meta:
        model = BollaCliente
        fields = ('codice', 'cliente', 'fatturata', 'da', 'a', 'con_righe')

    def filtra_righe(self, queryset, value):
        # il campo generato da extra non può essere filtrato da filter(),
        # quindi per restituire un queryset mi tocca creare una lista di
        # id ed eseguire un'altra query
        qs = queryset.extra(select={"n_righe_valide": "select count(*) from anagrafiche_rigabollacliente where anagrafiche_bollacliente.id = anagrafiche_rigabollacliente.bolla_id and not anagrafiche_rigabollacliente.cancellato"})
        ids = []
        for p in qs:
            if p.n_righe_valide > 0:
                ids.append(p.id)
        return BollaCliente.objects.filter(id__in=ids)


class FatturaClienteFilter(django_filters.FilterSet):
    da = django_filters.DateFilter(name='data', lookup_type='gte')
    a = django_filters.DateFilter(name='data', lookup_type='lte')

    class Meta:
        model = FatturaCliente
        fields = ('codice', 'cliente', 'da', 'a')

######################################## Fornitori: 

class PreventivoFornitoreFilter(django_filters.FilterSet):
    da = django_filters.DateFilter(name='data', lookup_type='gte')
    a = django_filters.DateFilter(name='data', lookup_type='lte')
    con_righe = django_filters.MethodFilter(action='filtra_righe')

    class Meta:
        model = PreventivoFornitore
        fields = ('codice', 'fornitore', 'accettato', 'da', 'a', 'con_righe')

    def filtra_righe(self, queryset, value):
        # il campo generato da extra non può essere filtrato da filter(),
        # quindi per restituire un queryset mi tocca creare una lista di
        # id ed eseguire un'altra query
        qs = queryset.extra(select={"n_righe_valide": "select count(*) from anagrafiche_rigapreventivofornitore where anagrafiche_preventivofornitore.id = anagrafiche_rigapreventivofornitore.preventivo_id and not anagrafiche_rigapreventivofornitore.cancellato"})
        ids = []
        for p in qs:
            if p.n_righe_valide > 0:
                ids.append(p.id)
        return PreventivoFornitore.objects.filter(id__in=ids)


class OrdineFornitoreFilter(django_filters.FilterSet):
    da = django_filters.DateFilter(name='data', lookup_type='gte')
    a = django_filters.DateFilter(name='data', lookup_type='lte')
    con_righe = django_filters.MethodFilter(action='filtra_righe')

    class Meta:
        model = OrdineFornitore
        fields = ('codice', 'fornitore', 'bollettato', 'fatturato', 
            'da', 'a', 'con_righe')

    def filtra_righe(self, queryset, value):
        # il campo generato da extra non può essere filtrato da filter(),
        # quindi per restituire un queryset mi tocca creare una lista di
        # id ed eseguire un'altra query
        qs = queryset.extra(select={"n_righe_valide": "select count(*) from anagrafiche_rigaordinefornitore where anagrafiche_ordinefornitore.id = anagrafiche_rigaordinefornitore.ordine_id and not anagrafiche_rigaordinefornitore.cancellato"})
        ids = []
        for p in qs:
            if p.n_righe_valide > 0:
                ids.append(p.id)
        return OrdineFornitore.objects.filter(id__in=ids)


class BollaFornitoreFilter(django_filters.FilterSet):
    da = django_filters.DateFilter(name='data', lookup_type='gte')
    a = django_filters.DateFilter(name='data', lookup_type='lte')
    con_righe = django_filters.MethodFilter(action='filtra_righe')
    articolo = django_filters.MethodFilter(action='filtra_articolo')

    class Meta:
        model = BollaFornitore
        fields = ('codice', 'fornitore', 'fatturata', 'da', 'a', 'con_righe', 'articolo')

    def filtra_righe(self, queryset, value):
        # il campo generato da extra non può essere filtrato da filter(),
        # quindi per restituire un queryset mi tocca creare una lista di
        # id ed eseguire un'altra query
        qs = queryset.extra(select={"n_righe_valide": "select count(*) from anagrafiche_rigabollafornitore where anagrafiche_bollafornitore.id = anagrafiche_rigabollafornitore.bolla_id and not anagrafiche_rigabollafornitore.cancellato"})
        ids = []
        for p in qs:
            if p.n_righe_valide > 0:
                ids.append(p.id)
        return BollaFornitore.objects.filter(id__in=ids)

    def filtra_articolo(self, queryset, value):
        qs = queryset.extra(select={"articolo": "select count(*) from anagrafiche_rigabollafornitore where anagrafiche_bollafornitore.id = anagrafiche_rigabollafornitore.bolla_id and not anagrafiche_rigabollafornitore.cancellato and anagrafiche_rigabollafornitore.articolo_id = %s"%(value)})
        ids = []
        for p in qs:
            if p.articolo > 0:
                ids.append(p.id)
        return BollaFornitore.objects.filter(id__in=ids)

class FatturaFornitoreFilter(django_filters.FilterSet):
    da = django_filters.DateFilter(name='data', lookup_type='gte')
    a = django_filters.DateFilter(name='data', lookup_type='lte')

    class Meta:
        model = FatturaFornitore
        fields = ('codice', 'fornitore', 'da', 'a')
