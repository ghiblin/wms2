#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os import listdir
from os.path import isfile, join
from datetime import datetime, date
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Sum, Max, signals
from django.contrib.auth.models import User
# from django.http import HttpResponse
from anagrafiche.api.apiExceptions import WmsValidationError


DIRECTORY_PUBBLICA = 'pubblica'
DIRECTORY_PRIVATA = 'privata'

PERSONA_FISICA = 'F'
PERSONA_GIURIDICA = 'G'
TIPO_PERSONA_CHOICES = (
    (PERSONA_FISICA, 'Persona fisica'),
    (PERSONA_GIURIDICA, 'Persona giuridica'),
)

# E' sbagliato fare bolle fornitori indicando come destinazione la sede di un cliente di Mr. Ferro. Però
# gli utenti lo fanno lo stesso e quindi tanto vale permettergli di indicare la sede da programma senza dover
# modificare a mano il file excel.
SEDE_LEGALE = 'L'
SEDE_OPERATIVA = 'O'
SEDE_AMMINISTRATIVA = 'A'
SEDE_CANTIERE = 'C'
SEDE_CLIENTE = 'X'
TIPO_SEDE_CHOICES = (
    (SEDE_LEGALE, 'Sede legale'),
    (SEDE_OPERATIVA, 'Sede operativa'),
    (SEDE_AMMINISTRATIVA, 'Sede amministrativa'),
    (SEDE_CANTIERE, 'Cantiere'),
    (SEDE_CLIENTE, 'Sede cliente'),
)

CONTATTO_TEL_UFFICIO = 'U'
CONTATTO_TEL_ABITAZIONE = 'A'
CONTATTO_CELLULARE = 'C'
CONTATTO_EMAIL = 'E'
CONTATTO_EMAIL_FATTURAZIONE = 'T'
CONTATTO_FAX = 'F'
CONTATTO_PERSONALIZZATO = 'P'
TIPO_CONTATTO_CHOICES = (
    (CONTATTO_TEL_UFFICIO, 'Telefono ufficio'),
    (CONTATTO_TEL_ABITAZIONE, 'Telefono abitazione'),
    (CONTATTO_CELLULARE, 'Cellulare'),
    (CONTATTO_EMAIL, 'Email'),
    (CONTATTO_EMAIL_FATTURAZIONE, 'Email fatturazione'),
    (CONTATTO_FAX, 'Fax'),
    (CONTATTO_PERSONALIZZATO, 'Personalizzato'),
)

UNITA_MISURA_METRI = 'ME'
UNITA_MISURA_METRI_QUADRATI = 'M2'
UNITA_MISURA_CENTIMETRI = 'CM'
UNITA_MISURA_MILLIMETRI = 'MM'
UNITA_MISURA_CHILI = 'KG'
UNITA_MISURA_ETTI = 'HG'
UNITA_MISURA_LITRI = 'LI'
UNITA_MISURA_MILLILITRI = 'ML'
UNITA_MISURA_SCATOLE = 'SC'
UNITA_MISURA_PEZZI = 'PZ'
UNITA_MISURA_NUMERO = 'NR'
UNITA_MISURA_CHOICES = (
    (UNITA_MISURA_PEZZI, 'pz'),
    (UNITA_MISURA_NUMERO, 'n.'),
    (UNITA_MISURA_SCATOLE, 'sc'),
    (UNITA_MISURA_METRI, 'm'),
    (UNITA_MISURA_METRI_QUADRATI, 'm²'),   # per l'esponente AltGr + 2 
    (UNITA_MISURA_CENTIMETRI, 'cm'),
    (UNITA_MISURA_MILLIMETRI, 'mm'),
    (UNITA_MISURA_CHILI, 'kg'),
    (UNITA_MISURA_ETTI, 'hg'),
    (UNITA_MISURA_LITRI, 'l'),
    (UNITA_MISURA_MILLILITRI, 'ml'),
)

# prefissi usati nei codici delle tabelle
CLIENTE_PREFIX = "C"
FORNITORE_PREFIX = "F"
PREVENTIVO_CLIENTE_PREFIX = 'PC'
ORDINE_CLIENTE_PREFIX = 'OC'
BOLLA_CLIENTE_PREFIX = 'BC'
FATTURA_CLIENTE_PREFIX = 'FC'
PREVENTIVO_FORNITORE_PREFIX = 'PF'
ORDINE_FORNITORE_PREFIX = 'OF'
BOLLA_FORNITORE_PREFIX = 'BF'
FATTURA_FORNITORE_PREFIX = 'FF'


PERSONA_DI_RIFERIMENTO_LENGTH = 150
RIFERIMENTO_CLIENTE_LENGTH = 150


class TipoPagamento(models.Model):
    descrizione = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.descrizione

    class Meta:
        verbose_name_plural = "tipi pagamento"
        ordering = ('id', )


class EntitaManager(models.Manager):
    def clienti(self):
        return self.filter(is_client=True, cancellato=False)

    def fornitori(self):
        return self.filter(is_supplier=True, cancellato=False)

    def proprietario(self):
        return self.get(is_owner=True)

    def proprietario_exists(self):
        return self.filter(is_owner=True).exists()

    def next_codice(self, sigla):
        # restituisce il codice più grande già presente nel db, aumentato di 1
        aggr_max = self.filter(codice__startswith=sigla).aggregate(Max('codice'))
        max_str = aggr_max['codice__max']
        if max_str:
            max_int = int(max_str[len(sigla):])
        else:
            max_int = 0
        next_codice = "{0}{1:04d}".format(sigla, max_int+1)
        return next_codice


class Entita(models.Model):
    codice = models.CharField(max_length=30)
    is_client = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    tipo = models.CharField(max_length=1, choices=TIPO_PERSONA_CHOICES, \
        default=PERSONA_GIURIDICA)
    nome = models.CharField(max_length=40, null=True, blank=True)
    cognome = models.CharField(max_length=40, null=True, blank=True)
    ragione_sociale = models.CharField(max_length=120, null=True, blank=True)
    codice_fiscale = models.CharField(max_length=16, null=True, blank=True)
    partita_iva = models.CharField(max_length=12, default="", null=True, blank=True)
    # TODO: mettere unique = True! dopo il deploy sul server !!
    cancellato = models.BooleanField(default=False)
    pagamento = models.ForeignKey(TipoPagamento, default=1)
    vettore = models.BooleanField(default=False)
    persona_di_riferimento = models.CharField(max_length=150, null=True, blank=True)
    costo_riba = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    straniero = models.BooleanField(default=False)
    objects = EntitaManager()

    def get_nome_completo(self):
        if self.tipo == PERSONA_FISICA:
            return "{} {}".format(self.nome, self.cognome)
        else:
            return self.ragione_sociale

    def get_indirizzi(self):
        return self.indirizzi.filter(cancellato=False)

    def get_contatti(self):
        return self.contatti.filter(cancellato=False)

    def get_conti_correnti(self):
        return self.conti_correnti.filter(cancellato=False)

    def get_contatto(self, tipo):
        """
        Restituisce il primo contatto non cancellato associato ad una entità
        e del tipo richiesto.
        """
        result = ''
        numeri = self.contatti.filter(tipo=tipo, cancellato=False)
        if numeri.count() > 0:
            result = numeri[0].valore
        return result

    def get_indirizzo(self, tipo, lunghezza_indirizzo='corto'):
        """
        Recupera un indirizzo non cancellato, del tipo passato come parametro e 
        associato all'entità.
        """
        indirizzi = self.indirizzi.filter(tipo=tipo, cancellato=False)
        if indirizzi.count() > 0:
            if lunghezza_indirizzo == 'medio':
                return indirizzi[0].get_indirizzo_medio()
            elif lunghezza_indirizzo == 'su_due_righe_con_cap':
                return indirizzi[0].get_indirizzo_su_due_righe_con_cap()
            else:
                return indirizzi[0].get_indirizzo_corto()

        return ""

    def get_indirizzo_in_due_campi(self, tipo):
        """
        Recupera un indirizzo non cancellato, del tipo passato come parametro e 
        associato all'entità. Poi restituisce due stringhe: la prima è la via
        dell'indirizzo e la seconda è la concatenazione di città e provincia.
        """
        via = ''
        citta_e_pr = ''
        indirizzi = self.indirizzi.filter(tipo=tipo, cancellato=False)
        if indirizzi.count() > 0:
            if indirizzi[0].via2:
                via = "{} {}".format(indirizzi[0].via1, indirizzi[0].via2)
            else:
                via = indirizzi[0].via1
            citta_e_pr = '{} ({})'.format(indirizzi[0].citta, indirizzi[0].provincia)
        return via, citta_e_pr

    def __str__(self):
        result = ""
        if self.tipo == PERSONA_FISICA:
            result = "{} - {} {}".format(self.codice, self.nome, self.cognome)
        else:
            result = "{} - {}".format (self.codice, self.ragione_sociale)
        return result

    class Meta:
        verbose_name_plural = "entità"


class ContoCorrenteManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)

    def get_cc_proprietario_gestionale(self):
        """
        Restituisce i conti correnti del proprietario del gestionale
        (Mr Ferro per esempio).
        """
        return self.filter(cancellato=False, entita=Entita.objects.proprietario())

    # DA CANCELLARE
    def get_cc_clienti(self):
        """
        Restituisce i conti correnti dei clienti di Mr Ferro
        """
        return self.filter(cancellato=False).exclude(entita=None)

    # def resetPredefinito(self, cliente, predefinito):
    def resetPredefinito(self, entita, predefinito):
        if predefinito:
            # tolgo il flag 'predefinito' da tutti i conti della
            # stessa entita
            # aa = self.filter(cliente=cliente, cancellato=False)
            conti_stessa_entita = self.filter(entita=entita, cancellato=False)
            conti_stessa_entita.update(predefinito=False)


