#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
#from anagrafiche.models import *
#from random import randint
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    
    args = 'confermo'
    help = 'Crea i permessi nel database che servono alla nostra app. CANCELLA TUTTI GLI ALTRI PERMESSI!'

    def handle(self, *args, **options):
        if (len(args) != 1) or args[0] != 'confermo':
            raise CommandError('lanciare il comando seguito dalla stringa \'confermo\'. PERICOLO!!!!!!')
        verifica = args[0]
        
        # cancellazione dei permessi creati automaticamente da django
        permessi_da_cancellare = Permission.objects.exclude(codename__startswith='_')
        permessi_cancellati = permessi_da_cancellare.count()
        for p in permessi_da_cancellare:
            self.stdout.write('Cancello il permesso: \'{}\''.format(p) )
            p.delete()

        # estrai o crea l'utente 'ut'. in ogni caso assicuriamoci che l'utente non
        # abbia alcun permesso.
        ut, created = User.objects.get_or_create(username='ut')
        ut.set_password('ut')
        ut.save()
        
        # ut.user_permissions.all().delete()     
        # non vogliamo cancellare il recod dei permessi ma soltanto togliere quei permessi a ut
        ut.user_permissions.clear()

        # i nuovi permessi devono per forza essere associati ad un content type.
        # Si è deciso di usare sempre il content type del modello Entita, ma 
        # non c'è una ragione particolare per questa scelta.
        entita_content_type = ContentType.objects.get(model='entita')

        # il primo parametro indica il nome del permesso da creare; il secondo
        # indica se il parametro va assegnato all'utente 'ut'
        permessi_necessari = (
            ('proprietario:*', False),
            ('proprietario:list', True),
            ('proprietario:retrieve', True),
            ('cliente:*', True),
            ('cliente:list', True),
            ('cliente:retrieve', True),
            ('fornitore:*', True),
            ('contoCorrente:*', True),
            ('contoCorrenteCliente:*', True),
            ('contoCorrenteCliente:list', True),
            ('contoCorrenteCliente:retrieve', True),
            ('contoCorrenteFornitore:*', True),
            ('contoCorrenteProprietario:*', False),
            ('contoCorrenteProprietario:list', True),
            ('contoCorrenteProprietario:retrieve', True),
            ('indirizzo:*', True),
            ('indirizzo:get_tipo_sede', True),
            ('indirizzoCliente:*', True),
            ('indirizzoCliente:list', True),
            ('indirizzoCliente:retrieve', True),
            ('indirizzoFornitore:*', True),
            ('indirizzoProprietario:*', False),
            ('indirizzoProprietario:list', True),
            ('indirizzoProprietario:retrieve', True),
            ('contatto:*', True),
            ('contatto:get_tipo_contatto', True),
            ('contattoCliente:*', True),
            ('contattoCliente:list', True),
            ('contattoCliente:retrieve', True),
            ('contattoFornitore:*', True),
            ('contattoProprietario:*', False),
            ('contattoProprietario:list', True),
            ('contattoProprietario:retrieve', True),
            ('commessa:*', False),
            ('commessa:create', True),
            ('commessa:destroy', True),
            ('commessa:list', True),
            ('commessa:retrieve', True),
            ('commessa:update', True),
            ('commessa:get_file', True),
            ('commessa:get_file_privato', False),
            ('commessa:get_file_pubblico', True),
            ('commessa:upload_file', True),
            ('commessa:delete_file', True),
            ('commessa:get_costi', False),
            ('dipendente:*', False),
            ('dipendente:get_ore', True),
            ('dipendenteConsuntivo:*', True),
            ('consuntivo:*', True),
            ('articolo:*', True),
            ('giacenza:*', True),
            ('movimento:*', True),
            ('preventivoCliente:*', False),
            ('rigaPreventivoCliente:*', False),
            ('ordineCliente:*', False),
            ('rigaOrdineCliente:*', False),
            ('ordineClienteSenzaTotale:*', True),
            ('rigaOrdineClienteSenzaTotale:*', True),
            ('bollaCliente:*', True),
            ('rigaBollaCliente:*', True),
            ('fatturaCliente:*', False),
            ('rigaFatturaCliente:*', False),
            ('preventivoFornitore:*', True),
            ('rigaPreventivoFornitore:*', True),
            ('ordineFornitore:*', True),
            ('rigaOrdineFornitore:*', True),
            ('bollaFornitore:*', True),
            ('rigaBollaFornitore:*', True),
            ('fatturaFornitore:*', True),
            ('rigaFatturaFornitore:*', True),            

        )
        permessi_creati = 0
        permessi_ut = 0
        for (p, assegna_a_ut) in permessi_necessari:
            # crea il permesso se non esiste:            
            obj, created = Permission.objects.get_or_create(name=p, codename="_"+p, 
                content_type=entita_content_type)
            if created:
                self.stdout.write('Creato permesso: \'{}\''.format(p) )
                permessi_creati += 1
            if assegna_a_ut:
                ut.user_permissions.add(obj)
                self.stdout.write('Permesso \'{}\' aggiunto all\'utente ut'.format(p))
                permessi_ut += 1
            
        self.stdout.write('\nPermessi cancellati: {}.\n'.format(permessi_cancellati) )
        self.stdout.write('Permessi creati: {}.\n'.format(permessi_creati) )
        self.stdout.write('Permessi assegnati a ut: {}.\n\n'.format(permessi_ut) )

        # uso filter invece di get
        ut1 = User.objects.filter(username='ut1')
        ut2 = User.objects.filter(username='ut2')
        if (ut1 and ut2):
            ut1 = ut1[0]
            ut2 = ut2[0]
            n_ut1 = len(ut1.get_all_permissions())
            n_ut2 = len(ut2.get_all_permissions())
            self.stdout.write('Permessi assegnati a ut1: {}'.format(n_ut1))
            self.stdout.write('Permessi assegnati a ut2: {}'.format(n_ut1))
            self.stdout.write('Ogni cliente è libero di assegnare i permessi che '
                + 'vuole. Per Mr. Ferro i permessi di ut1 e ut2 dovrebbero coincidere' 
                + ' con quelli di ut.\n\n')



        self.stdout.write('NB: all\'inizio dello script all\'utente ut vengono tolti ' 
            + 'tutti i permessi che ha e poi ricreati.')

        self.stdout.write('NB2: non sono sicuro al 100% che sia indispensabile, ma '
            + 'ora conviene riavviare il server!!')

        self.stdout.write('\nFine aggiornamento permessi.\n' )



"""
modelli che non hanno bisogno di permessi perché sono solo dizionari:

TipoPagamento
TipoLavoro
ClasseArticolo
AliquotaIVA
TipoCausaleTrasporto
TipoPorto
TipoTrasportoACura
TipoAspettoEsteriore

"""

