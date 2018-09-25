#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from django.contrib.auth.models import User, Permission
from anagrafiche.models import *

# DOCUMENTAZIONE:
# http://www.django-rest-framework.org/api-guide/relations/
#
# http://www.django-rest-framework.org/api-guide/serializers/#validation
#
# http://www.django-rest-framework.org/api-guide/relations/


# ESEMPI: 
# Per aggiungere un campo chiamato 'pagamento_display':
# pagamento_display = serializers.SerializerMethodField('get_pagamento_label')
# 
# Aggiungere 'pagamento_display' nei fields
# 
# def get_pagamento_label(self, obj):
#     return obj.get_pagamento_display()

######################################### Validazione Codice Fiscale:

re_codiceFiscale = re.compile(r'\w{3}\s*\w{3}\s*\w{5}\s*\w{5}$|\d{10}')
def valida_codice_fiscale(value, is_straniero):
    # Solleva un'eccezione se il codice fiscale non è valido. Altrimenti
    # restituisce il codice fiscale con lettere maiuscole e senza spazi.
    # Se il codice fiscale si riferisce ad uno straniero, il C.F. va 
    # sempre bene.
    if is_straniero:
        return re.sub('\s', '', value).upper()
    is_a_match = re_codiceFiscale.match(value)
    if not is_a_match:
        raise ValueError(_('Codice fiscale non valido.'))
    else:
        # elimina gli spazi e usa solo lettere maiuscole:
        value = re.sub('\s', '', value).upper()
        return ssn_validation(value)

def ssn_validation(ssn_value):
    """
    Validate Italian SSN for persons

    ``ValueError`` is raised if validation fails.
    """
    if len(ssn_value) != 16:
        raise ValueError(_('Lunghezza codice fiscale non valida.'))
    check_digit = ssn_check_digit(ssn_value)
    if ssn_value[15] != check_digit:
        raise ValueError(_('Check digit does not match.'))
    return ssn_value

def ssn_check_digit(value):
    "Calculate Italian social security number check digit."
    # copiato da local_flavor/it/util.py
    ssn_even_chars = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, 'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7,
        'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15,
        'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23,
        'Y': 24, 'Z': 25
    }
    ssn_odd_chars = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8':
        19, '9': 21, 'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15,
        'H': 17, 'I': 19, 'J': 21, 'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11,
        'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14, 'U': 16, 'V': 10, 'W': 22,
        'X': 25, 'Y': 24, 'Z': 23
    }
    # Chars from 'A' to 'Z'
    ssn_check_digits = [chr(x) for x in range(65, 91)]

    ssn = value.upper()
    total = 0
    for i in range(0, 15):
        try:
            if i % 2 == 0:
                total += ssn_odd_chars[ssn[i]]
            else:
                total += ssn_even_chars[ssn[i]]
        except KeyError:
            msg = "Character '%(char)s' is not allowed." % {'char': ssn[i]}
            raise ValueError(msg)
    return ssn_check_digits[total % 26]

########################################### Validazione  Partita IVA:

def valida_partita_iva(vat_number, is_straniero):
    # Solleva un'eccezione se la partita iva ricevuta non è valida.
    # Nel caso la partita iva si riferisca ad un cliente straniero, 
    # la partita IVA va sempre bene, basta che il campo non sia vuoto.
    #
    # copiato da local_flavor/it/util.py ma ho aggiunto la gestione
    # dei clienti stranieri.
    if is_straniero:
        # togli gli spazi e usa solo lettere maiuscole. 
        return re.sub('\s', '', vat_number).upper()
    vat_number = str(int(vat_number)).zfill(11)
    check_digit = vat_number_check_digit(vat_number[0:10])
    if vat_number[10] != check_digit:
        raise ValueError(_('Cifra di controllo non corrispondente.'))
    return smart_text(vat_number)

def vat_number_check_digit(vat_number):
    "Calculate Italian VAT number check digit."
    # copiato da local_flavor/it/util.py
    normalized_vat_number = smart_text(vat_number).zfill(10)
    total = 0
    for i in range(0, 10, 2):
        total += int(normalized_vat_number[i])
    for i in range(1, 11, 2):
        quotient, remainder = divmod(int(normalized_vat_number[i]) * 2, 10)
        total += quotient + remainder
    return smart_text((10 - total % 10) % 10)

################################################### Validazione IBAN:

re_iban = re.compile(r'[I|i][t|T][ ]?\d{2}[ ]?[a-zA-Z][ ]?\d{5}[ ]?\d{5}[ ]?\d{12}')
def valida_codice_IBAN(value):
    # solleva un eccezione se l'IBAN non è valido o ritorna il codice
    # IBAN senza spazi e con le lettere maiuscole
    is_a_match = re_iban.match(value)
    if not is_a_match:
        raise ValueError(_('IBAN non valido.'))
    else:
        # elimina gli spazi e usa solo lettere maiuscole:
        value = re.sub('\s', '', value).upper()
        return value

######################################################### Serializer:

class UserSerializer(serializers.ModelSerializer):
    permessi = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'permessi')
        read_only_fields = ('id', 'username', 'first_name', 'last_name', 'permessi')

    def get_permessi(self, obj):
        permissions = Permission.objects.all()
        user_permissions = {}
        for p in permissions:
            user_permissions[p.name] = obj.has_perm("anagrafiche.{}".format(p.codename))

        return user_permissions


class TipoPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPagamento
        fields = ('id', 'descrizione')


class IndirizzoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Indirizzo
        fields = ('id', 'entita', 'tipo', 'via1', 'via2', 'citta', \
            'provincia', 'cap', 'nazione')

    def validate_cap(self, value):
        value = value.strip()
        if (len(value) != 5) or not value.isdigit():
            raise serializers.ValidationError("Il campo 'cap' deve essere composto da 5 cifre.")
        return value

    def validate_provincia(self, value):
        value = value.strip()
        if (len(value) != 2) or not value.isalpha():
            raise serializers.ValidationError("Il campo 'provincia' deve contenere 2 lettere.")
        return value


class ContattoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contatto
        fields = ('id', 'entita', 'tipo', 'valore', 'custom_label', 'note')


class ContoCorrenteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContoCorrente
        fields = ('id', 'entita', 'predefinito', 'iban', 'swift', \
            'straniero', 'intestatario', 'nome_banca', 'filiale')

    def validate(self, data):
        # se il conto non è italiano, basta che il campo iban non 
        # sia vuoto.
        straniero = data.get('straniero')
        iban = data.get('iban')
        errorMsg = ""
        if not straniero:
            # valida_codice_iban oltre a fare la validazione del campo
            # restituisce l'iban senza spazi e con le lettere maiuscole
            try: 
                data['iban'] = valida_codice_IBAN(iban)
            except ValueError:
                errorMsg += "IBAN non valido. "

        if errorMsg:
            raise serializers.ValidationError(errorMsg)
        return data


# questa è un'api che useremo mai, ma ci serve per creare nested 
# relationships
class ProprietarioSerializer(serializers.ModelSerializer):
    indirizzi = serializers.SerializerMethodField()
    contatti = serializers.SerializerMethodField()
    conti_correnti = serializers.SerializerMethodField()

    class Meta:
        model = Entita
        fields = ('id', 'codice', 'tipo', 'nome', 'cognome', 'ragione_sociale', \
            'codice_fiscale', 'partita_iva', 'indirizzi', 'contatti',\
            'conti_correnti')

    def get_indirizzi(self, obj):
        indirizzi_non_cancellati = obj.get_indirizzi()
        indirizzi_serializzati = IndirizzoSerializer(indirizzi_non_cancellati, many=True)
        return indirizzi_serializzati.data

    def get_contatti(self, obj):
        contatti_non_cancellati = obj.get_contatti()
        contatti_serializzati = ContattoSerializer(contatti_non_cancellati, many=True)
        return contatti_serializzati.data

    def get_conti_correnti(self, obj):
        conti_correnti_non_cancellati = obj.get_conti_correnti()
        conti_correnti_serializzati = ContoCorrenteSerializer(conti_correnti_non_cancellati, many=True)
        return conti_correnti_serializzati.data


class ClienteSerializer(serializers.ModelSerializer):
    pagamento_label = serializers.SerializerMethodField()
    indirizzi = serializers.SerializerMethodField()
    contatti = serializers.SerializerMethodField()
    conti_correnti = serializers.SerializerMethodField()

    class Meta:
        model = Entita
        fields = ('id', 'codice', 'tipo', 'nome', 'cognome', 'ragione_sociale', \
            'codice_fiscale', 'partita_iva', 'costo_riba', 'straniero', \
            'pagamento', 'pagamento_label', 'persona_di_riferimento', 'indirizzi', \
            'contatti', 'conti_correnti', 'is_supplier', 'vettore')
        read_only_fields = ('id', 'codice', 'indirizzi')

    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione

    def get_indirizzi(self, obj):
        indirizzi_non_cancellati = obj.get_indirizzi()
        indirizzi_serializzati = IndirizzoSerializer(indirizzi_non_cancellati, many=True)
        return indirizzi_serializzati.data

    def get_contatti(self, obj):
        contatti_non_cancellati = obj.get_contatti()
        contatti_serializzati = ContattoSerializer(contatti_non_cancellati, many=True)
        return contatti_serializzati.data

    def get_conti_correnti(self, obj):
        conti_correnti_non_cancellati = obj.get_conti_correnti()
        conti_correnti_serializzati = ContoCorrenteSerializer(conti_correnti_non_cancellati, many=True)
        return conti_correnti_serializzati.data

    def validate_codice(self, value):
        if not value.strip():
            raise serializers.ValidationError("Il campo 'codice' è obbligatorio.")
        return value
    
    def validate(self, data):
        # Se persona fisica servono nome, cognome e codice ficale.
        # Se persona giuridica servono ragione sociale e partita iva.
        tipo = data.get('tipo')
        nome = data.get('nome')
        cognome = data.get('cognome')
        ragione_sociale = data.get('ragione_sociale')
        codice_fiscale = data.get('codice_fiscale')
        partita_iva = data.get('partita_iva')
        straniero = data.get('straniero')
        errorMsg = ""
        if tipo == PERSONA_FISICA:
            if not nome:
                errorMsg += "Campo 'nome' obbligatorio per le persone fisiche. "
            if not cognome:
                errorMsg += "Campo 'cognome' obbligatorio per le persone fisiche. "
            if codice_fiscale:
                try: 
                    # se il CF è valido, rimpiazzalo con la sua versione
                    # senza spazi e con le lettere maiuscole
                    data['codice_fiscale'] = valida_codice_fiscale(codice_fiscale, straniero)
                except ValueError:
                    errorMsg += "Codice fiscale non valido. "
            else:
                errorMsg += "Campo 'codice fiscale' obbligatorio per le persone fisiche. "
            if partita_iva:
                try: 
                    data['partita_iva'] = valida_partita_iva(partita_iva, straniero)
                except ValueError:
                    errorMsg += "Partita IVA non valida."
            # niente else:  per le persone fisiche la partita IVA non è obbligatoria
        else:
            if not ragione_sociale:
                errorMsg += "Campo 'ragione sociale' obbligatorio per le persone giuridiche. "
            if partita_iva:
                try: 
                    data['partita_iva'] = valida_partita_iva(partita_iva, straniero)
                except ValueError:
                    errorMsg += "Partita IVA non valida. "
            else:
                errorMsg += "Campo 'partita IVA' obbligatorio per le persone giuridiche. "
            if codice_fiscale:
                # le persone giuridiche possono avere codice fiscale che ha il 
                # formato di una partita IVA
                try: 
                    data['codice_fiscale'] = valida_partita_iva(codice_fiscale, straniero)
                except ValueError:
                    errorMsg += "Codice fiscale non valido. "

        if errorMsg:
            raise serializers.ValidationError(errorMsg)

        return data