class ContoCorrente(models.Model):
    # cliente = None indica che il cc è di Mr Ferro. Altrimenti, il cc
    # è di un cliente
    entita = models.ForeignKey(Entita, related_name="conti_correnti")
    # il cc predefinito è quello da usare come default quando si deve
    # scegliere un cc
    predefinito = models.BooleanField(default=False)
    iban = models.CharField(max_length=32)
    swift = models.CharField(max_length=11, null=True, blank=True, help_text="Chiamato anche codice BIC")
    # straniero=True se il conto corrente è di una banca straniera. Serve
    # a determinare come validare il campo
    straniero = models.BooleanField(default=False)
    intestatario = models.CharField(max_length=80)
    nome_banca = models.CharField(max_length=80)
    filiale = models.CharField(max_length=80, null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    attivo = models.BooleanField(default=True)
    objects = ContoCorrenteManager()

    def __str__(self):
        return "%s - %s" % (self.nome_banca, self.iban)

    class Meta:
        verbose_name_plural = "conti correnti"


class IndirizzoManager(models.Manager):
    def non_cancellati (self):
        return self.filter(cancellato=False)


class Indirizzo(models.Model):
    entita = models.ForeignKey(Entita, related_name="indirizzi")
    tipo = models.CharField(max_length=1, choices=TIPO_SEDE_CHOICES, default=SEDE_LEGALE)
    via1 = models.CharField(max_length=80)
    via2 = models.CharField(max_length=80, null=True, blank=True)
    citta = models.CharField(max_length=60)
    provincia = models.CharField(max_length=2)
    cap = models.CharField(max_length=5)
    nazione = models.CharField(max_length=30)
    cancellato = models.BooleanField(default=False)
    objects = IndirizzoManager()

    def get_indirizzo_corto(self):
        return "{} {} {} ({})".format(self.via1, self.via2, self.citta, self.provincia)

    def get_indirizzo_medio(self):
        return "{} {} - {} {} ({})".format(self.via1, self.via2, self.cap, self.citta, self.provincia)

    def get_indirizzo_su_due_righe_con_cap(self):
        prima_riga = "{} {}".format(self.via1, self.via2).strip()
        seconda_riga = "{} {} ({})".format(self.cap, self.citta.upper(), self.provincia)
        return (prima_riga, seconda_riga)

    def __str__(self):
        return "{} - {}".format(self.entita.get_nome_completo(),
            self.get_tipo_display())

    class Meta:
        verbose_name_plural = "indirizzi"


class ContattoManager(models.Manager):
    def non_cancellati (self):
        return self.filter(cancellato=False)


class Contatto(models.Model):
    entita = models.ForeignKey(Entita, related_name="contatti")
    tipo = models.CharField(max_length=1, choices=TIPO_CONTATTO_CHOICES, default=CONTATTO_TEL_UFFICIO)
    valore = models.CharField(max_length=80)
    custom_label = models.CharField(max_length=40, help_text="Etichetta da usare se tipo contatto = personalizzato",
                                    null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = IndirizzoManager()

    def __str__(self):
        return "{} - {}".format(self.entita.get_nome_completo(), self.get_tipo_display())

    class Meta:
        verbose_name_plural = "contatti"


class CommessaManager(models.Manager):
    
    def non_cancellati(self):
        result = self.filter(cancellato=False)
        return result

    # DA CANCELLARE
    def tutti(self, as_list=False):
        result = self.filter(cancellato=False)
        if as_list:
            # per rendere il risultato serializzabile devo fare così:
            result = list(result.values_list('id', 'codice', 'cliente', 'data_apertura'))
        return result

    def next_codice(self):
        # restituisce il codice più grande già esistente nel db, aumentato di 1
        year = datetime.now().year % 1000
        sigla = "{}/".format(year)
        aggr_max = self.filter(codice__startswith=sigla).aggregate(Max('codice'))
        max_str = aggr_max['codice__max']
        if max_str:
            max_int = int(max_str[len(sigla):])
        else:
            max_int = 0
        next_codice = "{0}{1:04d}".format(sigla, max_int+1)
        return next_codice

    def filtraCommesse(self, **mydict):
        result = self.tutti()
        codice = mydict.get('codice', None)
        cliente = mydict.get('cliente', None)
        if codice:
            result = result.filter(codice=codice)
        if cliente:
            result = result.filter(cliente=cliente)
        return result

    def get_magazzino(self):
        return self.get(codice='MAGAZZINO')


def crea_directory_commessa(sender, instance, created, **kwargs):
    """
    Crea una directory dove memorizzare i file relativi alla commessa
    """
    if created:
        nome_directory = instance.get_nome_directory()
        os.mkdir(os.path.join(settings.DIRECTORY_COMMESSE, nome_directory))


class Commessa(models.Model):
    codice = models.CharField(max_length=20)
    # limit_choices_to funziona solo nell'admin
    cliente = models.ForeignKey(Entita, limit_choices_to={'is_client': True})
    data_apertura = models.DateField(default='2015-01-01')
    data_consegna = models.DateField(null=True, blank=True)
    prodotto = models.TextField(null=True, blank=True)
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = CommessaManager()

    def __str__(self):
        return "%s - %s" % (self.codice, self.cliente)

    def get_nome_directory(self):
        return self.codice.replace('/', '-')

    def get_path_public_directory(self):
        nome_directory = self.get_nome_directory()
        root_commessa = os.path.join(settings.DIRECTORY_COMMESSE, nome_directory)
        return os.path.join(root_commessa, DIRECTORY_PUBBLICA)
    
    def get_path_private_directory(self):
        nome_directory = self.get_nome_directory()
        root_commessa = os.path.join(settings.DIRECTORY_COMMESSE, nome_directory)
        return os.path.join(root_commessa, DIRECTORY_PRIVATA)

    def get_percorso_file_pubblico(self, nome_file):
        """
        Restituisce il percorso completo del file pubblico passato come parametro
        """
        path_dir = self.get_path_public_directory()
        return os.path.join(path_dir, nome_file)

    def get_percorso_file_privato(self, nome_file):
        """
        Restituisce il percorso completo del file privato passato come parametro
        """
        path_dir = self.get_path_private_directory()
        return os.path.join(path_dir, nome_file)

    def get_file_pubblici(self):
        """
        Restituisce l'elenco dei file pubblici di questa commessa
        """
        mypath = self.get_path_public_directory()
        try: 
            onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
        except FileNotFoundError:
            onlyfiles = []
        return onlyfiles

    def get_file_privati(self):
        """
        Restituisce l'elenco dei file privati di questa commessa
        """
        mypath = self.get_path_private_directory()
        try: 
            onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
        except FileNotFoundError:
            onlyfiles = []
        return onlyfiles

    def scrivi_file(self, nome_file, privato, file_content):
        nome_directory = self.get_nome_directory()
        sottodirectory = DIRECTORY_PRIVATA if privato=="true" else DIRECTORY_PUBBLICA

        # creazione cartella commessa
        try:
            os.makedirs(os.path.join(settings.DIRECTORY_COMMESSE, nome_directory))
        except OSError as err:
            if err.errno!=17:
                raise

        # creazione cartella commessa / [pubblica | privata]
        try:
            os.makedirs(os.path.join(settings.DIRECTORY_COMMESSE, nome_directory, sottodirectory))
        except OSError as err:
            if err.errno!=17:
                raise

        if privato == "true":
            path_file = self.get_percorso_file_privato(nome_file)
        else:
            path_file = self.get_percorso_file_pubblico(nome_file)

        fout = open(path_file, 'wb+')
        try:
            # Iterate through the chunks.
            for chunk in file_content.chunks():
                fout.write(chunk)
            fout.close()
            return True
        except:
            return False


    def cancella_file(self, nome_file, privato):       
        if privato == "true":
            path_file = self.get_percorso_file_privato(nome_file)
        else:
            path_file = self.get_percorso_file_pubblico(nome_file)

        try:
            os.remove(path_file)
            return True
        except:
            return False            

    class Meta:
        verbose_name_plural = "commesse"

# signals.post_save.connect(create_cartelle_commessa, sender=Commessa)

"""
class DocumentoManger(models.Manager):
    pass
    #http://stackoverflow.com/questions/2277281/django-upload-file-into-specific-directory-that-depends-on-the-post-uri


class Documento(models.Model):
    nome = models.CharField(max_length=200)
    commessa = models.ForeignKey(Commessa)
    objects = DocumentoManger()

    def __str__(self):
        return "{} - {}".format(self.commessa.codice, self.nome)

    class Meta:
        verbose_name_plural = "Documenti"
"""

class DipendenteManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)

    def tutti(self):
        return self.filter(cancellato=False)

    def attivi(self):
        return self.filter(cancellato=False, attivo=True)

    def get_dipendenti_e_ore(self, as_list=False, da=None, a=None):
        """
        Restituisce tutti i dipendenti non cancellati e con il totale di ore lavorate
        nel periodo specificato
        """
        # TODO: sql injection possibile!
        query = 'select sum(ore) from anagrafiche_consuntivo where anagrafiche_consuntivo' \
            + '.dipendente_id = anagrafiche_dipendente.id ' \
            + ' AND not anagrafiche_consuntivo.cancellato'
        if da:
            query += ' AND anagrafiche_consuntivo.data >= DATE(\'%s\')' % da
        if a:
            query += ' AND anagrafiche_consuntivo.data <= DATE(\'%s\')' % a

        # ad ogni record restituito da self.tutti() aggiungi un campo chiamato 'ore_totali'
        # valorizzato con il risultato della query
        result = self.attivi().extra(select = {'ore_totali': query})
        if as_list:
            # per rendere il risultato serializzabile devo fare così:
            result = list(result.values_list('id', 'nome', 'cognome', 'ore_totali'))
        return result


class Dipendente(models.Model):
    nome = models.CharField(max_length=30)
    cognome = models.CharField(max_length=30)
    costo_orario = models.DecimalField(max_digits=6, decimal_places=2)
    matricola = models.IntegerField()
    data_assunzione = models.DateField(null=True, blank=True)
    data_cessazione = models.DateField(null=True, blank=True)
    scadenza_visita_medica = models.DateField(null=True, blank=True)
    codice_fiscale = models.CharField(max_length=16, null=True, blank=True)
    cellulare = models.CharField(max_length=20, null=True, blank=True)
    salta_validazione_cf = models.BooleanField(default=False)
    attivo = models.BooleanField(default=True)
    # esterno = i dipendenti arrivati tramite le agenzie tipo adecco
    interno = models.BooleanField(default=True)
    # i dipendenti diretti sono quelli i cui costi si imputano ad una commessa
    diretto = models.BooleanField(default=True)
    cancellato = models.BooleanField(default=False)
    objects = DipendenteManager()

    def getNomeCompleto(self):
        return "%s %s" % (self.nome, self.cognome)
        
    def __str__(self):
        return "%s %s (%s €/ora)" % (self.nome, self.cognome, self.costo_orario)

    class Meta:
        verbose_name_plural = "dipendenti"


class TipoLavoroManager(models.Manager):

    def tutti(self, as_list=False):
        #result = self.filter(cancellato=False)
        result = self.all()
        if as_list:
            # per rendere il risultato serializzabile devo fare così:
            result = list(result.values_list('id', 'descrizione'))
        return result


class TipoLavoro(models.Model):
    descrizione = models.CharField(max_length=50, unique=True)
    objects = TipoLavoroManager()

    def __str__(self):
        return self.descrizione

    class Meta:
        verbose_name_plural = "Tipi lavoro"


class ConsuntivoManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)
        
    def tutti(self):
        return self.filter(cancellato=False)

    def getByCommessa(self, idCommessa):
        result = self.tutti().filter(commessa=idCommessa)
        result = result.order_by('data', 'dipendente__nome', 'dipendente__cognome')
        return result

    def filtraConsuntivi(self, **mydict):
        result = self.tutti()
        data_da = mydict.get('da', None)
        data_a = mydict.get('a', None)
        commessa = mydict.get('commessa', None)
        dipendente = mydict.get('dipendente', None)
        tipo_lavoro = mydict.get('tipo_lavoro', None)
        if data_da:
            data_da = datetime.strptime(data_da, '%Y-%m-%d').date()
            result = result.filter(data__gte=data_da)
        if data_a:
            data_a = datetime.strptime(data_a, '%Y-%m-%d').date()
            result = result.filter(data__lte=data_a)
        if commessa:
            result = result.filter(commessa=commessa)
        if dipendente:
            result = result.filter(dipendente=dipendente)
        if tipo_lavoro:
            result = result.filter(tipo_lavoro=tipo_lavoro)
        return result

    def getTotaliDipendente(self, **my_dict):
        """
        Restituisce un oggetto con il totale delle ore fatte da un 
        dipendente in un periodo, moltiplicato per il suo costo orario.
        """
        data_da = my_dict.get('da', None)
        data_a = my_dict.get('a', None)
        dipendente = my_dict.get('dipendente', None)
        sommatoria = self.tutti().filter(dipendente=dipendente)
        if data_da:
            data_da = datetime.strptime(data_da, '%Y-%m-%d').date()
            sommatoria = sommatoria.filter(data__gte=data_da)
        if data_a:
            data_a = datetime.strptime(data_a, '%Y-%m-%d').date()
            sommatoria = sommatoria.filter(data__lte=data_a)
        totale = sommatoria.aggregate(totale_ore=Sum('ore'))
        costo_orario = Dipendente.objects.get(id=dipendente).costo_orario
        if totale['totale_ore']:
            risultato = {
                'totale_ore': totale['totale_ore'],
                'totale_importi': round(totale['totale_ore']*costo_orario, 2)
            }
        else:
            risultato = {
                'totale_ore': 0,
                'totale_importi': 0
            }
        return risultato


