#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from anagrafiche.models import *


class Command(BaseCommand):
    """
    Correzione del codice delle fatture clienti generate all'inizio dell'anno.
    """

    args = ''
    help = 'Corregge il codice delle fatture cliente emesse con l\'anno corrente.'

    def handle(self, *args, **options):

        fatture = FatturaCliente.objects.filter(codice__icontains="FC17")
        print("Esco senza fare nulla, fatture gia corrette")
        return
        n = 0
        for fattura in fatture:
            n += 1
            print(fattura.codice)
            aaa = "FC16{:04}".format(int(fattura.codice[4:]) + 348)
            print(aaa)
            fattura.codice = aaa
            fattura.save()
            print()

        self.stdout.write('Corrette {} fatture'.format(n))

# Esempio per controllare l'output dello script:
# fatture = FatturaCliente.objects.all().values('codice').annotate(nn=Count('codice'))
# [ff['codice'] for ff in fatture if ff['nn'] >1]