class FornitoreSerializer(serializers.ModelSerializer):
    pagamento_label = serializers.SerializerMethodField()
    indirizzi = serializers.SerializerMethodField()
    contatti = serializers.SerializerMethodField()
    conti_correnti = serializers.SerializerMethodField()

    class Meta:
        model = Entita
        fields = ('id', 'codice', 'tipo', 'nome', 'cognome', 'ragione_sociale', \
            'codice_fiscale', 'partita_iva', 'costo_riba', 'straniero', \
            'pagamento', 'pagamento_label', 'persona_di_riferimento', \
            'vettore', 'indirizzi', 'contatti', 'conti_correnti', 'is_client')
        read_only_fields = ('id', 'codice', 'indirizzi')

    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione

    def get_indirizzi(self, obj):
        indirizzi_non_cancellati = obj.get_indirizzi()
        indirizzi_serializzati = IndirizzoSerializer(indirizzi_non_cancellati, many=True)
        return indirizzi_serializzati.data

    def get_contatti(self, obj):
        contatti_non_cancellati = obj.get_contatti()
        contatti_serializzati = ContattoSerializer(contatti_non_cancellati, many=True)
        return contatti_serializzati.data

    def get_conti_correnti(self, obj):
        conti_correnti_non_cancellati = obj.get_conti_correnti()
        conti_correnti_serializzati = ContoCorrenteSerializer(conti_correnti_non_cancellati, many=True)
        return conti_correnti_serializzati.data
    
    """
    def validate_codice(self, value):
        if not value.strip():
            raise serializers.ValidationError("Il campo 'codice' è obbligatorio.")
        return value
    """
    
    def validate(self, data):
        # Se persona fisica servono nome, cognome e codice ficale.
        # Se persona giuridica servono ragione sociale e partita iva.
        tipo = data.get('tipo')
        nome = data.get('nome')
        cognome = data.get('cognome')
        ragione_sociale = data.get('ragione_sociale')
        codice_fiscale = data.get('codice_fiscale')
        partita_iva = data.get('partita_iva')
        straniero = data.get('straniero')
        errorMsg = ""
        if tipo == PERSONA_FISICA:
            if not nome:
                errorMsg += "Campo 'nome' obbligatorio per le persone fisiche. "
            if not cognome:
                errorMsg += "Campo 'cognome' obbligatorio per le persone fisiche. "
            if codice_fiscale:
                try: 
                    # se il CF è valido, rimpiazzalo con la sua versione
                    # senza spazi e con le lettere maiuscole
                    data['codice_fiscale'] = valida_codice_fiscale(codice_fiscale, straniero)
                except ValueError:
                    errorMsg += "Codice fiscale non valido. "
            else:
                errorMsg += "Campo 'codice fiscale' obbligatorio per le persone fisiche. "
            if partita_iva:
                try: 
                    data['partita_iva'] = valida_partita_iva(partita_iva, straniero)
                except ValueError:
                    errorMsg += "Partita IVA non valida."
            # niente else:  per le persone fisiche la partita IVA non è obbligatoria
        else:
            if not ragione_sociale:
                errorMsg += "Campo 'ragione sociale' obbligatorio per le persone giuridiche. "
            if partita_iva:
                try: 
                    data['partita_iva'] = valida_partita_iva(partita_iva, straniero)
                except ValueError:
                    errorMsg += "Partita IVA non valida. "
            else:
                errorMsg += "Campo 'partita IVA' obbligatorio per le persone giuridiche. "
            if codice_fiscale:
                # le persone giuridiche possono avere codice fiscale che ha il 
                # formato di una partita IVA
                try: 
                    data['codice_fiscale'] = valida_partita_iva(codice_fiscale, straniero)
                except ValueError:
                    errorMsg += "Codice fiscale non valido. "

        if errorMsg:
            raise serializers.ValidationError(errorMsg)

        return data


class CommessaSerializer(serializers.ModelSerializer):
    preventivi = serializers.SerializerMethodField()
    ordini = serializers.SerializerMethodField()
    bolle = serializers.SerializerMethodField()
    fatture = serializers.SerializerMethodField()

    class Meta:
        model = Commessa
        fields = ('id', 'codice', 'cliente', 'data_apertura', 'data_consegna', 
            'prodotto', 'destinazione', 'preventivi', 'ordini', 'bolle', 'fatture')
        read_only_fields = ('id', 'codice')

    def get_preventivi(self, obj):
        preventivi_non_cancellati = obj.preventivi.filter(cancellato=False)
        preventivi_serializzati = [{'id': x.id, 'codice': x.codice, 'oggetto':x.oggetto } for x in preventivi_non_cancellati]
        return preventivi_serializzati

    def get_ordini(self, obj):
        ordini_non_cancellati = obj.ordini_clienti.filter(cancellato=False)
        ordini_serializzati = [{'id': x.id, 'codice': x.codice, 'oggetto':x.oggetto } for x in ordini_non_cancellati]
        return ordini_serializzati
    
    def get_bolle(self, obj):
        bolle_non_cancellate = obj.bolle_clienti.filter(cancellato=False)
        bolle_serializzate = [{'id': x.id, 'codice': x.codice, 'data':x.data, 'oggetto':x.oggetto } for x in bolle_non_cancellate]
        return bolle_serializzate
    
    def get_fatture(self, obj):
        fatture_non_cancellate = obj.fatture_clienti.filter(cancellato=False)
        fatture_serializzate = [{'id': x.id, 'codice': x.codice, 'data':x.data, 'oggetto':x.oggetto } for x in fatture_non_cancellate]
        return fatture_serializzate

    def validate_cliente(self, value):
        # value è un'istanza del modello Entita
        if not value.is_client:
            raise serializers.ValidationError("L'entità selezionata non è un cliente.") 
        return value

    def validate(self, data):
        cliente = data.get('cliente')
        destinazione = data.get('destinazione')
        if destinazione and destinazione.entita != cliente:
            raise serializers.ValidationError("La destinazione scelta non " +
                "appartiene al cliente selezionato.")
        return data


class DipendenteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dipendente
        fields = ('id', 'nome', 'cognome', 'costo_orario', 'matricola', 'data_assunzione',
            'data_cessazione', 'scadenza_visita_medica', 'codice_fiscale', 'cellulare', 
            'salta_validazione_cf', 'attivo', 'diretto', 'interno')

    def validate(self, data):
        codice_fiscale = data.get('codice_fiscale')
        salta_validazione_cf = data.get('salta_validazione_cf')
        errorMsg = ""
        if codice_fiscale:
            try: 
                # se il CF è valido, rimpiazzalo con la sua versione
                # senza spazi e con le lettere maiuscole
                data['codice_fiscale'] = valida_codice_fiscale(codice_fiscale, 
                    salta_validazione_cf)
            except ValueError:
                errorMsg = "Codice fiscale non valido."

        if errorMsg:
            raise serializers.ValidationError(errorMsg)
        return data

class TipoLavoroSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoLavoro
        fields = ('id', 'descrizione')


class ConsuntivoSerializer(serializers.ModelSerializer):
    tipo_lavoro_label = serializers.SerializerMethodField()
    commessa_label = serializers.SerializerMethodField()

    class Meta:
        model = Consuntivo
        fields = ('id', 'data', 'ore', 'tipo_lavoro', 'tipo_lavoro_label', \
            'dipendente', 'commessa', 'commessa_label', 'note')

    def get_tipo_lavoro_label(self, obj):
        return obj.tipo_lavoro.descrizione

    def get_commessa_label(self, obj):
        return obj.commessa.codice


class ClasseArticoloSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClasseArticolo
        fields = ('id', 'sigla', 'descrizione')


class TipoMovimentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoMovimento
        fields = ('id', 'descrizione', 'segno')


class ArticoloSerializer(serializers.ModelSerializer):
    classe_label = serializers.SerializerMethodField()
    unita_di_misura_label = serializers.SerializerMethodField()

    class Meta:
        model = Articolo
        fields = ('id', 'codice', 'classe', 'classe_label', 'descrizione', 'codice_fornitore', \
            'note', 'unita_di_misura', 'unita_di_misura_label', 'prezzo_di_listino', 'lt', 'ss', \
            'scorta')
        # il campo codice è read only perché viene settato in automatico 
        # nel metodo perform_create di ArticoloViewSet
        read_only_fields = ('id', 'codice')

    def get_classe_label(self, obj):
        return obj.classe.descrizione

    def get_unita_di_misura_label(self, obj):
        return obj.get_unita_di_misura_display()


class GiacenzaSerializer(serializers.ModelSerializer):
    lotto_label = serializers.SerializerMethodField()
    articolo_label = serializers.SerializerMethodField()
    unita_di_misura = serializers.SerializerMethodField()
    commessa = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()

    class Meta:
        model = Giacenza
        fields = ('id', 'lotto', 'lotto_label', 'articolo', 'articolo_label',  'unita_di_misura', \
            'quantita', 'note', 'commessa', 'commessa_codice')
        read_only_fields = ('id')

    def get_lotto_label(self, obj):
        return obj.lotto.codice

    def get_articolo_label(self, obj):
        return obj.articolo.descrizione

    def get_unita_di_misura(self, obj):
        return obj.articolo.get_unita_di_misura_display()

    def get_commessa(self, obj):
        return obj.lotto.commessa.id

    def get_commessa_codice(self, obj):
        return obj.lotto.commessa.codice


class MovimentoSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_label = serializers.SerializerMethodField()
    lotto_codice = serializers.SerializerMethodField()
    tipo_movimento_label = serializers.SerializerMethodField()
    autore_nome = serializers.SerializerMethodField()
    destinazione_codice = serializers.SerializerMethodField()
    abs_quantita = serializers.SerializerMethodField()

    class Meta:
        model = Movimento
        fields = ('id', 'articolo', 'articolo_codice', 'articolo_label', \
            'lotto', 'lotto_codice', 'data', 'tipo_movimento', 'tipo_movimento_label', \
            'autore', 'autore_nome', 'quantita', 'abs_quantita', 'unita_di_misura', 'destinazione', \
            'destinazione_codice')
        read_only_fields = ('id', 'autore', 'unita_di_misura', 'riga_bolla')

    def get_articolo_codice(self, obj):
        return obj.articolo.codice
    
    def get_articolo_label(self, obj):
        return obj.articolo.descrizione
    
    def get_lotto_codice(self, obj):
        return obj.lotto.codice
    
    def get_tipo_movimento_label(self, obj):
        return obj.tipo_movimento.descrizione

    def get_autore_nome(self, obj):
        return obj.autore.username

    def get_destinazione_codice(self, obj):
        return obj.destinazione.codice
    
    def get_abs_quantita(self, obj):
        # nel db i movimenti di scarico sono memorizzati con valori negativi, ma a video vogliamo sempre vedere
        # valori positivi
        return abs(obj.quantita)

    def validate_quantita(self, value):
        if value < 0 :
            raise serializers.ValidationError("La quantità deve sempre essere positiva, anche quando si fa uno scarico.")
        return value

    def validate(self, data):
        articolo = data.get('articolo')
        lotto = data.get('lotto')
        destinazione = data.get('destinazione')
        tipo_movimento = data.get('tipo_movimento')
        magazzino = Commessa.objects.get_magazzino()
        scarico = TipoMovimento.objects.get_scarico()

        if not lotto.righe.filter(articolo=articolo).exists():
            raise serializers.ValidationError("L'articolo \"{}\" non fa parte del lotto {}.".format(articolo.descrizione, lotto.codice))
        # import pdb; pdb.set_trace()

        if tipo_movimento == scarico and destinazione == magazzino:
            raise serializers.ValidationError("Non si può effettuare uno scarico con destinazione 'MAGAZZINO'.")
            
        return data


class AliquotaIVASerializer(serializers.ModelSerializer):

    class Meta:
        model = AliquotaIVA
        fields = ('id', 'codice', 'descrizione', 'percentuale')


class PreventivoClienteSerializer(serializers.ModelSerializer):
    cliente_codice = serializers.SerializerMethodField()
    cliente_label = serializers.SerializerMethodField()
    pagamento_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()

    class Meta:
        model = PreventivoCliente
        fields = ('id', 'codice', 'data', 'cliente', 'cliente_codice', \
            'cliente_label', 'oggetto', 'accettato', 'pagamento', 'pagamento_label', \
            'destinazione', 'persona_di_riferimento', 'totale', 'totale_su_stampa', \
            'disegni_costruttivi', 'relazione_di_calcolo', \
            'tipo_di_acciaio', 'spessori', 'zincatura', \
            'classe_di_esecuzione', 'wps', 'verniciatura',\
            'aliquota_IVA', 'note',
            'commessa', 'commessa_codice')
        # il campo 'accettato' diventa True solo quando il preventivo
        # diventa un ordine, e quindi non è possibile cambiarlo qui
        read_only_fields = ('id', 'codice', 'accettato', 'totale')

    def get_cliente_codice(self, obj):
        return obj.cliente.codice

    def get_cliente_label(self, obj):
        return obj.cliente.get_nome_completo()
        
    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione
    
    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None


class RigaPreventivoClienteSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()

    class Meta:
        model = RigaPreventivoCliente
        fields = ('id', 'preventivo', 'articolo', 'articolo_codice', 'articolo_descrizione', \
            'articolo_prezzo', 'sconto_percentuale', 'quantita', 'articolo_unita_di_misura',  \
            'accettata', 'articolo_unita_di_misura_label', 'totale', 'note')
        read_only_fields = ('id', 'totale')

    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()


class RigaOrdineClienteSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()
    preventivo_codice = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()

    class Meta:
        model = RigaOrdineCliente
        fields = ('id', 'ordine', 'preventivo', 'preventivo_codice', 'riga_preventivo', 
            'commessa', 'commessa_codice', 'articolo', 'articolo_codice', 'sconto_percentuale',
            'articolo_descrizione', 'articolo_prezzo', 'quantita', 'articolo_unita_di_misura', 
            'articolo_unita_di_misura_label', 'totale', 'note', 'riga_bolla', 'bollettata', 'fatturata')
        read_only_fields = ('id', 'totale', 'riga_bolla')

    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()

    def get_preventivo_codice(self, obj):
        if obj.preventivo:
            return obj.preventivo.codice
        else:
            return None

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None


class RigaOrdineClienteSenzaTotaleSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()
    preventivo_codice = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()

    class Meta:
        model = RigaOrdineCliente
        fields = ('id', 'ordine', 'preventivo', 'preventivo_codice', 'riga_preventivo', 
            'commessa', 'commessa_codice', 'articolo', 'articolo_codice', 
            'articolo_descrizione', 'quantita', 'articolo_unita_di_misura', 
            'articolo_unita_di_misura_label', 'note', 'riga_bolla', 'bollettata', 'fatturata')
        ## TODO: verificare se i campi 'bollettata' e 'fatturata' non debbano essere read-only

    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()

    def get_preventivo_codice(self, obj):
        if obj.preventivo:
            return obj.preventivo.codice
        else:
            return None

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None


class OrdineClienteSerializer(serializers.ModelSerializer):
    cliente_codice = serializers.SerializerMethodField()
    cliente_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()
    pagamento_label = serializers.SerializerMethodField()
    righe = RigaOrdineClienteSerializer(many=True, read_only=True)

    class Meta:
        model = OrdineCliente
        fields = ('id', 'codice', 'data', 'cliente', 'cliente_codice',  \
            'cliente_label', 'commessa', 'commessa_codice', \
            'pagamento', 'pagamento_label', 'oggetto', 'destinazione', \
            'disegni_costruttivi', 'relazione_di_calcolo', \
            'tipo_di_acciaio', 'spessori', 'zincatura', \
            'classe_di_esecuzione', 'wps', 'verniciatura',\
            'persona_di_riferimento', 'riferimento_cliente', 'righe', 'sconto_euro', 'sconto_percentuale', \
            'aliquota_IVA', 'totale', 'totale_su_stampa', 'note', 'bollettato', \
            'fatturato')
        # Il campo 'bollettato' diventa True solo quando l'ordine
        # viene messo in una bolla, e quindi non è possibile cambiarlo qui. Stessa cosa
        # per il campo 'fatturato':
        read_only_fields = ('id', 'codice', 'totale', 'bollettato', 'fatturato')

    def get_cliente_codice(self, obj):
        return obj.cliente.codice

    def get_cliente_label(self, obj):
        return obj.cliente.get_nome_completo()

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None

    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione

    def validate_cliente(self, value):
        if not value.is_client:
            raise serializers.ValidationError("Il cliente selezionato non è valido")
        return value
    
    def validate_sconto_euro(self, value):
        if value < 0:
            raise serializers.ValidationError("Lo sconto in euro non può essere inferiore a 0.")
        return value
    
    def validate_sconto_percentuale(self, value):
        if (value < 0) or (value > 100):
            raise serializers.ValidationError("Lo sconto percentuale deve essere compreso tra 0 e 100.")
        return value

    def validate(self, data):
        sconto_euro = data.get('sconto_euro')
        sconto_percentuale = data.get('sconto_percentuale')
        if sconto_euro and sconto_percentuale:
            raise serializers.ValidationError("Non è possibile applicare sia lo "
                + "sconto percentuale che lo sconto in euro.")       
        return data


class OrdineClienteSenzaTotaleSerializer(serializers.ModelSerializer):
    cliente_codice = serializers.SerializerMethodField()
    cliente_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()
    pagamento_label = serializers.SerializerMethodField()
    righe = RigaOrdineClienteSenzaTotaleSerializer(many=True, read_only=True)

    class Meta:
        model = OrdineCliente
        fields = ('id', 'codice', 'data', 'cliente', 'cliente_codice',  \
            'cliente_label', 'commessa', 'commessa_codice', \
            'pagamento', 'pagamento_label', 'oggetto', 'destinazione', \
            'disegni_costruttivi', 'relazione_di_calcolo', \
            'tipo_di_acciaio', 'spessori', 'zincatura', \
            'classe_di_esecuzione', 'wps', 'verniciatura',\
            'persona_di_riferimento', 'riferimento_cliente', 'righe', 'sconto_euro', 'sconto_percentuale', \
             'aliquota_IVA', 'note', 'bollettato', 'fatturato')

    def get_cliente_codice(self, obj):
        return obj.cliente.codice

    def get_cliente_label(self, obj):
        return obj.cliente.get_nome_completo()

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None

    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione

class TipoCausaleTrasportoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCausaleTrasporto
        fields = ('id', 'descrizione')


class TipoAspettoEsterioreSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAspettoEsteriore
        fields = ('id', 'descrizione')


class TipoPortoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPorto
        fields = ('id', 'descrizione')


class TipoTrasportoACuraSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTrasportoACura
        fields = ('id', 'descrizione')


class RigaBollaClienteSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()
    riga_ordine_codice = serializers.SerializerMethodField()
    #commessa_codice = serializers.SerializerMethodField()

    class Meta:
        model = RigaBollaCliente
        fields = ('id', 'bolla', 'riga_ordine', 'riga_ordine_codice',
            'fatturata', 'articolo', 'articolo_codice', 
            'articolo_descrizione', 'quantita', 'articolo_unita_di_misura', 
            'articolo_unita_di_misura_label', 'note')
        ## La commessa viene settata nel modello Bolla, non nella riga:
        ## 'commessa', 'commessa_codice',
        ### Il prezzo è stato tolto e quindi anche il totale non serve:
        ### , 'articolo_prezzo', 'totale'
        ### read_only_fields = ('id', 'totale')
    
    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()

    def get_riga_ordine_codice(self, obj):
        if obj.riga_ordine:
            return obj.riga_ordine.ordine.codice
        else:
            return None

    #def get_commessa_codice(self, obj):
    #    obj.commessa.codice


class BollaClienteSerializer(serializers.ModelSerializer):
    cliente_codice = serializers.SerializerMethodField()
    cliente_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()
    aspetto_esteriore_label = serializers.SerializerMethodField()
    causale_trasporto_label = serializers.SerializerMethodField()
    porto_label = serializers.SerializerMethodField()
    trasporto_a_cura_label = serializers.SerializerMethodField()
    vettore_codice = serializers.SerializerMethodField()
    vettore_label = serializers.SerializerMethodField()
    righe = RigaBollaClienteSerializer(many=True, read_only=True)

    class Meta:
        model = BollaCliente
        fields = ('id', 'codice', 'data', 'cliente', 'cliente_codice',  \
            'cliente_label', 'commessa', 'commessa_codice', 'fatturata', \
            'destinazione', 'persona_di_riferimento', 'riferimento_cliente', 'oggetto', \
            'aspetto_esteriore', 'aspetto_esteriore_label', \
            'causale_trasporto', 'causale_trasporto_label', 'porto', \
            'porto_label', 'trasporto_a_cura', 'trasporto_a_cura_label', \
            'peso_netto', 'peso_lordo', 'numero_colli', 'vettore', \
            'vettore_codice', 'vettore_label', 'righe', 'note')
        read_only_fields = ('id', 'codice', 'totale')

    def get_cliente_codice(self, obj):
        return obj.cliente.codice

    def get_cliente_label(self, obj):
        return obj.cliente.get_nome_completo()

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None

    def get_aspetto_esteriore_label(self, obj):
        if obj.aspetto_esteriore:
            return obj.aspetto_esteriore.descrizione
        else:
            return ""

    def get_causale_trasporto_label(self, obj):
        if obj.causale_trasporto:
            return obj.causale_trasporto.descrizione
        else:
            return ""

    def get_porto_label(self, obj):
        if obj.porto:
            return obj.porto.descrizione
        else:
            return ""

    def get_trasporto_a_cura_label(self, obj):
        if obj.trasporto_a_cura:
            return obj.trasporto_a_cura.descrizione
        else:
            return ""

    def get_vettore_codice(self, obj):
        if obj.vettore:
            return obj.vettore.codice
        else:
            return ""

    def get_vettore_label(self, obj):
        if obj.vettore:
            return obj.vettore.get_nome_completo()
        else:
            return ""



class RigaFatturaClienteSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()
    riga_ordine_codice = serializers.SerializerMethodField()
    riga_bolla_codice = serializers.SerializerMethodField()

    class Meta:
        model = RigaFatturaCliente
        fields = ('id', 'fattura', 'riga_ordine', 'riga_ordine_codice',
            'riga_bolla', 'riga_bolla_codice', 'articolo', 'articolo_codice', 
            'articolo_descrizione', 'articolo_prezzo', 'sconto_percentuale', 
            'articolo_unita_di_misura', 
            'articolo_unita_di_misura_label', 'quantita', 'totale', 'note')
        ## La commessa viene settata nel modello Fattura, non nella riga:
        ## 'commessa', 'commessa_codice',
        read_only_fields = ('id', 'totale', 'riga_ordine', 'riga_bolla')
    
    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()

    def get_riga_ordine_codice(self, obj):
        if obj.riga_ordine:
            return obj.riga_ordine.ordine.codice
        else:
            return None

    def get_riga_bolla_codice(self, obj):
        if obj.riga_bolla:
            return obj.riga_bolla.bolla.codice
        else:
            return None


    def validate(self, data):
        fattura = data.get('fattura')
        if not fattura.aliquota_IVA:
            raise serializers.ValidationError("La fattura associata a questa riga non ha un'aliquota IVA settata.")
        return data


class FatturaClienteSerializer(serializers.ModelSerializer):
    cliente_codice = serializers.SerializerMethodField()
    cliente_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()
    pagamento_label = serializers.SerializerMethodField()
    righe = RigaFatturaClienteSerializer(many=True, read_only=True)

    class Meta:
        model = FatturaCliente
        fields = ('id', 'codice', 'data', 'cliente', 'cliente_codice',  \
            'cliente_label', 'commessa', 'commessa_codice', 'destinazione', \
            'persona_di_riferimento', 'riferimento_cliente', \
            'oggetto', 'imponibile', 'sconto_euro', 'sconto_percentuale', \
            'imponibile_netto', 'aliquota_IVA',  'totale_iva', 'totale', \
            'pagamento', 'pagamento_label', 'banca_di_appoggio', 'righe', \
            'note', 'da_confermare')
        read_only_fields = ('id', 'codice', 'da_confermare', 'imponibile', 
            'imponibile_netto', 'totale_iva', 'totale')

    def get_cliente_codice(self, obj):
        return obj.cliente.codice

    def get_cliente_label(self, obj):
        return obj.cliente.get_nome_completo()

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None

    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione

    def validate_banca_di_appoggio(self, value):
        if value and value.entita != Entita.objects.proprietario():
            raise serializers.ValidationError("La banca di appoggio selezionata non è valida.")
        return value

    def validate_sconto_euro(self, value):
        if value < 0:
            raise serializers.ValidationError("Lo sconto in euro non può essere inferiore a 0.")
        return value
    
    def validate_sconto_percentuale(self, value):
        if (value < 0) or (value > 100):
            raise serializers.ValidationError("Lo sconto percentuale deve essere compreso tra 0 e 100.")
        return value

    def validate(self, data):
        sconto_euro = data.get('sconto_euro')
        sconto_percentuale = data.get('sconto_percentuale')
        if sconto_euro and sconto_percentuale:
            raise serializers.ValidationError("Non è possibile applicare sia lo sconto percentuale che lo sconto in "
                                              + "euro.")
        return data


