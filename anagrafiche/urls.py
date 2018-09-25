#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'anagrafiche.views.home', name='home'),
    url(r'^menu$', 'anagrafiche.views.menu', name='menu'),
    url(r'^status$', 'anagrafiche.views.status', name='status'),

    url(r'^stampa/commessa/(\d+)/$', 'anagrafiche.stampe.commessa.crea_xls_commessa',
        name='crea-xls-commessa'),
    url(r'^stampa/consuntivi/$', 'anagrafiche.stampe.consuntivi.crea_xls_consuntivi',
        name='crea-xls-consuntivi'),

    url(r'^stampa/preventivoCliente/(\d+)/$', 'anagrafiche.stampe.preventivi.crea_xls_preventivo_cliente',
        name='crea-xls-preventivo-cliente'),
    url(r'^stampa/ordineCliente/(\d+)/$', 'anagrafiche.stampe.ordini.crea_xls_ordine_cliente',
        name='crea-xls-ordine-cliente'),
    url(r'^stampa/bollaCliente/(\d+)/$', 'anagrafiche.stampe.bolle.crea_xls_bolla_cliente',
        name='crea-xls-bolla-cliente'),
    url(r'^stampa/fatturaCliente/(\d+)/$', 'anagrafiche.stampe.fatture.crea_xls_fattura_cliente',
        name='crea-xls-fattura-cliente'),
    
    url(r'^stampa/preventivoFornitore/(\d+)/$', 'anagrafiche.stampe.preventivi.crea_xls_preventivo_fornitore',
        name='crea-xls-preventivo-fornitore'),
    url(r'^stampa/ordineFornitore/(\d+)/$', 'anagrafiche.stampe.ordini.crea_xls_ordine_fornitore',
        name='crea-xls-ordine-fornitore'),
    url(r'^stampa/bollaFornitore/(\d+)/$', 'anagrafiche.stampe.bolle.crea_xls_bolla_fornitore',
        name='crea-xls-bolla-fornitore'),
    # fatturaFornitore non va stampata.

    url(r'^pdf/preventivoCliente/(\d+)/$', 'anagrafiche.stampe.pdfUtils.crea_pdf_preventivo_cliente',
        name='crea-pdf-preventivo-cliente'),
    url(r'^testSergio$', 'anagrafiche.views.testSergio', name='testSergio'),
)

# non è possibile inserire dei commenti multilinea nei file urls.py, quindi uso una 
# nuova variabile per escludere gli url che volevo cancellare.
patterns_cancellati = (
    url(r'^clienti$', 'anagrafiche.views.clienti', name='clienti'),
    url(r'^cliente$', 'anagrafiche.views.cliente', name='cliente'),
    url(r'^cliente/(\d+)$', 'anagrafiche.views.cliente', name='cliente'),
    url(r'^cliente/(\d+)/elimina$', 'anagrafiche.views.eliminaCliente', name='eliminaCliente'),

    url(r'^contiCorrenti$', 'anagrafiche.views.contiCorrenti', name='contiCorrenti'),
    url(r'^contoCorrente$', 'anagrafiche.views.contoCorrente', name='contoCorrente'),
    url(r'^contoCorrente/(\d+)$', 'anagrafiche.views.contoCorrente', name='contoCorrente'),
    url(r'^contoCorrente/(\d+)/elimina$', 'anagrafiche.views.eliminaContoCorrente', 
        name='eliminaContoCorrente'),
    
    url(r'^commesse$', 'anagrafiche.views.commesse', name='commesse'),
    url(r'^commesseJSON$', 'anagrafiche.views.commesseJSON', name='commesseJSON'),
    url(r'^commessa$', 'anagrafiche.views.commessa', name='commessa'),
    url(r'^commessa/(\d+)$', 'anagrafiche.views.commessa', name='commessa'),
    url(r'^commessa/(\d+)/elimina$', 'anagrafiche.views.eliminaCommessa', name='eliminaCommessa'),

    url(r'^dipendenti$', 'anagrafiche.views.dipendenti', name='dipendenti'),
    url(r'^dipendente$', 'anagrafiche.views.dipendente', name='dipendente'),
    url(r'^dipendente/(\d+)$', 'anagrafiche.views.dipendente', name='dipendente'),
    url(r'^dipendente/(\d+)/elimina$', 'anagrafiche.views.eliminaDipendente', name='eliminaDipendente'),

    url(r'^dipendente/(\d+)/consuntivi$', 'anagrafiche.views.consuntiviDipendente', name='consuntiviDipendente'),
    url(r'^dipendentiEOre$', 'anagrafiche.views.dipendentiEOre', name='dipendentiEOre'),

    url(r'^consuntivi$', 'anagrafiche.views.consuntivi', name='consuntivi'),
    url(r'^consuntivo$', 'anagrafiche.views.consuntivo', name='consuntivo'),
    url(r'^consuntivo/(\d+)$', 'anagrafiche.views.consuntivo', name='consuntivo'),
    url(r'^consuntivo/(\d+)/elimina$', 'anagrafiche.views.eliminaConsuntivo', name='eliminaConsuntivo'),
    url(r'^costiCommessa$', 'anagrafiche.views.costiCommessa', name='costiCommessa'),
    url(r'^costiCommessa/(\d+)$', 'anagrafiche.views.costiCommessaSpecifica', name='costiCommessaSpecifica'),

    url(r'^tipiLavoroJSON$', 'anagrafiche.views.tipiLavoroJSON', name='tipiLavoroJSON'),
)