class Consuntivo(models.Model):
    data = models.DateField()
    ore = models.DecimalField(max_digits=7, decimal_places=2,
        validators=[MaxValueValidator(12), MinValueValidator(0.5)])
    tipo_lavoro = models.ForeignKey(TipoLavoro)
    dipendente = models.ForeignKey(Dipendente)
    commessa = models.ForeignKey(Commessa)
    note = models.TextField(null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = ConsuntivoManager()

    def __str__(self):
        return "Consuntivo per %s - dipendente %s - %s - %s ore di %s" \
            % (self.commessa.codice, self.dipendente, self.data, self.ore, self.tipo_lavoro)

    class Meta:
        verbose_name_plural = "Consuntivi"


class ClasseArticolo(models.Model):
    sigla = models.CharField(max_length=2)
    descrizione = models.CharField(max_length=40)

    def __str__(self):
        return self.descrizione

    class Meta:
        verbose_name_plural = "classi articoli"


class TipoMovimentoManager(models.Manager):
    
    def get_carico(self):
        return self.get(descrizione="Carico")
    
    def get_scarico(self):
        return self.get(descrizione="Scarico")
        

class TipoMovimento(models.Model):
    descrizione = models.CharField(max_length=100)
    segno = models.IntegerField(default=+1)
    objects = TipoMovimentoManager()

    def __str__(self):
        return self.descrizione

    class Meta:
        verbose_name_plural = "Tipi movimenti"


class ArticoloManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)

    def next_codice(self, sigla):
        # restituisce il codice più grande corrispondente alla sigla passata
        # in input, aumentato di 1
        aggr_max = self.filter(codice__startswith=sigla).aggregate(Max('codice'))
        max_str = aggr_max['codice__max']
        if max_str:
            max_int = int(max_str[len(sigla):])
        else:
            max_int = 0
        next_codice = "{0}{1:04d}".format(sigla, max_int+1)
        return next_codice


class Articolo(models.Model):
    codice = models.CharField(max_length=6)
    classe = models.ForeignKey(ClasseArticolo)
    descrizione = models.CharField(max_length=70)
    codice_fornitore = models.CharField(max_length=50, null=True, blank=True, \
        help_text="Codice usato dal fornitore per identificare questo articolo")
    note = models.TextField(null=True, blank=True)
    unita_di_misura = models.CharField(max_length=2, choices=UNITA_MISURA_CHOICES)
    prezzo_di_listino = models.DecimalField(max_digits=13, decimal_places=2)
    lt = models.PositiveIntegerField(null=True, blank=True, help_text="Lead time")
    ss = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, 
        help_text="scorta di sicurezza")
    cancellato = models.BooleanField(default=False)
    scorta = models.IntegerField(default=0)
    objects = ArticoloManager()

    def __str__(self):
        return "{} - {}".format(self.codice, self.descrizione)

    class Meta:
        verbose_name_plural = "articoli"


class GiacenzaManager(models.Manager):
    pass


class Giacenza(models.Model):
    lotto = models.ForeignKey('BollaFornitore', related_name="giacenze")
    articolo = models.ForeignKey(Articolo)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))])
    note = models.CharField(max_length=500, blank=True, default="")
    objects = GiacenzaManager()
        
    def __str__(self):
        return "{} - {} di {}".format(self.lotto.codice, self.quantita, self.articolo.descrizione)

    class Meta:
        verbose_name_plural = "giacenze"



def verifica_giacenza_pre_save(sender, **kwargs):
    """
    Verifica che la giacenza di un lotto abbia la quantità non negativa.
    """
    giacenza = kwargs['instance']
    
    if giacenza.quantita < 0:
        raise WmsValidationError({"non_field_errors": "La giacenza dell'articolo \"{}\" non può avere una quantità negativa." \
            .format(giacenza.articolo.descrizione)})
signals.pre_save.connect(verifica_giacenza_pre_save, sender=Giacenza)


def aggiorna_giacenza_e_scorta_post_save(sender, **kwargs):
    """
    Se la giacenza di un lotto ha quantità uguale a 0, allora cancella la giacenza.
    Dopo aver aggiornato la giacenza (sia in caso di carico o scarico) bisogna aggiornare
    la scorta dell'articolo.
    """
    giacenza = kwargs['instance']
    
    if giacenza.quantita == 0:
        giacenza.delete()
 
    articolo = giacenza.articolo
    scorta = Giacenza.objects.filter(articolo=articolo).aggregate(Sum('quantita'))
    articolo.scorta = scorta['quantita__sum'] or 0
    articolo.save()

signals.post_save.connect(aggiorna_giacenza_e_scorta_post_save, sender=Giacenza)

class MovimentoManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)


class Movimento(models.Model):
    articolo = models.ForeignKey(Articolo, related_name='movimenti')
    lotto = models.ForeignKey('BollaFornitore', related_name='movimenti')
    data = models.DateTimeField(auto_now_add=True)
    tipo_movimento = models.ForeignKey(TipoMovimento)
    autore = models.ForeignKey(User, related_name='movimenti')
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    # le unità di misura di un articolo possono cambiare nel tempo, mentre nei movimenti
    # devono rimanere storicizzati. Quindi non uso una foreign key ma memorizzo la descrizione 
    # dell'u.m. usata al momento del movimento:
    unita_di_misura = models.CharField(max_length=20)
    # la destinazione è la commessa che giustifica il movimento. Quando si carica un articolo 
    # a seguito di una bolla fornitore la destinazione è sempre la commessa MAGAZZINO. Quando 
    # si trasferisce il materiale dal magazzino si usa la commessa su cui si lavora
    destinazione = models.ForeignKey(Commessa, related_name='movimenti')
    cancellato = models.BooleanField(default=False)
    objects = MovimentoManager()

    @classmethod
    def get_quantita_reale(cls, quantita, tipo_movimento):
        """
        Nelle api bisogna sempre passare quantità positive, però nel db memorizzo quantità
        negative se l'operazione è di tipo scarico, reso o correzione negativa.
        """
        quantita_reale = quantita*tipo_movimento.segno
        return quantita_reale

    def __str__(self):
        return "{} verso {}: {} (qty: {})".format(self.tipo_movimento.descrizione, self.destinazione.codice, self.articolo.codice, self.quantita)

    class Meta:
        verbose_name_plural = "movimenti magazzino"