"""
class PostSerializer(serializers.ModelSerializer):
    # We also set required=False here because we will set the 
    # author of this post automatically.
    author = AccountSerializer(read_only=True, required=False)

    class Meta:
        model = Post

        fields = ('id', 'author', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    # For the same reason we used required=False in AccountSerializer, 
    # we must also add author to the list of validations we wish to skip.
    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(PostSerializer, self).get_validation_exclusions()

        return exclusions + ['author']
"""



class PreventivoFornitoreSerializer(serializers.ModelSerializer):
    fornitore_codice = serializers.SerializerMethodField()
    fornitore_label = serializers.SerializerMethodField()
    pagamento_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()

    class Meta:
        model = PreventivoFornitore
        fields = ('id', 'codice', 'codice_preventivo_fornitore', 'data', \
            'data_preventivo_fornitore', 'fornitore', 'fornitore_codice', \
            'fornitore_label', 'oggetto', 'accettato', 'pagamento', 'pagamento_label', \
            'destinazione', 'persona_di_riferimento', 'totale', 'totale_su_stampa', \
            'aliquota_IVA', 'note',
            'commessa', 'commessa_codice')
        # il campo 'accettato' diventa True solo quando il preventivo
        # diventa un ordine, e quindi non è possibile cambiarlo qui
        read_only_fields = ('id', 'codice', 'accettato', 'totale')

    def get_fornitore_codice(self, obj):
        return obj.fornitore.codice

    def get_fornitore_label(self, obj):
        return obj.fornitore.get_nome_completo()
        
    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione
    
    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None


class RigaPreventivoFornitoreSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()

    class Meta:
        model = RigaPreventivoFornitore
        fields = ('id', 'preventivo', 'articolo', 'articolo_codice', 'articolo_descrizione', \
            'articolo_prezzo', 'sconto_percentuale', 'articolo_codice_fornitore', \
            'quantita', 'articolo_unita_di_misura', 'data_consegna', \
            'accettata', 'articolo_unita_di_misura_label', 'totale', 'note')
        read_only_fields = ('id', 'totale')

    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()


class RigaOrdineFornitoreSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()
    ## la commessa si ricava dall'ordine, quindi qui la tolgo:
    ## commessa_codice = serializers.SerializerMethodField()

    class Meta:
        model = RigaOrdineFornitore
        fields = ('id', 'ordine', 'riga_preventivo', 'data_consegna',
            'articolo', 'articolo_codice_fornitore', 'articolo_codice', 'sconto_percentuale',
            'articolo_descrizione', 'articolo_prezzo', 'quantita', 'articolo_unita_di_misura', 
            'articolo_unita_di_misura_label', 'totale', 'note', 'riga_bolla', 'bollettata', 'fatturata')
        read_only_fields = ('id', 'totale', 'riga_bolla')

    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()


class OrdineFornitoreSerializer(serializers.ModelSerializer):
    fornitore_codice = serializers.SerializerMethodField()
    fornitore_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()
    pagamento_label = serializers.SerializerMethodField()
    righe = RigaOrdineFornitoreSerializer(many=True, read_only=True)

    class Meta:
        model = OrdineFornitore
        fields = ('id', 'codice', 'data', 'fornitore', 'fornitore_codice',  \
            'fornitore_label', 'commessa', 'commessa_codice', \
            'pagamento', 'pagamento_label', 'oggetto', 'destinazione', \
            'persona_di_riferimento', 'righe', 'sconto_euro', 'sconto_percentuale', \
            'aliquota_IVA', 'totale', 'totale_su_stampa', 'note', 'bollettato', \
            'fatturato')
        # Il campo 'bollettato' diventa True solo quando l'ordine
        # viene messo in una bolla, e quindi non è possibile cambiarlo qui. Stessa cosa
        # per il campo 'fatturato':
        read_only_fields = ('id', 'codice', 'totale', 'bollettato', 'fatturato')

    def get_fornitore_codice(self, obj):
        return obj.fornitore.codice

    def get_fornitore_label(self, obj):
        return obj.fornitore.get_nome_completo()

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None

    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione

    def validate_fornitore(self, value):
        if not value.is_supplier:
            raise serializers.ValidationError("Il fornitore selezionato non è valido")
        return value
    
    def validate_sconto_euro(self, value):
        if value < 0:
            raise serializers.ValidationError("Lo sconto in euro non può essere inferiore a 0.")
        return value
    
    def validate_sconto_percentuale(self, value):
        if (value < 0) or (value > 100):
            raise serializers.ValidationError("Lo sconto percentuale deve essere compreso tra 0 e 100.")
        return value

    def validate(self, data):
        sconto_euro = data.get('sconto_euro')
        sconto_percentuale = data.get('sconto_percentuale')
        if sconto_euro and sconto_percentuale:
            raise serializers.ValidationError("Non è possibile applicare sia lo "
                + "sconto percentuale che lo sconto in euro.")       
        return data

# Nel caso dei fornitori, non c'è il serializzatore OrdineSenzaTotali perché
# tutti gli utenti possono vedere i totali.


class RigaBollaFornitoreSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()
    riga_ordine_codice = serializers.SerializerMethodField()
    #commessa_codice = serializers.SerializerMethodField()

    class Meta:
        model = RigaBollaFornitore
        fields = ('id', 'bolla', 'riga_ordine', 'riga_ordine_codice',
            'fatturata', 'articolo', 'articolo_codice', 'articolo_codice_fornitore',
            'articolo_descrizione', 'quantita', 'articolo_unita_di_misura', 
            'articolo_unita_di_misura_label', 'note')
        ## La commessa viene settata nel modello Bolla, non nella riga:
        ## 'commessa', 'commessa_codice',
        ### Il prezzo è stato tolto e quindi anche il totale non serve:
        ### , 'articolo_prezzo', 'totale'
    
    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()

    def get_riga_ordine_codice(self, obj):
        if obj.riga_ordine:
            return obj.riga_ordine.ordine.codice
        else:
            return None

    #def get_commessa_codice(self, obj):
    #    obj.commessa.codice


