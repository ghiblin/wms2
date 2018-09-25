#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework_nested import routers
# from anagrafiche.api.apiViews import *
from anagrafiche.api.apiViewsClienti import *
from anagrafiche.api.apiViewsFornitori import *

router = routers.SimpleRouter()
router.register(r'tipoPagamento', TipoPagamentoViewSet)
router.register(r'proprietario', ProprietarioViewSet)
router.register(r'cliente', ClienteViewSet, 'cliente')
router.register(r'fornitore', FornitoreViewSet, 'fornitore')
router.register(r'contoCorrente', ContoCorrenteViewSet)
router.register(r'indirizzo', IndirizzoViewSet)
router.register(r'contatto', ContattoViewSet)
router.register(r'commessa', CommessaViewSet)
router.register(r'dipendente', DipendenteViewSet)
router.register(r'tipoLavoro', TipoLavoroViewSet)
router.register(r'consuntivo', ConsuntivoViewSet)
router.register(r'classeArticolo', ClasseArticoloViewSet)
router.register(r'tipoMovimento', TipoMovimentoViewSet)
router.register(r'articolo', ArticoloViewSet)
router.register(r'giacenza', GiacenzaViewSet)
router.register(r'movimento', MovimentoViewSet)
router.register(r'aliquotaIVA', AliquotaIVAViewSet)

# API che riguardano i clienti
router.register(r'preventivoCliente', PreventivoClienteViewSet)
router.register(r'rigaPreventivoCliente', RigaPreventivoClienteViewSet)
router.register(r'ordineCliente', OrdineClienteViewSet)
router.register(r'ordineClienteSenzaTotale', OrdineClienteSenzaTotaleViewSet, 'ordineclientesenzatotale')
router.register(r'rigaOrdineCliente', RigaOrdineClienteViewSet)
router.register(r'rigaOrdineClienteSenzaTotale', RigaOrdineClienteSenzaTotaleViewSet, 'rigaordineclientesenzatotale')
router.register(r'tipoCausaleTrasporto', TipoCausaleTrasportoViewSet)
router.register(r'tipoPorto', TipoPortoViewSet)
router.register(r'tipoTrasportoACura', TipoTrasportoACuraViewSet)
router.register(r'tipoAspettoEsteriore', TipoAspettoEsterioreViewSet)
router.register(r'bollaCliente', BollaClienteViewSet)
router.register(r'rigaBollaCliente', RigaBollaClienteViewSet)
router.register(r'fatturaCliente', FatturaClienteViewSet)
router.register(r'rigaFatturaCliente', RigaFatturaClienteViewSet)

# API che riguardano i fornitori
router.register(r'preventivoFornitore', PreventivoFornitoreViewSet)
router.register(r'rigaPreventivoFornitore', RigaPreventivoFornitoreViewSet)
router.register(r'ordineFornitore', OrdineFornitoreViewSet)
router.register(r'rigaOrdineFornitore', RigaOrdineFornitoreViewSet)
router.register(r'bollaFornitore', BollaFornitoreViewSet)
router.register(r'rigaBollaFornitore', RigaBollaFornitoreViewSet)
router.register(r'fatturaFornitore', FatturaFornitoreViewSet)
router.register(r'rigaFatturaFornitore', RigaFatturaFornitoreViewSet)

proprietario_router = routers.NestedSimpleRouter(router, r'proprietario', lookup='entita')
proprietario_router.register(r'contoCorrente', ProprietarioContoCorrenteViewSet)
proprietario_router.register(r'indirizzo', ProprietarioIndirizzoViewSet)
proprietario_router.register(r'contatto', ProprietarioContattoViewSet)

clienti_router = routers.NestedSimpleRouter(router, r'cliente', lookup='entita')
clienti_router.register(r'contoCorrente', ClienteContoCorrenteViewSet)
clienti_router.register(r'indirizzo', ClienteIndirizzoViewSet)
clienti_router.register(r'contatto', ClienteContattoViewSet)

fornitori_router = routers.NestedSimpleRouter(router, r'fornitore', lookup='entita')
fornitori_router.register(r'contoCorrente', FornitoreContoCorrenteViewSet)
fornitori_router.register(r'indirizzo', FornitoreIndirizzoViewSet)
fornitori_router.register(r'contatto', FornitoreContattoViewSet)

dipendenti_router = routers.NestedSimpleRouter(router, r'dipendente', lookup='dipendente')
dipendenti_router.register(r'consuntivo', DipendenteConsuntivoViewSet)

urlpatterns = patterns('',
                       url(r'^api/v1/', include(router.urls)),
                       url(r'^api/v1/', include(proprietario_router.urls)),
                       url(r'^api/v1/', include(clienti_router.urls)),
                       url(r'^api/v1/', include(fornitori_router.urls)),
                       url(r'^api/v1/', include(dipendenti_router.urls)),
                       url(r'^$', 'anagrafiche.views.home', name='home'),

                       url(r'^api/v1/login/$', LoginView.as_view(), name='loginAPI'),
                       url(r'^api/v1/logout/$', LogoutView.as_view(), name='logoutAPI'),

                       url(r'^login$', 'anagrafiche.views.loginView', name='login'),
                       url(r'^logout$', 'anagrafiche.views.logout_view', name='logout'),
                       url(r'^anagrafiche/', include('anagrafiche.urls')),

                       url(r'^admin/', include(admin.site.urls)), )