def aggiorna_giacenza_dopo_mod_movimento(sender, **kwargs):
    """
    Aggiorna la giacenza di un lotto prima della save di un movimento.
    """
    nuovo_movimento = kwargs['instance']
    
    vecchio_record = None

    # devo usare le transazioni qui o la prima modifica dello scarico del test test_movimenti_e_giacenze_10
    # fallisce perché la giacenza del movimento originale è salvata prima che l'aggiornamento della seconda giacenza
    # sollevi un'eccezione.

    with transaction.atomic():
        if nuovo_movimento.id:
            # Non mi basta controllare solo se nuovo_movimento ha un id settato o no perché quando eseguo i 
            # test automatici e carico le fixtures, nuovo_movimento ha l'id settato anche se il 
            # record non è ancora stato inserito nel db:
            if Movimento.objects.filter(pk=nuovo_movimento.id).exists():
                # l'id è settato e il record esiste effettivamente nel db. In questo caso quindi il movimento
                # non corrisponde ad una fixture.
                #import pdb; pdb.set_trace()
                pass
            else:
                # Si tratta di una fixture caricata durante i test automatici e quindi termina questo metodo 
                # senza fare niente.
                return

            # Modifica di un movimento già inserito nel db. 
            # La giacenza dell'articolo potrebbe esistere o no. Per esempio ci sono prima un carico di 300
            # pezzi di un articolo e poi uno scarico di 300. Se a quel punto modifico un movimento, la 
            # giacenza non esiste e va ricreata.
            vecchio_record = Movimento.objects.get(id=nuovo_movimento.id)

            #### inizio blocco che gestisce la cancellazione logica
            if nuovo_movimento.cancellato and not vecchio_record.cancellato:
                # import pdb; pdb.set_trace()
                # si sta cancellando logicamente un movimento. Se la giacenza dell'articolo va in negativo allora blocca la
                # cancellazione. Il controllo ha senso solo quando si cancellano i carichi. Se si cancella uno scarico la
                # giacenza aumenta sempre.
                giacenza = None
                giacenza_list = Giacenza.objects.filter(lotto=nuovo_movimento.lotto, articolo=nuovo_movimento.articolo)
                if nuovo_movimento.quantita > 0:
                    if not giacenza_list or nuovo_movimento.quantita > giacenza_list[0].quantita:
                        raise WmsValidationError({"non_field_errors": ("Cancellando questo movimento si avrebbe una giacenza negativa " \
                            + "dell'articolo \"{}\". Se devi proprio cancellare questo carico prima cancella i movimenti di " \
                            + "scarico.").format(nuovo_movimento.articolo.descrizione)})

                if giacenza_list:
                    giacenza = giacenza_list[0]
                        
                    # procedi con l'aggiornamento della giacenza e poi esci
                    giacenza.quantita -= nuovo_movimento.quantita
                    giacenza.save()
                else: 
                    # non esiste più la giacenza relativa al movimento cancellato. Capita se si fa un caricamento di un articolo e poi si scarica la
                    # stessa quantità dello stesso articolo e lotto. In questo caso se si cancella lo scarico va creata una nuova giacenza con quantità pari allo scarico cancellato.
                    giacenza = Giacenza()
                    giacenza.articolo = vecchio_record.articolo
                    giacenza.quantita = abs(vecchio_record.quantita)   # la quantità negli scarichi è negativa
                    giacenza.lotto = vecchio_record.lotto
                    giacenza.save()
                return
            #### fine blocco che gestisce la cancellazione logica

            modificato_articolo = False
            if nuovo_movimento.articolo != vecchio_record.articolo:
                modificato_articolo = True
            
            modificato_lotto = False
            if nuovo_movimento.lotto != vecchio_record.lotto:
                # import pdb; pdb.set_trace()
                modificato_lotto = True

            if modificato_articolo or modificato_lotto:
                giacenza_vecchia = Giacenza.objects.get(lotto=vecchio_record.lotto, articolo=vecchio_record.articolo)
                giacenza_vecchia.quantita -= vecchio_record.quantita
                giacenza_vecchia.save() 

            modifica_quantita = nuovo_movimento.quantita - vecchio_record.quantita
            giacenza, giacenza_creata = Giacenza.objects.get_or_create(lotto=nuovo_movimento.lotto, lotto__cancellato=False, \
                articolo = nuovo_movimento.articolo, defaults={'quantita': modifica_quantita})
            if giacenza_creata:
                if modificato_articolo or modificato_lotto:
                    # aggiorno la giacenza dopo la modifica dell'articolo del movimento
                    giacenza.quantita = nuovo_movimento.quantita
                else:
                    # aggiorno la giacenza dopo la modifica della quantità del movimento
                    giacenza.quantita = modifica_quantita
                giacenza.save()
            else:
                if modificato_articolo or modificato_lotto:
                    # aggiorno la giacenza dopo la modifica dell'articolo del movimento
                    giacenza.quantita += nuovo_movimento.quantita
                else: 
                    # aggiorno la giacenza dopo la modifica della quantità del movimento
                    giacenza.quantita += modifica_quantita
                giacenza.save()


        else:
            # creazione di un movimento. La giacenza del relativo articolo potrebbe già esistere nel database
            # oppure no.
            giacenza, giacenza_creata = Giacenza.objects.get_or_create(lotto=nuovo_movimento.lotto, lotto__cancellato=False, \
                articolo = nuovo_movimento.articolo, defaults={'quantita': nuovo_movimento.quantita})

            ##### la giacenza a questo punto è già creata, anche se la quantità è negativa...
            ##### Invece di mettere degli if in questo punto conviene mettere un giacenza.pre_save per bloccare la 
            ##### creazione di giacenze con quantita negative ed un giacenza.post_save per cancellare le giacenze
            ##### con quantita = 0.

            # La creazione o la modifica di una giacenza può sollevare una APIException e quindi bloccare il salvataggio del 
            # movimento.
            
            # se la giacenza c'era già, aggiorna la quantità
            if not giacenza_creata:
                # visto che abbiamo già passato le API, nuovo_movimento.quantità ha già il segno giusto (anche in caso di scarico)
                giacenza.quantita = giacenza.quantita + nuovo_movimento.quantita
                giacenza.save()

signals.pre_save.connect(aggiorna_giacenza_dopo_mod_movimento, sender=Movimento)

"""
def aggiorna_giacenza_dopo_cancellazione_movimento(sender, **kwargs):
    #### Attivato quando si cancella FISICAMENTE un movimento, per esempio dall'admin di django.
    raise APIException("Stai cancellando un movimento, mentre invece dovresti passare dalle API!")
    
signals.pre_delete.connect(aggiorna_giacenza_dopo_cancellazione_movimento, sender=Movimento)
"""




def aggiorna_movimento_dopo_mod_riga_bolla(sender, **kwargs):
    """
    Aggiorna il movimento di carico relativo ad una riga di una bolla fornitore.
    Come conseguenza, si aggiorneranno anche la giacenza e la scorta di un articolo.
    """
    nuova_riga_bolla = kwargs['instance']
    vecchio_record = None

    with transaction.atomic():
        if nuova_riga_bolla.id:
            # Non mi basta controllare solo se nuova_riga_bolla ha un id settato o no perché quando eseguo i 
            # test automatici e carico le fixtures, nuova_riga_bolla ha l'id settato anche se il 
            # record non è ancora stato inserito nel db:
            if RigaBollaFornitore.objects.filter(pk=nuova_riga_bolla.id).exists():
                # l'id è settato e il record esiste effettivamente nel db. In questo caso quindi la riga bolla
                # non corrisponde ad una fixture.
                #import pdb; pdb.set_trace()
                pass
            else:
                # Si tratta di una fixture caricata durante i test automatici e quindi termina questo metodo 
                # senza fare niente.
                return

            # Modifica di un movimento già inserito nel db. 
            # La giacenza dell'articolo potrebbe esistere o no. Per esempio ci sono prima un carico di 300
            # pezzi di un articolo e poi uno scarico di 300. Se a quel punto modifico un movimento, la 
            # giacenza non esiste e va ricreata.

            ### Quando si crea una riga bolla, poi si genera in automatico il relativo movimento e si aggiorna la 
            ### riga bolla. Quindi l'oggetto nuova_riga_bolla può avere un id anche se è un record quasi nuovo e non 
            ### un aggiornamento di una riga fatto dall'utente. Per questo motivo si è messo il controllo if per vedere
            ### se tra record vecchio e nuovo è cambiato qualcosa tra articolo, quantita e unità_di_misura (cioè i
            ### campi che andrebbero aggiornati anche nel relativo movimento).

            
            vecchio_record = RigaBollaFornitore.objects.get(pk=nuova_riga_bolla.id)

            #### inizio blocco che gestisce la cancellazione logica della riga bolla
            if nuova_riga_bolla.cancellato and not vecchio_record.cancellato:
                nuova_riga_bolla.carico.cancellato = True
                nuova_riga_bolla.carico.save()
                return
            #### fine blocco che gestisce la cancellazione logica

            """
            modificato_articolo = False
            if nuova_riga_bolla.articolo != vecchio_record.articolo:
                modificato_articolo = True
            

            modificato_lotto = False   # ha senso per le righe bolle?
            #if nuova_riga_bolla.lotto != vecchio_record.lotto:
            #    1/0 # TODO
            #    # import pdb; pdb.set_trace()
            #    modificato_lotto = True

            if modificato_articolo or modificato_lotto:
                1/0 # TODO
                giacenza_vecchia = Giacenza.objects.get(lotto=vecchio_record.lotto, articolo=vecchio_record.articolo)
                giacenza_vecchia.quantita -= vecchio_record.quantita
                giacenza_vecchia.save() 
            """


            """
            modifica_quantita = nuova_riga_bolla.quantita - vecchio_record.quantita
            giacenza, giacenza_creata = Giacenza.objects.get_or_create(lotto=nuova_riga_bolla.bolla, lotto__cancellato=False, \
                articolo = nuova_riga_bolla.articolo, defaults={'quantita': modifica_quantita})
            if giacenza_creata:
                1/0 # TODO
                if modificato_articolo or modificato_lotto:
                    # aggiorno la giacenza dopo la modifica dell'articolo del movimento
                    giacenza.quantita = nuova_riga_bolla.quantita
                else:
                    # aggiorno la giacenza dopo la modifica della quantità del movimento
                    giacenza.quantita = modifica_quantita
                giacenza.save()
            else:
                if modificato_articolo or modificato_lotto:
                    1/0 # TODO
                    # aggiorno la giacenza dopo la modifica dell'articolo del movimento
                    giacenza.quantita += nuova_riga_bolla.quantita
                else: 
                    # aggiorno la giacenza dopo la modifica della quantità della riga bolla
                    print("aggiungo " + str(modifica_quantita) + " alla giacenza1.")
                    giacenza.quantita += modifica_quantita
                giacenza.save()
            """
            if nuova_riga_bolla.articolo != vecchio_record.articolo or \
                    nuova_riga_bolla.quantita != vecchio_record.quantita or \
                    nuova_riga_bolla.articolo_unita_di_misura != vecchio_record.articolo_unita_di_misura:
                # print ("Aggiorno movimento relativo alla riga bolla fornitori.")
                # Aggiornando il movimento, l'aggiornamento della giacenza è automatico per via del 
                # pre_save sui movimenti.
                nuova_riga_bolla.carico.articolo = nuova_riga_bolla.articolo
                nuova_riga_bolla.carico.quantita = nuova_riga_bolla.quantita
                nuova_riga_bolla.carico.unita_di_misura = nuova_riga_bolla.articolo_unita_di_misura
                nuova_riga_bolla.carico.save()            

        else:
            # creazione di una riga bolla
            pass

signals.pre_save.connect(aggiorna_movimento_dopo_mod_riga_bolla, sender='anagrafiche.RigaBollaFornitore')