class BollaFornitoreSerializer(serializers.ModelSerializer):
    fornitore_codice = serializers.SerializerMethodField()
    fornitore_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()
    aspetto_esteriore_label = serializers.SerializerMethodField()
    causale_trasporto_label = serializers.SerializerMethodField()
    porto_label = serializers.SerializerMethodField()
    trasporto_a_cura_label = serializers.SerializerMethodField()
    vettore_codice = serializers.SerializerMethodField()
    vettore_label = serializers.SerializerMethodField()
    righe = RigaBollaFornitoreSerializer(many=True, read_only=True)

    class Meta:
        model = BollaFornitore
        fields = ('id', 'codice', 'codice_bolla_fornitore', 'data', 'data_bolla_fornitore', \
            'fornitore', 'fornitore_codice', 'persona_di_riferimento', \
            'fornitore_label', 'commessa', 'commessa_codice', 'fatturata', \
            'destinazione', 'oggetto', 'aspetto_esteriore', 'aspetto_esteriore_label', \
            'causale_trasporto', 'causale_trasporto_label', 'porto', \
            'porto_label', 'trasporto_a_cura', 'trasporto_a_cura_label', \
            'peso_netto', 'peso_lordo', 'numero_colli', 'vettore', \
            'vettore_codice', 'vettore_label', 'righe', 'classe_di_corrosivita', 'note')
        read_only_fields = ('id', 'codice', 'totale')

    def get_fornitore_codice(self, obj):
        return obj.fornitore.codice

    def get_fornitore_label(self, obj):
        return obj.fornitore.get_nome_completo()

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None

    def get_aspetto_esteriore_label(self, obj):
        if obj.aspetto_esteriore:
            return obj.aspetto_esteriore.descrizione
        else:
            return ""

    def get_causale_trasporto_label(self, obj):
        if obj.causale_trasporto:
            return obj.causale_trasporto.descrizione
        else:
            return ""

    def get_porto_label(self, obj):
        if obj.porto:
            return obj.porto.descrizione
        else:
            return ""

    def get_trasporto_a_cura_label(self, obj):
        if obj.trasporto_a_cura:
            return obj.trasporto_a_cura.descrizione
        else:
            return ""

    def get_vettore_codice(self, obj):
        if obj.vettore:
            return obj.vettore.codice
        else:
            return ""

    def get_vettore_label(self, obj):
        if obj.vettore:
            return obj.vettore.get_nome_completo()
        else:
            return ""


class RigaFatturaFornitoreSerializer(serializers.ModelSerializer):
    articolo_codice = serializers.SerializerMethodField()
    articolo_unita_di_misura_label = serializers.SerializerMethodField()
    riga_ordine_codice = serializers.SerializerMethodField()
    riga_bolla_codice = serializers.SerializerMethodField()

    class Meta:
        model = RigaFatturaFornitore
        fields = ('id', 'fattura', 'riga_ordine', 'riga_ordine_codice',
            'riga_bolla', 'riga_bolla_codice', 'articolo', 'articolo_codice', 
            'articolo_descrizione', 'articolo_prezzo', 'sconto_percentuale', 
            'articolo_unita_di_misura', 'articolo_codice_fornitore',
            'articolo_unita_di_misura_label', 'quantita', 'totale', 'note')
        ## La commessa viene settata nel modello Fattura, non nella riga:
        ## 'commessa', 'commessa_codice',
        read_only_fields = ('id', 'totale', 'riga_ordine', 'riga_bolla')
    
    def get_articolo_codice(self, obj):
        return obj.articolo.codice

    def get_articolo_unita_di_misura_label(self, obj):
        return obj.get_articolo_unita_di_misura_display()

    def get_riga_ordine_codice(self, obj):
        if obj.riga_ordine:
            return obj.riga_ordine.ordine.codice
        else:
            return None

    def get_riga_bolla_codice(self, obj):
        if obj.riga_bolla:
            return obj.riga_bolla.bolla.codice
        else:
            return None


class FatturaFornitoreSerializer(serializers.ModelSerializer):
    fornitore_codice = serializers.SerializerMethodField()
    fornitore_label = serializers.SerializerMethodField()
    commessa_codice = serializers.SerializerMethodField()
    pagamento_label = serializers.SerializerMethodField()
    righe = RigaFatturaFornitoreSerializer(many=True, read_only=True)

    class Meta:
        model = FatturaFornitore
        fields = ('id', 'codice', 'codice_fattura_fornitore', 'data', \
            'data_fattura_fornitore', 'fornitore', 'fornitore_codice',  \
            'fornitore_label', 'commessa', 'commessa_codice', 'destinazione', \
            'persona_di_riferimento', \
            'oggetto', 'imponibile', 'sconto_euro', 'sconto_percentuale', \
            'imponibile_netto', 'aliquota_IVA',  'totale_iva', 'totale', \
            'pagamento', 'pagamento_label', 'banca_di_appoggio', 'righe', \
            'note')  # da_confermare
        read_only_fields = ('id', 'codice', 'imponibile', 
            'imponibile_netto', 'totale_iva', 'totale')    # da_confermare

    def get_fornitore_codice(self, obj):
        return obj.fornitore.codice

    def get_fornitore_label(self, obj):
        return obj.fornitore.get_nome_completo()

    def get_commessa_codice(self, obj):
        if obj.commessa:
            return obj.commessa.codice
        else:
            return None

    def get_pagamento_label(self, obj):
        return obj.pagamento.descrizione

    """
    Per validare la banca serve sapere anche il fornitore!
    def validate_banca_di_appoggio(self, value):
        if value and value.entita != Entita.objects.proprietario():
            raise serializers.ValidationError("La banca di appoggio selezionata non è valida.")
        return value
    """
    
    def validate_sconto_euro(self, value):
        if value < 0:
            raise serializers.ValidationError("Lo sconto in euro non può essere inferiore a 0.")
        return value
    
    def validate_sconto_percentuale(self, value):
        if (value < 0) or (value > 100):
            raise serializers.ValidationError("Lo sconto percentuale deve essere compreso tra 0 e 100.")
        return value

    def validate(self, data):
        sconto_euro = data.get('sconto_euro')
        sconto_percentuale = data.get('sconto_percentuale')
        if (sconto_euro > 0) and (sconto_percentuale > 0):
            raise serializers.ValidationError("Non è possibile applicare sia lo "
                + "sconto percentuale che lo sconto in euro.")       
        return data

