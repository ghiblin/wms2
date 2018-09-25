#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from rest_framework import permissions
from django.contrib.auth.models import Permission

#logger = logging.getLogger(__name__)
logger = logging.getLogger('django')

class MyCustomPerm(permissions.BasePermission):
    nomeModello = None
    azione = None

    def __init__(self, nomeModello, azione):
        self.nomeModello = nomeModello
        self.azione = azione

    def check_wms_permission(self, u):
        # print ("{}:{}".format(self.nomeModello, self.azione))
        # codice può valore 'commessa:list', 'commessa:retrieve', 'commessa:*', ecc.
        codice = "{}:{}".format(self.nomeModello, self.azione)

        
        logger.info('Controllo se esiste permesso \'{}\''.format(codice))

        codice_specifico_esiste = Permission.objects.filter(name=codice).exists()
        if not codice_specifico_esiste:
            codice_specifico = codice
            # usa il codice generico del modello
            codice = "{}:*".format(self.nomeModello)
            logger.info('Permesso specifico \'{}\' non esiste, uso permesso generico: \'{}\''.format(codice_specifico, codice))

        result = u.has_perm('anagrafiche._{}'.format(codice))
        logger.info('Utente {} ha permesso \'{}\'? {}'.format(u, codice, result))
        return result 


    def has_permission(self, request, view):
        # import pdb; pdb.set_trace()
        u = request.user
        if u.is_superuser or settings.SKIP_PERMISSION_CHECK:
            logger.info('controllo permesso saltato')
            return True
        return self.check_wms_permission(u)



    def has_object_permission(self, request, view, obj):
        #import pdb; pdb.set_trace()
        if self.nomeModello in ('indirizzo', 'contoCorrente', 'contatto'):
            u = request.user
            if obj.entita.is_client:
                self.nomeModello = self.nomeModello + "Cliente"
            elif obj.entita.is_supplier:
                self.nomeModello = self.nomeModello + "Fornitore"
            elif obj.entita.is_owner:
                self.nomeModello = self.nomeModello + "Proprietario"
            else:
                # error
                1/0
            return self.check_wms_permission(u)

        return True