def aggiorna_movimenti_dopo_mod_bolla(sender, **kwargs):
    """
    Aggiorna i movimenti di carico/scarico relativi alle righe di una bolla fornitore cancellata.
    """
    nuova_bolla = kwargs['instance']
    vecchio_record = None

    with transaction.atomic():
        if nuova_bolla.id:
            # Non mi basta controllare solo se nuova_bolla ha un id settato o no perché quando eseguo i 
            # test automatici e carico le fixtures, nuova_bolla ha l'id settato anche se il 
            # record non è ancora stato inserito nel db:
            if BollaFornitore.objects.filter(pk=nuova_bolla.id).exists():
                # l'id è settato e il record esiste effettivamente nel db. In questo caso quindi la bolla
                # non corrisponde ad una fixture.
                #import pdb; pdb.set_trace()
                pass
            else:
                # Si tratta di una fixture caricata durante i test automatici e quindi termina questo metodo 
                # senza fare niente.
                return
            
            vecchio_record = BollaFornitore.objects.get(pk=nuova_bolla.id)
            #### inizio blocco che gestisce la cancellazione logica della bolla
            if nuova_bolla.cancellato and not vecchio_record.cancellato:
                scarichi = nuova_bolla.get_scarichi()
                if scarichi:
                    raise WmsValidationError({"non_field_errors": "La bolla {} non può essere cancellata perché sono stati effettuati scarichi." \
                        .format(vecchio_record.codice)})
                else:
                    # import pdb; pdb.set_trace()
                    righe_bolla = nuova_bolla.righe.non_cancellati()
                    for riga_bolla in righe_bolla:
                        riga_bolla.cancellato = True
                        riga_bolla.save()
                return
            #### fine blocco che gestisce la cancellazione logica della bolla

            """
            ### Quando si crea una riga bolla, poi si genera in automatico il relativo movimento e si aggiorna la 
            ### riga bolla. Quindi l'oggetto nuova_riga_bolla può avere un id anche se è un record quasi nuovo e non 
            ### un aggiornamento di una riga fatto dall'utente. Per questo motivo si è messo il controllo if per vedere
            ### se tra record vecchio e nuovo è cambiato qualcosa tra articolo, quantita e unità_di_misura (cioè i
            ### campi che andrebbero aggiornati anche nel relativovo movimento).

            if nuova_riga_bolla.articolo != vecchio_record.articolo or \
                    nuova_riga_bolla.quantita != vecchio_record.quantita or \
                    nuova_riga_bolla.articolo_unita_di_misura != vecchio_record.articolo_unita_di_misura:
                # print ("Aggiorno movimento relativo alla riga bolla fornitori.")
                # Aggiornando il movimento, l'aggiornamento della giacenza è automatico per via del 
                # pre_save sui movimenti.
                nuova_riga_bolla.carico.articolo = nuova_riga_bolla.articolo
                nuova_riga_bolla.carico.quantita = nuova_riga_bolla.quantita
                nuova_riga_bolla.carico.unita_di_misura = nuova_riga_bolla.articolo_unita_di_misura
                nuova_riga_bolla.carico.save()            
            """

        else:
            # creazione di una nuova bolla, non devo controllare niente.
            pass

signals.pre_save.connect(aggiorna_movimenti_dopo_mod_bolla, sender='anagrafiche.BollaFornitore')


# ----------------------------------------------------------------------------------------------------------------------

class AliquotaIVAManager(models.Manager):
    
    def get_aliquota_default(self):
        return self.get(percentuale=22)


class AliquotaIVA(models.Model):
    codice = models.CharField(max_length=6, null=True, blank=True)
    descrizione = models.CharField(max_length=150)
    percentuale = models.DecimalField(max_digits=5, decimal_places=2, unique=False)
    objects = AliquotaIVAManager()

    def __str__(self):
        return self.descrizione

    class Meta:
        verbose_name_plural = "aliquote IVA"


class PreventivoClienteManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)

    def next_codice(self):
        # restituisce il codice più grande già presente nel db, aumentato di 1
        year = datetime.now().year % 1000
        radice = "{}{}".format(PREVENTIVO_CLIENTE_PREFIX, year)
        aggr_max = self.filter(codice__startswith=radice).aggregate(Max('codice'))
        max_str = aggr_max['codice__max']
        if max_str:
            max_int = int(max_str[len(radice):])
        else:
            max_int = 0
        next_codice = "{0}{1:04d}".format(radice, max_int+1)
        return next_codice


class PreventivoCliente(models.Model):
    codice = models.CharField(max_length=9)
    data = models.DateField()
    cliente = models.ForeignKey(Entita, limit_choices_to= \
        {'is_client':True, 'cancellato': False})
    commessa = models.ForeignKey(Commessa, null=True, blank=True, 
        related_name="preventivi")
    oggetto = models.CharField(max_length=150, null=True, blank=True)
    accettato = models.BooleanField(default=False)
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)
    persona_di_riferimento = models.CharField(max_length=PERSONA_DI_RIFERIMENTO_LENGTH,
        null=False, blank=True, default="")
    pagamento = models.ForeignKey(TipoPagamento, default=1)
    disegni_costruttivi = models.BooleanField(default=True)
    relazione_di_calcolo = models.BooleanField(default=True)
    tipo_di_acciaio = models.CharField(max_length=150, blank=True, default="")
    spessori = models.CharField(max_length=150, blank=True, default="")
    zincatura = models.CharField(max_length=150, blank=True, default="")
    classe_di_esecuzione = models.CharField(max_length=150, blank=True, default="")
    wps = models.CharField(max_length=150, blank=True, default="")
    verniciatura = models.CharField(max_length=150, blank=True, default="")
    aliquota_IVA = models.ForeignKey(AliquotaIVA, null=True, blank=True)
    totale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    totale_su_stampa = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = PreventivoClienteManager()

    def __str__(self):
        return "{} - {}".format(self.codice, self.cliente.get_nome_completo())

    def aggiorna_stato(self):
        """
        Verifica le righe di questo preventivo e se sono tutte accettate, marca
        questo preventivo come accettato
        """
        righe_non_cancellate = self.righe.filter(cancellato=False)
        if righe_non_cancellate.count() > 0:
            if not righe_non_cancellate.filter(accettata=False).exists():
                self.accettato = True
                self.save()

    def imposta_commessa(self, commessa):
        """
        Imposta la commessa in un preventivo utilizzato per un ordine
        """
        self.commessa = commessa
        self.save()

    def aggiorna_totale(self):
        totale_preventivo = self.righe.filter(cancellato=False).aggregate(Sum('totale'))
        # quando tutte le righe del preventivo sono cancellate, il totale
        # diventerebbe null. Quindi aggiungo "or 0"
        self.totale = totale_preventivo['totale__sum'] or 0
        self.save()

    class Meta:
        verbose_name_plural = "preventivi clienti"


class RigaPreventivoClienteManager(models.Manager):
    
    def non_cancellati(self):
        return self.filter(cancellato=False)


class RigaPreventivoCliente(models.Model):
    preventivo = models.ForeignKey(PreventivoCliente, related_name="righe")
    articolo = models.ForeignKey(Articolo)
    articolo_descrizione = models.CharField(max_length=1000)
    articolo_prezzo = models.DecimalField(max_digits=13, decimal_places=2)
    sconto_percentuale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    articolo_unita_di_misura = models.CharField(max_length=2, 
        choices=UNITA_MISURA_CHOICES, default=UNITA_MISURA_NUMERO)
    accettata = models.BooleanField(default=False)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    totale = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.CharField(max_length=500, blank=True, default="")
    cancellato = models.BooleanField(default=False)
    objects = RigaPreventivoClienteManager()

    def get_importo(self):
        return self.quantita * self.articolo_prezzo
        
    def __str__(self):
        return "{} - {}".format(self.preventivo.codice, self.articolo_descrizione)

    class Meta:
        verbose_name_plural = "righe preventivi clienti"


class OrdineClienteManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)

    def next_codice(self):
        # restituisce il codice più grande già presente nel db, aumentato di 1
        year = datetime.now().year % 1000
        radice = "{}{}".format(ORDINE_CLIENTE_PREFIX, year)
        aggr_max = self.filter(codice__startswith=radice).aggregate(Max('codice'))
        max_str = aggr_max['codice__max']
        if max_str:
            max_int = int(max_str[len(radice):])
        else:
            max_int = 0
        next_codice = "{0}{1:04d}".format(radice, max_int+1)
        return next_codice


