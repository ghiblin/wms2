#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from anagrafiche.models import *


class Command(BaseCommand):
    """
    Creazione commessa 'MAGAZZINO' dove caricare i costi di acquisto del materiale.
    Ha id uguale a 0 e non deve essere selezionabile nei documenti dei clienti.
    La commessa 'VARIE' è uguale alla commessa MAGAZZINO, ma ha id -1.
    """

    args = ''
    help = 'Crea le commesse MAGAZZINO e VARIE.'

    def handle(self, *args, **options):
        proprietario = Entita.objects.proprietario()

        commessa_magazzino = Commessa.objects.filter(codice='MAGAZZINO', 
            cliente_id=proprietario.id)

        if commessa_magazzino:
            self.stdout.write('La commessa MAGAZZINO esisteva già. La aggiorno per sicurezza.')
            commessa_magazzino = commessa_magazzino[0]
        else:
            commessa_magazzino = Commessa()

        
        commessa_magazzino.id = 0
        commessa_magazzino.cliente_id = proprietario.id
        commessa_magazzino.codice = 'MAGAZZINO'
        commessa_magazzino.prodotto = 'MAGAZZINO'
        commessa_magazzino.save()
        self.stdout.write('Commessa MAGAZZINO creata o aggiornata.')
            

        commessa_varie = Commessa.objects.filter(codice='VARIE', 
            cliente_id=proprietario.id)

        if commessa_varie:
            self.stdout.write('La commessa VARIE esisteva già. La aggiorno per sicurezza.')
            commessa_varie = commessa_varie[0]
        else:
            commessa_varie = Commessa()

        
        commessa_varie.id = -1
        commessa_varie.cliente_id = proprietario.id
        commessa_varie.codice = 'VARIE'
        commessa_varie.prodotto = 'VARIE'
        commessa_varie.save()
        self.stdout.write('Commessa VARIE creata o aggiornata.')
