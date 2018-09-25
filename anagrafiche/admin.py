#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin
from anagrafiche.models import *
from django.contrib.auth.models import Permission

class EntitaAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'is_owner', 'is_client', 'is_supplier')


class ContoCorrenteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato',)


class IndirizzoAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'tipo', 'entita')


class ContattoAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'tipo', 'entita')


class CommessaAdmin(admin.ModelAdmin):
    list_filter = ('cancellato',)


class DipendenteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato',)


class ConsuntivoAdmin(admin.ModelAdmin):
    list_filter = ( 'dipendente', 'cancellato', 'tipo_lavoro')


class ArticoloAdmin(admin.ModelAdmin):
    list_filter = ( 'classe', 'cancellato', 'unita_di_misura')


class GiacenzaAdmin(admin.ModelAdmin):
    list_filter = ( 'articolo',)


class MovimentoAdmin(admin.ModelAdmin):
    list_filter = ( 'tipo_movimento',)


class PreventivoClienteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'accettato', 'cliente')


class RigaPreventivoClienteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'accettata', 'preventivo')


class OrdineClienteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'bollettato', 'fatturato', 'cliente')


class RigaOrdineClienteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'bollettata', 'fatturata', 'ordine')


class BollaClienteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'fatturata', 'cliente')


class RigaBollaClienteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'fatturata', 'bolla')


class FatturaClienteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'cliente')


class RigaFatturaClienteAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'fattura')

######### Fornitori:
class PreventivoFornitoreAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'accettato', 'fornitore')


class RigaPreventivoFornitoreAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'accettata', 'preventivo')


class OrdineFornitoreAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'bollettato', 'fatturato', 'fornitore')


class RigaOrdineFornitoreAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'bollettata', 'fatturata', 'ordine')


class BollaFornitoreAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'fatturata', 'fornitore')


class RigaBollaFornitoreAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'fatturata', 'bolla')


class FatturaFornitoreAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'fornitore')


class RigaFatturaFornitoreAdmin(admin.ModelAdmin):
    list_filter = ('cancellato', 'fattura')


admin.site.register(TipoPagamento)
admin.site.register(Entita, EntitaAdmin)
admin.site.register(ContoCorrente, ContoCorrenteAdmin)
admin.site.register(Indirizzo, IndirizzoAdmin)
admin.site.register(Contatto, ContattoAdmin)
admin.site.register(Commessa, CommessaAdmin)
admin.site.register(Dipendente, DipendenteAdmin)
admin.site.register(Consuntivo, ConsuntivoAdmin)
admin.site.register(TipoLavoro)
admin.site.register(ClasseArticolo)
admin.site.register(TipoMovimento)
admin.site.register(Articolo, ArticoloAdmin)
admin.site.register(Giacenza, GiacenzaAdmin)
admin.site.register(Movimento, MovimentoAdmin)
admin.site.register(AliquotaIVA)
admin.site.register(PreventivoCliente, PreventivoClienteAdmin)
admin.site.register(RigaPreventivoCliente, RigaPreventivoClienteAdmin)
admin.site.register(OrdineCliente, OrdineClienteAdmin)
admin.site.register(RigaOrdineCliente, RigaOrdineClienteAdmin)
admin.site.register(BollaCliente, BollaClienteAdmin)
admin.site.register(RigaBollaCliente, RigaBollaClienteAdmin)
admin.site.register(FatturaCliente, FatturaClienteAdmin)
admin.site.register(RigaFatturaCliente, RigaFatturaClienteAdmin)

admin.site.register(PreventivoFornitore, PreventivoFornitoreAdmin)
admin.site.register(RigaPreventivoFornitore, RigaPreventivoFornitoreAdmin)
admin.site.register(OrdineFornitore, OrdineFornitoreAdmin)
admin.site.register(RigaOrdineFornitore, RigaOrdineFornitoreAdmin)
admin.site.register(BollaFornitore, BollaFornitoreAdmin)
admin.site.register(RigaBollaFornitore, RigaBollaFornitoreAdmin)
admin.site.register(FatturaFornitore, FatturaFornitoreAdmin)
admin.site.register(RigaFatturaFornitore, RigaFatturaFornitoreAdmin)


admin.site.register(TipoCausaleTrasporto)
admin.site.register(TipoPorto)
admin.site.register(TipoTrasportoACura)
admin.site.register(TipoAspettoEsteriore)

admin.site.register(Permission)