class OrdineCliente(models.Model):
    codice = models.CharField(max_length=9)
    data = models.DateField()
    cliente = models.ForeignKey(Entita, limit_choices_to={'is_client': True, 'cancellato': False})
    oggetto = models.CharField(max_length=150, null=True, blank=True)
    commessa = models.ForeignKey(Commessa, related_name="ordini_clienti")
    bollettato = models.BooleanField(default=False)
    fatturato = models.BooleanField(default=False)
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)
    persona_di_riferimento = models.CharField(max_length=PERSONA_DI_RIFERIMENTO_LENGTH, null=False, blank=True,
                                              default="")
    riferimento_cliente = models.CharField(max_length=RIFERIMENTO_CLIENTE_LENGTH, null=True, blank=True, default="")
    pagamento = models.ForeignKey(TipoPagamento, default=1)
    disegni_costruttivi = models.BooleanField(default=True)
    relazione_di_calcolo = models.BooleanField(default=True)
    tipo_di_acciaio = models.CharField(max_length=150, blank=True, default="")
    spessori = models.CharField(max_length=150, blank=True, default="")
    zincatura = models.CharField(max_length=150, blank=True, default="")
    classe_di_esecuzione = models.CharField(max_length=150, blank=True, default="")
    wps = models.CharField(max_length=150, blank=True, default="")
    verniciatura = models.CharField(max_length=150, blank=True, default="")    
    sconto_euro = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sconto_percentuale = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    totale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    totale_su_stampa = models.BooleanField(default=True)
    aliquota_IVA = models.ForeignKey(AliquotaIVA, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = OrdineClienteManager()

    def __str__(self):
        return "{} (commessa: {}) - {}".format(self.codice, self.commessa.codice, self.cliente.get_nome_completo())

    def aggiorna_totale(self):
        totale_ordine = self.righe.filter(cancellato=False).aggregate(Sum('totale'))
        self.totale = totale_ordine['totale__sum'] or 0
        self.save()

    def aggiorna_stato(self):
        """
        Verifica le righe di questo ordine e se sono tutte bollettate, marca
        questo ordine come bollettato
        """
        righe_non_cancellate = self.righe.filter(cancellato=False)
        if righe_non_cancellate.count() > 0:
            if not righe_non_cancellate.filter(bollettata=False).exists():
                self.bollettato = True
                self.save()

    def aggiorna_campo_fatturato(self):
        """
        Verifica le righe di questo ordine e se sono tutte fatturate, marca
        questo ordine come fatturato.
        """
        righe_non_cancellate = self.righe.filter(cancellato=False)
        if righe_non_cancellate.count() > 0:
            if not righe_non_cancellate.filter(fatturata=False).exists():
                self.fatturato = True
                self.save()

    class Meta:
        verbose_name_plural = "ordini clienti"

"""
def aggiornaTotaleOrdineCliente(sender, instance, created, **kwargs):
    
    Aggiorna il totale dell'ordine quando si modifica un ordine esistente. Non
    ha senso quando si crea l'ordine perché non può avere righe.
    
    if not created:
        instance.aggiorna_totale()

#signals.post_save.connect(aggiornaTotaleOrdineCliente, sender=OrdineCliente)
"""

class RigaOrdineClienteManager(models.Manager):
    
    def non_cancellati(self):
        return self.filter(cancellato=False)


class RigaOrdineCliente(models.Model):
    # Il campo preventivo è ridondante perché c'è già il campo riga_preventivo. Per ora
    # comunque resta qua...
    # Per i campi 'preventivo' e 'riga_preventivo' avrei dovuto usare una relazione
    # OneToOne invece di una Foreign key. 
    ordine = models.ForeignKey(OrdineCliente, related_name="righe")
    preventivo = models.ForeignKey(PreventivoCliente, related_name="righe_ordine",
        null=True, blank=True)
    riga_preventivo = models.ForeignKey(RigaPreventivoCliente, related_name="riga_ordine",
        null=True, blank=True)
    # la commessa viene settata nel modello OrdineCliente, quindi il 
    # seguente campo vale sempre null e potrebbe essere cancellato
    commessa = models.ForeignKey(Commessa, null=True, blank=True)
    articolo = models.ForeignKey(Articolo)
    articolo_descrizione = models.CharField(max_length=1000)
    articolo_prezzo = models.DecimalField(max_digits=13, decimal_places=2)
    sconto_percentuale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    articolo_unita_di_misura = models.CharField(max_length=2, 
        choices=UNITA_MISURA_CHOICES, default=UNITA_MISURA_NUMERO)
    bollettata = models.BooleanField(default=False)
    fatturata = models.BooleanField(default=False)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    totale = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.CharField(max_length=500, blank=True, default="")
    cancellato = models.BooleanField(default=False)
    objects = RigaOrdineClienteManager()

    def __str__(self):
        return "{} - {}".format(self.ordine.codice, self.articolo)

    class Meta:
        verbose_name_plural = "righe ordini clienti"


class TipoCausaleTrasportoManager(models.Model):
    pass


class TipoCausaleTrasporto(models.Model):
    descrizione = models.CharField(max_length=150)
    objects = TipoCausaleTrasportoManager()

    def is_conto_lavorazione(self):
        return self.id == 3

    def __str__(self):
        return "{}".format(self.descrizione)

    class Meta:
        verbose_name_plural = "tipi causali trasporto"


class TipoPortoManager(models.Model):
    pass


class TipoPorto(models.Model):
    descrizione = models.CharField(max_length=150)
    objects = TipoPortoManager()

    def __str__(self):
        return "{}".format(self.descrizione)

    class Meta:
        verbose_name_plural = "tipi porto"


class TipoTrasportoACuraManager(models.Model):
    pass


class TipoTrasportoACura(models.Model):
    descrizione = models.CharField(max_length=150)
    objects = TipoTrasportoACuraManager()

    def __str__(self):
        return "{}".format(self.descrizione)

    class Meta:
        verbose_name_plural = "tipi trasporto a cura"


class TipoAspettoEsterioreManager(models.Model):
    pass


class TipoAspettoEsteriore(models.Model):
    descrizione = models.CharField(max_length=150)
    objects = TipoAspettoEsterioreManager()

    def __str__(self):
        return "{}".format(self.descrizione)

    class Meta:
        verbose_name_plural = "tipi aspetto esteriore"


class BollaClienteManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)

    def next_codice(self):
        # restituisce il codice più grande già presente nel db, aumentato di 1
        year = datetime.now().year % 1000
        radice = "{}{}".format(BOLLA_CLIENTE_PREFIX, year)
        aggr_max = self.filter(codice__startswith=radice).aggregate(Max('codice'))
        max_str = aggr_max['codice__max']
        if max_str:
            max_int = int(max_str[len(radice):])
        else:
            max_int = 0
        next_codice = "{0}{1:04d}".format(radice, max_int+1)
        return next_codice

    def get_default_causale_trasporto(self):
        return 1 # vendita

    def get_default_trasporto_a_cura_di(self):
        return 3 # mittente


class BollaCliente(models.Model):
    codice = models.CharField(max_length=9)
    data = models.DateField()
    cliente = models.ForeignKey(Entita, limit_choices_to={'is_client': True, 'cancellato': False})
    oggetto = models.CharField(max_length=150, null=True, blank=True)
    commessa = models.ForeignKey(Commessa, related_name="bolle_clienti")
    persona_di_riferimento = models.CharField(max_length=PERSONA_DI_RIFERIMENTO_LENGTH, null=False, blank=True,
                                              default="")
    riferimento_cliente = models.CharField(max_length=RIFERIMENTO_CLIENTE_LENGTH, null=True, blank=True, default="")
    fatturata = models.BooleanField(default=False)
    aspetto_esteriore = models.ForeignKey(TipoAspettoEsteriore, null=True, blank=True)
    causale_trasporto = models.ForeignKey(TipoCausaleTrasporto)
    porto = models.ForeignKey(TipoPorto, null=True, blank=True)
    trasporto_a_cura = models.ForeignKey(TipoTrasportoACura)
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)

    # peso netto, peso lordo e numero colli sono campi che solitamente rimangono
    # vuoti e sono compilati a mano dal magazziniere quando prepara la spedizione
    peso_netto = models.CharField(max_length=50, null=True, blank=True, default='0')
    peso_lordo = models.CharField(max_length=50, null=True, blank=True, default='0')
    numero_colli = models.PositiveIntegerField(null=True, blank=True)

    vettore = models.ForeignKey(Entita, null=True, blank=True, limit_choices_to= \
        {'is_supplier':True, 'vettore':True, 'cancellato': False}, related_name="bolle_trasportate")
    note = models.TextField(null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = BollaClienteManager()

    def __str__(self):
        return "{} - {}".format(self.codice, self.cliente.get_nome_completo())

    """
    def aggiorna_totale(self):
        totale_bolla = self.righe.filter(cancellato=False).aggregate(Sum('totale'))
        self.totale = totale_bolla['totale__sum'] or 0
        self.save()
    """

    def aggiorna_campo_fatturato(self):
        """
        Verifica le righe di questa bolla e se sono tutte fatturate, marca
        questa bolla come fatturato.
        """
        righe_non_cancellate = self.righe.filter(cancellato=False)
        if righe_non_cancellate.count() > 0:
            if not righe_non_cancellate.filter(fatturata=False).exists():
                self.fatturata = True
                self.save()

    class Meta:
        verbose_name_plural = "bolle clienti"


class RigaBollaClienteManager(models.Manager):
    
    def non_cancellati(self):
        return self.filter(cancellato=False)


class RigaBollaCliente(models.Model):
    bolla = models.ForeignKey(BollaCliente, related_name="righe")
    #ordine = models.ForeignKey(OrdineCliente, related_name="righe_bolle",
    #    null=True, blank=True)
    riga_ordine = models.OneToOneField(RigaOrdineCliente, 
        null=True, blank=True, related_name="riga_bolla")
    #commessa = è memorizzata sulla bolla
    fatturata = models.BooleanField(default=False)
    articolo = models.ForeignKey(Articolo)
    articolo_descrizione = models.CharField(max_length=1000)
    #articolo_prezzo = models.DecimalField(max_digits=13, decimal_places=2)
    articolo_unita_di_misura = models.CharField(max_length=2, 
        choices=UNITA_MISURA_CHOICES, default=UNITA_MISURA_NUMERO)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    #totale = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.CharField(max_length=500, blank=True, default="")
    cancellato = models.BooleanField(default=False)
    objects = RigaBollaClienteManager()

    def __str__(self):
        return "{} - {}".format(self.bolla.codice, self.articolo_descrizione)

    class Meta:
        verbose_name_plural = "righe bolle clienti"


class FatturaClienteManager(models.Manager):

    def non_cancellati(self):
        return self.filter(cancellato=False)

    def next_codice(self):
        # restituisce il codice più grande già presente nel db, aumentato di 1
        # year = datetime.now().year % 1000
        oggi = datetime.now()
        if oggi.month==1 and oggi.day<=15 and FatturaCliente.objects.filter(data__year=oggi.year -1).exists():
            year = (oggi.year -1) % 1000
        else:
            year = oggi.year % 1000

        radice = "{}{}".format(FATTURA_CLIENTE_PREFIX, year)
        aggr_max = self.filter(codice__startswith=radice).aggregate(Max('codice'))
        max_str = aggr_max['codice__max']
        if max_str:
            max_int = int(max_str[len(radice):])
        else:
            max_int = 0
        next_codice = "{0}{1:04d}".format(radice, max_int+1)
        return next_codice

    def reset(self):
        """
        Serve solo per lo sviluppo dell'applicazione
        """
        RigaOrdineCliente.objects.all().update(fatturata=False)
        OrdineCliente.objects.all().update(fatturato=False)
        RigaBollaCliente.objects.all().update(fatturata=False)
        BollaCliente.objects.all().update(fatturata=False)
        FatturaCliente.objects.all().delete()


class FatturaCliente(models.Model):
    codice = models.CharField(max_length=9)
    data = models.DateField()
    cliente = models.ForeignKey(Entita, limit_choices_to={'is_client': True, 'cancellato': False})
    oggetto = models.CharField(max_length=150, null=True, blank=True)
    commessa = models.ForeignKey(Commessa, related_name="fatture_clienti", null=True, blank=True)
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)
    persona_di_riferimento = models.CharField(max_length=PERSONA_DI_RIFERIMENTO_LENGTH, null=False, blank=True,
                                              default="")
    riferimento_cliente = models.CharField(max_length=RIFERIMENTO_CLIENTE_LENGTH, null=True, blank=True, default="")
    imponibile = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sconto_euro = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sconto_percentuale = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    imponibile_netto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    aliquota_IVA = models.ForeignKey(AliquotaIVA, null=True, blank=True)
    totale_iva = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    totale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pagamento = models.ForeignKey(TipoPagamento, default=1)
    banca_di_appoggio = models.ForeignKey(ContoCorrente, null=True, blank=True)
    # Totale su stampa?
    note = models.TextField(null=True, blank=True)
    da_confermare = models.BooleanField(default=False, help_text="campo settato "
        + "a True quando la fattura è creata con valori di default")
    cancellato = models.BooleanField(default=False)
    objects = FatturaClienteManager()

    def __str__(self):
        return "{} - {}".format(self.codice, self.cliente.get_nome_completo())

    ## https://docs.python.org/3.4/library/decimal.html
    ## The quantize() method rounds a number to a fixed exponent. This method is 
    ## useful for monetary applications that often round results to a fixed number of places.

    # Devo usare il metodo quantize() per arrotondare il valore dei decimali prodotti da 
    # moltiplicazioni e divisioni, perché hanno 4 cifre decimali. Questi valori quando vengono salvati
    # nel db sono forzati a 2 cifre decimali, ma il loro utilizzo prima della scrittura sul db può
    # provocare problemi. Per esempio il totale fattura risulta diverso da imponibile_netto più iva

    def aggiorna_totale(self):
        imponibile_obj = self.righe.filter(cancellato=False).aggregate(Sum('totale'))
        self.imponibile = imponibile_obj['totale__sum'] or Decimal(0)
        if self.sconto_euro:
            self.imponibile_netto = self.imponibile - self.sconto_euro
        elif self.sconto_percentuale:
            self.imponibile_netto = self.imponibile * (1 - self.sconto_percentuale / 100)
        else:
            self.imponibile_netto = self.imponibile
        self.imponibile_netto = self.imponibile_netto.quantize(Decimal('.01'))

        self.totale_iva = self.imponibile_netto * (self.aliquota_IVA.percentuale / 100)
        self.totale_iva = self.totale_iva.quantize(Decimal('.01'))

        self.totale = self.imponibile_netto + self.totale_iva
        self.save()

    def dissocia_bolle_e_ordini(self):
        """
        Toglie l'associazione dalle righe di questa fattura, eliminando la connessione con le righe_bolle.
        Al termine di questa funzione, la bolla usata per il drop può essere utilizzata per un'altra fattura.
        Allo stesso modo si devono cancellare le associazioni tra riga_fattura e riga_ordine.
        Le righe ordini sono dissociate sia che ordine e fattura siano collegate direttamente sia che siano collegate
        tramite la bolla.
        """
        for riga_fattura in self.righe.all():

            riga_bolla = riga_fattura.riga_bolla
            if riga_bolla:
                riga_bolla.fatturata = False
                riga_bolla.save()

                riga_fattura.riga_bolla = None
                riga_fattura.save()

                bolla = riga_bolla.bolla
                bolla.fatturata = False
                bolla.save()

            riga_ordine = riga_fattura.riga_ordine
            if riga_ordine:
                riga_ordine.fatturata = False
                riga_ordine.save()

                riga_fattura.riga_ordine = None
                riga_fattura.save()

                ordine = riga_ordine.ordine
                ordine.fatturato = False
                ordine.save()

    class Meta:
        verbose_name_plural = "fatture clienti"


class RigaFatturaClienteManager(models.Manager):
    
    def non_cancellati(self):
        return self.filter(cancellato=False)


class RigaFatturaCliente(models.Model):
    # Il campo 'commessa' non è messo qui perché è deducibile dalla Fattura.
    fattura = models.ForeignKey(FatturaCliente, related_name="righe")
    riga_ordine = models.OneToOneField(RigaOrdineCliente, 
        null=True, blank=True, related_name="riga_fattura")
    riga_bolla = models.OneToOneField(RigaBollaCliente, 
        null=True, blank=True, related_name="riga_fattura")
    articolo = models.ForeignKey(Articolo)
    articolo_descrizione = models.CharField(max_length=1000)
    articolo_prezzo = models.DecimalField(max_digits=13, decimal_places=2)
    sconto_percentuale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    articolo_unita_di_misura = models.CharField(max_length=2, 
        choices=UNITA_MISURA_CHOICES, default=UNITA_MISURA_NUMERO)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    totale = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.CharField(max_length=500, blank=True, default="")
    cancellato = models.BooleanField(default=False)
    objects = RigaFatturaClienteManager()

    def __str__(self):
        return "{} - {}".format(self.fattura.codice, self.articolo_descrizione)

    class Meta:
        verbose_name_plural = "righe fatture clienti"




##############  FORNITORI 


class CertificazioneFerroManager(models.Manager):
    
    def getCertificazioneDefault(self):        
        return self.filter(descrizione="3.3")

class CertificazioneFerro(models.Model):
    """
    Per ora l'issue sulla certificazione del ferro è sospesa, quindi questo modello non è utilizzato.
    """
    descrizione = models.CharField(max_length=50)
    objects = CertificazioneFerroManager()

    class Meta:
        verbose_name_plural = "Certificazioni ferro"

    def __str__(self):
        return "Certificazione {}".format(self.descrizione)


class WMSManagerMixin(object):

    def non_cancellati(self):
        return self.filter(cancellato=False)

    def next_codice(self):
        # restituisce il codice più grande già presente nel db, aumentato di 1
        year = datetime.now().year % 1000
        radice = "{}{}".format(self.prefisso, year)
        aggr_max = self.filter(codice__startswith=radice).aggregate(Max('codice'))
        max_str = aggr_max['codice__max']
        if max_str:
            max_int = int(max_str[len(radice):])
        else:
            max_int = 0
        next_codice = "{0}{1:04d}".format(radice, max_int+1)
        return next_codice


class WMSRigheManagerMixin(object):

    def non_cancellati(self):
        return self.filter(cancellato=False)


class PreventivoFornitoreManager(WMSManagerMixin, models.Manager):
    prefisso = PREVENTIVO_FORNITORE_PREFIX


class PreventivoFornitore(models.Model):
    codice = models.CharField(max_length=9)
    codice_preventivo_fornitore = models.CharField(max_length=15, 
        null=True, blank=True)
    data = models.DateField()
    data_preventivo_fornitore = models.DateField(null=True)
    fornitore = models.ForeignKey(Entita, limit_choices_to= \
        {'is_supplier':True, 'cancellato': False})
    commessa = models.ForeignKey(Commessa, null=True, blank=True, 
        related_name="preventivi_fornitori")
    oggetto = models.CharField(max_length=150, null=True, blank=True)
    accettato = models.BooleanField(default=False)
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)
    persona_di_riferimento = models.CharField(max_length=PERSONA_DI_RIFERIMENTO_LENGTH,
        null=False, blank=True, default="")    
    pagamento = models.ForeignKey(TipoPagamento, default=1)
    aliquota_IVA = models.ForeignKey(AliquotaIVA, null=True, blank=True)
    totale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    totale_su_stampa = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = PreventivoFornitoreManager()

    def __str__(self):
        return "{} - {}".format(self.codice, self.fornitore.get_nome_completo())

    def aggiorna_stato(self):
        """
        Verifica le righe di questo preventivo e se sono tutte accettate, marca
        questo preventivo come accettato.
        """
        righe_non_cancellate = self.righe.filter(cancellato=False)
        if righe_non_cancellate.count() > 0:
            if not righe_non_cancellate.filter(accettata=False).exists():
                self.accettato = True
                self.save()

    def imposta_commessa(self, commessa):
        """
        Imposta la commessa in un preventivo utilizzato per un ordine.
        """
        self.commessa = commessa
        self.save()

    def aggiorna_totale(self):
        totale_preventivo = self.righe.filter(cancellato=False).aggregate(Sum('totale'))
        # quando tutte le righe del preventivo sono cancellate, il totale
        # diventerebbe null. Quindi aggiungo "or 0"
        self.totale = totale_preventivo['totale__sum'] or 0
        self.save()

    class Meta:
        verbose_name_plural = "preventivi fornitori"


class RigaPreventivoFornitoreManager(WMSRigheManagerMixin, models.Manager):
    pass


class RigaPreventivoFornitore(models.Model):
    preventivo = models.ForeignKey(PreventivoFornitore, related_name="righe")
    articolo = models.ForeignKey(Articolo)
    articolo_descrizione = models.CharField(max_length=1000)
    articolo_codice_fornitore = models.CharField(max_length=200, null=True, blank=True)
    articolo_prezzo = models.DecimalField(max_digits=13, decimal_places=2)
    sconto_percentuale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    articolo_unita_di_misura = models.CharField(max_length=2, 
        choices=UNITA_MISURA_CHOICES, default=UNITA_MISURA_NUMERO)
    accettata = models.BooleanField(default=False)
    data_consegna = models.DateField(null=True)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    totale = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.CharField(max_length=500, blank=True, default="")
    cancellato = models.BooleanField(default=False)
    objects = RigaPreventivoFornitoreManager()

    def get_importo(self):
        return self.quantita * self.articolo_prezzo
        
    def __str__(self):
        return "{} - {}".format(self.preventivo.codice, self.articolo_descrizione)

    class Meta:
        verbose_name_plural = "righe preventivi fornitori"


class OrdineFornitoreManager(WMSManagerMixin, models.Manager):
    prefisso = ORDINE_FORNITORE_PREFIX


class OrdineFornitore(models.Model):
    codice = models.CharField(max_length=9)
    codice_ordine_fornitore = models.CharField(max_length=15, 
        null=True, blank=True)
    data = models.DateField()
    data_ordine_fornitore = models.DateField(null=True)
    fornitore = models.ForeignKey(Entita, limit_choices_to= \
        {'is_supplier':True, 'cancellato': False})
    oggetto = models.CharField(max_length=150, null=True, blank=True)
    commessa = models.ForeignKey(Commessa, related_name="ordini_fornitori")
    bollettato = models.BooleanField(default=False)
    fatturato = models.BooleanField(default=False)
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)
    persona_di_riferimento = models.CharField(max_length=PERSONA_DI_RIFERIMENTO_LENGTH,
        null=False, blank=True, default="")
    pagamento = models.ForeignKey(TipoPagamento, default=1)
    sconto_euro = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sconto_percentuale = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    totale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    totale_su_stampa = models.BooleanField(default=True)
    aliquota_IVA = models.ForeignKey(AliquotaIVA, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = OrdineFornitoreManager()

    def __str__(self):
        return "{} (commessa: {}) - {}".format(self.codice, self.commessa.codice, 
            self.fornitore.get_nome_completo())

    def aggiorna_totale(self):
        totale_ordine = self.righe.filter(cancellato=False).aggregate(Sum('totale'))
        self.totale = totale_ordine['totale__sum'] or 0
        self.save()

    def aggiorna_stato(self):
        """
        Verifica le righe di questo ordine e se sono tutte bollettate, marca
        questo ordine come bollettato
        """
        righe_non_cancellate = self.righe.filter(cancellato=False)
        if righe_non_cancellate.count() > 0:
            if not righe_non_cancellate.filter(bollettata=False).exists():
                self.bollettato = True
                self.save()

    def aggiorna_campo_fatturato(self):
        """
        Verifica le righe di questo ordine e se sono tutte fatturate, marca
        questo ordine come fatturato.
        """
        righe_non_cancellate = self.righe.filter(cancellato=False)
        if righe_non_cancellate.count() > 0:
            if not righe_non_cancellate.filter(fatturata=False).exists():
                self.fatturato = True
                self.save()

    class Meta:
        verbose_name_plural = "ordini fornitori"


class RigaOrdineFornitoreManager(WMSRigheManagerMixin, models.Manager):
    pass


class RigaOrdineFornitore(models.Model):
    ordine = models.ForeignKey(OrdineFornitore, related_name="righe")
    riga_preventivo = models.OneToOneField(RigaPreventivoFornitore, related_name="riga_ordine",
        null=True, blank=True)
    # la commessa viene settata nel modello OrdineFornitore, quindi il 
    # seguente campo vale sempre null e potrebbe essere cancellato
    #### commessa = models.ForeignKey(Commessa, null=True, blank=True)
    articolo = models.ForeignKey(Articolo)
    articolo_codice_fornitore = models.CharField(max_length=200, null=True, blank=True)
    articolo_descrizione = models.CharField(max_length=1000)
    articolo_prezzo = models.DecimalField(max_digits=16, decimal_places=5)
    sconto_percentuale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    articolo_unita_di_misura = models.CharField(max_length=2, 
        choices=UNITA_MISURA_CHOICES, default=UNITA_MISURA_NUMERO)
    data_consegna = models.DateField(null=True)
    bollettata = models.BooleanField(default=False)
    fatturata = models.BooleanField(default=False)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    totale = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.CharField(max_length=500, blank=True, default="")
    cancellato = models.BooleanField(default=False)
    objects = RigaOrdineFornitoreManager()

    def __str__(self):
        return "{} - {}".format(self.ordine.codice, self.articolo)

    class Meta:
        verbose_name_plural = "righe ordini fornitori"


class BollaFornitoreManager(WMSManagerMixin, models.Manager):
    prefisso = BOLLA_FORNITORE_PREFIX

    def get_default_causale_trasporto(self):
        return 1 # vendita

    def get_default_trasporto_a_cura_di(self):
        return 3 # mittente



class BollaFornitore(models.Model):
    codice = models.CharField(max_length=9)
    codice_bolla_fornitore = models.CharField(max_length=15, 
        null=True, blank=True)
    data = models.DateField()
    data_bolla_fornitore = models.DateField(null=True)
    fornitore = models.ForeignKey(Entita, limit_choices_to= \
        {'is_supplier':True, 'cancellato': False})
    oggetto = models.CharField(max_length=150, null=True, blank=True)
    commessa = models.ForeignKey(Commessa, related_name="bolle_fornitori")
    persona_di_riferimento = models.CharField(max_length=PERSONA_DI_RIFERIMENTO_LENGTH,
        null=False, blank=True, default="")
    fatturata = models.BooleanField(default=False)
    aspetto_esteriore = models.ForeignKey(TipoAspettoEsteriore, null=True, blank=True)
    causale_trasporto = models.ForeignKey(TipoCausaleTrasporto)
    porto = models.ForeignKey(TipoPorto, null=True, blank=True)
    trasporto_a_cura = models.ForeignKey(TipoTrasportoACura)
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)

    # peso netto, peso lordo e numero colli sono campi che solitamente rimangono
    # vuoti e sono compilati a mano dal magazziniere quando prepara la spedizione
    peso_netto = models.CharField(max_length=50, null=True, blank=True, default='0')
    peso_lordo = models.CharField(max_length=50, null=True, blank=True, default='0')
    numero_colli = models.PositiveIntegerField(null=True, blank=True)
    vettore = models.ForeignKey(Entita, null=True, blank=True, \
        related_name="bolle_trasportate_fornitori", \
        limit_choices_to= {'is_supplier':True, 'vettore':True, 'cancellato': False})
    # la classe di corrosività è usata solo sulle stampe e solo se la causale 
    # trasporto è 'C/lavorazione'
    classe_di_corrosivita = models.CharField(max_length=20, default="C3")
    note = models.TextField(null=True, blank=True)
    cancellato = models.BooleanField(default=False)
    objects = BollaFornitoreManager()

    def __str__(self):
        return "{} - {}".format(self.codice, self.fornitore.get_nome_completo())

    """
    def aggiorna_totale(self):
        totale_bolla = self.righe.filter(cancellato=False).aggregate(Sum('totale'))
        self.totale = totale_bolla['totale__sum'] or 0
        self.save()
    """

    def aggiorna_campo_fatturato(self):
        """
        Verifica le righe di questa bolla e se sono tutte fatturate, marca
        questa bolla come fatturato.
        """
        righe_non_cancellate = self.righe.filter(cancellato=False)
        if righe_non_cancellate.count() > 0:
            if not righe_non_cancellate.filter(fatturata=False).exists():
                self.fatturata = True
                self.save()

    def get_scarichi(self):
        """
        Restituisce i movimenti non cancellati di tipo scarico legati ad una bolla
        Fornitore.
        """
        tipo_scarico = TipoMovimento.objects.get_scarico()
        return self.movimenti.filter(tipo_movimento=tipo_scarico, cancellato=False)

    class Meta:
        verbose_name_plural = "bolle fornitori"


class RigaBollaFornitoreManager(WMSRigheManagerMixin, models.Manager):
    pass    


class RigaBollaFornitore(models.Model):
    bolla = models.ForeignKey(BollaFornitore, related_name="righe")
    #ordine = models.ForeignKey(OrdineFornitore, related_name="righe_bolle",
    #    null=True, blank=True)
    riga_ordine = models.OneToOneField(RigaOrdineFornitore, 
        null=True, blank=True, related_name="riga_bolla")
    #commessa = è memorizzata sulla bolla
    fatturata = models.BooleanField(default=False)
    articolo = models.ForeignKey(Articolo)
    articolo_codice_fornitore = models.CharField(max_length=200, null=True, blank=True)
    articolo_descrizione = models.CharField(max_length=1000)
    #articolo_prezzo = models.DecimalField(max_digits=13, decimal_places=2)
    articolo_unita_di_misura = models.CharField(max_length=2, 
        choices=UNITA_MISURA_CHOICES, default=UNITA_MISURA_NUMERO)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    # data_consegna non va creata?????
    #totale = models.DecimalField(max_digits=15, decimal_places=2)
    carico = models.OneToOneField(Movimento, null=True, blank=True, related_name="riga_bolla")
    note = models.CharField(max_length=500, blank=True, default="")
    cancellato = models.BooleanField(default=False)
    objects = RigaBollaFornitoreManager()

    def __str__(self):
        return "{} - {}".format(self.bolla.codice, self.articolo_descrizione)

    class Meta:
        verbose_name_plural = "righe bolle fornitori"


class FatturaFornitoreManager(WMSManagerMixin, models.Manager):
    prefisso = FATTURA_FORNITORE_PREFIX


class FatturaFornitore(models.Model):
    codice = models.CharField(max_length=9)
    codice_fattura_fornitore = models.CharField(max_length=15, 
        null=True, blank=True)
    data = models.DateField()
    data_fattura_fornitore = models.DateField(null=True)
    fornitore = models.ForeignKey(Entita, limit_choices_to= \
        {'is_supplier':True, 'cancellato': False})
    oggetto = models.CharField(max_length=150, null=True, blank=True)
    commessa = models.ForeignKey(Commessa, related_name="fatture_fornitori")
    persona_di_riferimento = models.CharField(max_length=PERSONA_DI_RIFERIMENTO_LENGTH,
        null=False, blank=True, default="")
    destinazione = models.ForeignKey(Indirizzo, null=True, blank=True)
    imponibile = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sconto_euro = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sconto_percentuale = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    imponibile_netto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    aliquota_IVA = models.ForeignKey(AliquotaIVA, null=True, blank=True, 
        help_text="Può valere Null quando si crea partendo da una bolla.")
    totale_iva = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    totale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pagamento = models.ForeignKey(TipoPagamento, default=1)
    banca_di_appoggio = models.ForeignKey(ContoCorrente, null=True, blank=True)
    ##    Totale su stampa?
    note = models.TextField(null=True, blank=True)
    #da_confermare = models.BooleanField(default=False, help_text="campo settato "
    #    + "a True quando la fattura è creata con valori di default")
    cancellato = models.BooleanField(default=False)
    objects = FatturaFornitoreManager()

    def __str__(self):
        return "{} - {}".format(self.codice, self.fornitore.get_nome_completo())

    def aggiorna_totale(self):
        imponibile_obj = self.righe.filter(cancellato=False).aggregate(Sum('totale'))
        self.imponibile = imponibile_obj['totale__sum'] or Decimal(0)
        if self.sconto_euro:
            self.imponibile_netto = self.imponibile - self.sconto_euro
        elif self.sconto_percentuale:
            self.imponibile_netto = self.imponibile * (1 - self.sconto_percentuale / 100)
        else:
            self.imponibile_netto = self.imponibile
        self.imponibile_netto = self.imponibile_netto.quantize(Decimal('0.01'))

        self.totale_iva = self.imponibile_netto * (self.aliquota_IVA.percentuale / 100)
        self.totale_iva = self.totale_iva.quantize(Decimal('0.01'))

        self.totale = self.imponibile_netto + self.totale_iva
        self.save()

    class Meta:
        verbose_name_plural = "fatture fornitori"


class RigaFatturaFornitoreManager(WMSRigheManagerMixin, models.Manager):
    pass


class RigaFatturaFornitore(models.Model):
    # Il campo 'commessa' non è messo qui perché è deducibile dalla Fattura.
    fattura = models.ForeignKey(FatturaFornitore, related_name="righe")
    riga_ordine = models.OneToOneField(RigaOrdineFornitore, 
        null=True, blank=True, related_name="riga_fattura")
    riga_bolla = models.OneToOneField(RigaBollaFornitore, 
        null=True, blank=True, related_name="riga_fattura")
    articolo = models.ForeignKey(Articolo)
    articolo_codice_fornitore = models.CharField(max_length=200, null=True, blank=True)
    articolo_descrizione = models.CharField(max_length=1000)
    articolo_prezzo = models.DecimalField(max_digits=16, decimal_places=5)
    sconto_percentuale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    articolo_unita_di_misura = models.CharField(max_length=2, 
        choices=UNITA_MISURA_CHOICES, default=UNITA_MISURA_NUMERO)
    quantita = models.DecimalField('quantità', max_digits=15, decimal_places=2)
    # data_consegna non va creata????
    totale = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.CharField(max_length=500, blank=True, default="")
    cancellato = models.BooleanField(default=False)
    objects = RigaFatturaFornitoreManager()

    def __str__(self):
        return "{} - {}".format(self.fattura.codice, self.articolo_descrizione)

    class Meta:
        verbose_name_plural = "righe fatture fornitori"
