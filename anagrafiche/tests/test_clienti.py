from rest_framework import status
from rest_framework.test import APITestCase  # , APIRequestFactory
from rest_framework.test import APIClient

from django.core.urlresolvers import reverse
from anagrafiche.models import *

saltaQuestoTest = True

"""
class ProvaTestCase(APITestCase):
    " ""
    Prima classe creata per eseguire i test automatici. si potrebbe anche cancellare...
    " ""

    fixtures = ['wms_data']

    @unittest.skipIf(saltaQuestoTest, 'codice copiato da internet, non va.')
    def test_get_list(self):
        import pdb; pdb.set_trace()
        factory = APIRequestFactory()
        request = factory.get('/api/v1/tipoPagamento/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
"""


class ClientiTestCase(APITestCase):
    """
    Testa che le API dei clienti funzionino per gli utenti di tipo admin.
    """
    fixtures = ['wms_data']

    def test_crea_cliente_pf(self):
        client = APIClient()
        client.login(username='admin', password='nimda')
        nome = 'Paperon'
        cognome = 'De Paperoni'
        dati_cliente = {
            'nome': nome,
            'cognome': cognome,
            'tipo': PERSONA_FISICA,
            'codice_fiscale': 'DPPPRN60A01H501T',
            'partita_iva': ''
        }
        url_cliente_list = reverse('cliente-list')
        response = client.post(url_cliente_list, dati_cliente)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_cliente = response.data['id']
        is_supplier = response.data['is_supplier']
        self.assertTrue('vettore' in response.data)
        self.assertFalse(is_supplier)
        cliente = Entita.objects.get(pk=id_cliente, is_client=True)
        self.assertEqual(cliente.nome, nome)
        self.assertEqual(cliente.cognome, cognome)

        ################################################################################################################
        # Ripeto il test specificando una partita iva non valida.
        ################################################################################################################
        dati_cliente['partita_iva'] = '123456'
        response = client.post(url_cliente_list, dati_cliente)
        # print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        ################################################################################################################
        # Ripeto il test specificando una partita iva valida
        ################################################################################################################
        dati_cliente['partita_iva'] = '00726320153'
        response = client.post(url_cliente_list, dati_cliente)
        # print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_cliente = response.data['id']
        cliente = Entita.objects.get(pk=id_cliente, is_client=True)
        self.assertEqual(cliente.nome, nome)
        self.assertEqual(cliente.cognome, cognome)

        ################################################################################################################
        # Faccio diventare questo cliente anche un fornitore
        ################################################################################################################
        url_converti_a_fornitore = reverse('cliente-anche-fornitore', args=(id_cliente,))
        response = client.put(url_converti_a_fornitore)
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Entita.objects.filter(pk=id_cliente, is_client=True, is_supplier=True).exists())

    def test_crea_fornitore_pf(self):
        client = APIClient()
        client.login(username='admin', password='nimda')
        nome = 'Paperon'
        cognome = 'De Paperoni'
        dati_fornitore = {
            'nome': nome,
            'cognome': cognome,
            'tipo': PERSONA_FISICA,
            'codice_fiscale': 'DPPPRN60A01H501T',
            'partita_iva': ''
        }
        url_fornitore_list = reverse('fornitore-list')
        response = client.post(url_fornitore_list, dati_fornitore)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        is_client = response.data['is_client']
        self.assertFalse(is_client)
        id_fornitore = response.data['id']
        fornitore = Entita.objects.get(pk=id_fornitore, is_supplier=True)
        self.assertEqual(fornitore.nome, nome)
        self.assertEqual(fornitore.cognome, cognome)

        ################################################################################################################
        # Ripeto il test specificando una partita iva non valida.
        ################################################################################################################
        dati_fornitore['partita_iva'] = '123456'
        response = client.post(url_fornitore_list, dati_fornitore)
        # print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        ################################################################################################################
        # Ripeto il test specificando una partita iva valida
        ################################################################################################################
        dati_fornitore['partita_iva'] = '00726320153'
        response = client.post(url_fornitore_list, dati_fornitore)
        # print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_fornitore = response.data['id']
        fornitore = Entita.objects.get(pk=id_fornitore, is_supplier=True)
        self.assertEqual(fornitore.nome, nome)
        self.assertEqual(fornitore.cognome, cognome)

        ################################################################################################################
        # Faccio diventare questo fornitore anche un cliente
        ################################################################################################################
        url_converti_a_cliente = reverse('fornitore-anche-cliente', args=(id_fornitore,))
        response = client.put(url_converti_a_cliente)
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Entita.objects.filter(pk=id_fornitore, is_client=True, is_supplier=True).exists())

    def test_get_ordineCliente(self):
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_ordine_cliente_list = reverse('ordinecliente-list')
        response = client.get(url_ordine_cliente_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_duplicaPreventivoCliente(self):
        id_preventivo_origine = 33
        preventivo_origine = PreventivoCliente.objects.get(pk=id_preventivo_origine)
        numero_preventivi_cliente_prima = PreventivoCliente.objects.count()
        client = APIClient()
        client.login(username='admin', password='nimda')
        indirizzo_chiamata = reverse('preventivocliente-duplica', args=(id_preventivo_origine,))
        response = client.post(indirizzo_chiamata, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_preventivo_nuovo = response.data['id']
        self.assertNotEqual(id_preventivo_origine, id_preventivo_nuovo, "L'id del preventivo restituito deve essere "
                            + "diverso dall'id del preventivo da clonare.")
        preventivo_nuovo = PreventivoCliente.objects.get(pk=id_preventivo_nuovo)

        numero_preventivi_cliente_dopo = PreventivoCliente.objects.count()
        self.assertEqual(numero_preventivi_cliente_prima + 1, numero_preventivi_cliente_dopo, "Creato un preventivo "
                         + "cliente")

        self.assertEqual(preventivo_origine.righe.count(), preventivo_nuovo.righe.count(), "Numero righe preventivo "
                         + "nuovo deve essere uguale al numero di righe del preventivo di origine.")

        self.assertFalse(preventivo_nuovo.accettato, "Il nuovo preventivo deve sempre avere accettato=False")

        for nome_campo in ['aliquota_IVA_id', 'classe_di_esecuzione', 'cliente_id', 'commessa_id', 'destinazione_id',
                           'disegni_costruttivi', 'note', 'oggetto', 'pagamento_id', 'persona_di_riferimento',
                           'relazione_di_calcolo', 'spessori', 'tipo_di_acciaio', 'totale', 'totale_su_stampa',
                           'verniciatura', 'wps', 'zincatura']:

            self.assertEqual(preventivo_origine.__getattribute__(nome_campo),
                             preventivo_nuovo.__getattribute__(nome_campo), "Il valore del campo '{}' non coincide "
                             + "nei due preventivi.".format(nome_campo))
        # codice preventivo 
        # self.assertEqual(preventivo_nuovo.data, today...)

    def test_crea_ordineCliente(self):
        client = APIClient()
        client.login(username='admin', password='nimda')
        numero_ordini_cliente_prima = OrdineCliente.objects.count()
        # print ("numero ordini esistenti: {}".format(numero_ordini_cliente_prima))
        cliente = Entita.objects.get(ragione_sociale='Marlegno S.r.l.')
        commessa = Commessa.objects.filter(cliente=cliente).first()
        dati_ordine = {
            'cliente': str(cliente.id),
            'commessa': str(commessa.id),
            'data': datetime.now().strftime('%Y-%m-%d')
        }
        url_ordine_cliente_list = reverse('ordinecliente-list')
        response = client.post(url_ordine_cliente_list, dati_ordine)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_ordine = response.data['id']
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertEqual(ordine.totale, 0)
        self.assertEqual(ordine.sconto_euro, 0)
        self.assertEqual(ordine.sconto_percentuale, 0)
        self.assertFalse(ordine.bollettato)
        self.assertFalse(ordine.fatturato)
        self.assertIsNone(ordine.destinazione)

        numero_ordini_cliente_dopo = OrdineCliente.objects.count()
        # print ("numero ordini esistenti dopo: {}".format(numero_ordini_cliente_dopo))
        self.assertEqual(numero_ordini_cliente_prima+1, numero_ordini_cliente_dopo)

        # import pdb; pdb.set_trace()
        articolo = Articolo.objects.first()
        riga1_prezzo = 10
        riga1_quantita = 20
        riga1_sconto_percentuale = 0
        dati_riga = {
            'ordine': str(id_ordine),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_prezzo': riga1_prezzo,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga1_sconto_percentuale,
            'quantita': riga1_quantita
        }

        url_riga_ordine_cliente_list = reverse('rigaordinecliente-list')
        response = client.post(url_riga_ordine_cliente_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # id_riga1 = response.data['id']
        totale_riga1_aspettato = riga1_prezzo * riga1_quantita * (100 - riga1_sconto_percentuale) / 100
        self.assertEqual(response.data['totale'], totale_riga1_aspettato)
        self.assertIsNone(response.data['preventivo'])
        self.assertIsNone(response.data['riga_preventivo'])
        self.assertIsNone(response.data['riga_bolla'])
        self.assertIsNone(response.data['preventivo_codice'])
        self.assertFalse(response.data['fatturata'])
        self.assertFalse(response.data['bollettata'])
        self.assertEqual(response.data['quantita'], riga1_quantita)
        self.assertEqual(response.data['articolo_prezzo'], riga1_prezzo)
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertEqual(ordine.totale, totale_riga1_aspettato, 'Totale ordine aggiornato')

        riga2_prezzo = 100
        riga2_quantita = 3
        riga2_sconto_percentuale = 10
        dati_riga = {
            'ordine': str(id_ordine),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_prezzo': riga2_prezzo,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga2_sconto_percentuale,
            'quantita': riga2_quantita
        }

        response = client.post(url_riga_ordine_cliente_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # id_riga2 = response.data['id']
        totale_riga2_aspettato = riga2_prezzo * riga2_quantita * (100 - riga2_sconto_percentuale) / 100
        self.assertEqual(response.data['totale'], totale_riga2_aspettato)
        self.assertIsNone(response.data['preventivo'])
        self.assertIsNone(response.data['riga_preventivo'])
        self.assertIsNone(response.data['riga_bolla'])
        self.assertIsNone(response.data['preventivo_codice'])
        self.assertFalse(response.data['fatturata'])
        self.assertFalse(response.data['bollettata'])
        self.assertEqual(response.data['quantita'], riga2_quantita)
        self.assertEqual(response.data['articolo_prezzo'], riga2_prezzo)

        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertEqual(ordine.totale, totale_riga1_aspettato + totale_riga2_aspettato, 'Totale ordine aggiornato')

    def test_crea_ordineCliente_con_sconto_non_valido(self):
        """
        Primo test: sconto percentuale maggiore di 0 e sconto_euro > 0. La creazione
        dell'ordine deve fallire.
        Secondo test: sconto percentuale maggiore di 100.
        Terzo test: sconto_euro minore di 0.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        numero_ordini_cliente_prima = OrdineCliente.objects.count()
        # print ("numero ordini esistenti: {}".format(numero_ordini_cliente_prima))
        cliente = Entita.objects.get(ragione_sociale='Marlegno S.r.l.')
        commessa = Commessa.objects.filter(cliente=cliente).first()
        dati_ordine = {
            'cliente': str(cliente.id),
            'commessa': str(commessa.id),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'sconto_euro': '111', 
            'sconto_percentuale': '5'
        }
        url_ordine_cliente_list = reverse('ordinecliente-list')
        response = client.post(url_ordine_cliente_list, dati_ordine)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        numero_ordini_cliente_dopo = OrdineCliente.objects.count()
        # print ("numero ordini esistenti dopo: {}".format(numero_ordini_cliente_dopo))
        self.assertEqual(numero_ordini_cliente_prima, numero_ordini_cliente_dopo)

        # sconto percentuale maggiore di 100
        dati_ordine = {
            'cliente': str(cliente.id),
            'commessa': str(commessa.id),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'sconto_euro': '0', 
            'sconto_percentuale': '150'
        }
        response = client.post(url_ordine_cliente_list, dati_ordine)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        numero_ordini_cliente_dopo = OrdineCliente.objects.count()
        # print ("numero ordini esistenti dopo: {}".format(numero_ordini_cliente_dopo))
        self.assertEqual(numero_ordini_cliente_prima, numero_ordini_cliente_dopo)

        # sconto euro minore di 0
        dati_ordine = {
            'cliente': str(cliente.id),
            'commessa': str(commessa.id),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'sconto_euro': '-100', 
            'sconto_percentuale': '0'
        }
        response = client.post(url_ordine_cliente_list, dati_ordine)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        numero_ordini_cliente_dopo = OrdineCliente.objects.count()
        # print ("numero ordini esistenti dopo: {}".format(numero_ordini_cliente_dopo))
        self.assertEqual(numero_ordini_cliente_prima, numero_ordini_cliente_dopo)

    def test_crea_fatturaCliente_da_ordineCliente(self):
        """
        Crea un ordine con due righe, poi crea la fattura. L'operazione
        dovrebbe fallire perché prima bisogna impostare l'iva nell'ordine.
        Assegna l'iva al 10% all'ordine e poi crea la fattura.
        Poi crea la bolla dall'ordine che deve risultare già fatturata subito
        dopo la creazione.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        cliente = Entita.objects.get(ragione_sociale='Marlegno S.r.l.')
        id_cliente = cliente.id
        commessa = Commessa.objects.filter(cliente=cliente).first()
        persona_di_riferimento = 'Paperon de Paperoni'
        riferimento_cliente = "Ordine 12345"
        dati_ordine = {
            'cliente': str(cliente.id),
            'commessa': str(commessa.id),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'persona_di_riferimento': persona_di_riferimento,
            'riferimento_cliente': riferimento_cliente
        }
        url_ordine_cliente_list = reverse('ordinecliente-list')
        response = client.post(url_ordine_cliente_list, dati_ordine)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_ordine = response.data['id']
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertEqual(ordine.cliente_id, id_cliente)
        self.assertEqual(ordine.persona_di_riferimento, persona_di_riferimento, 'Verifico che il campo "Persona di '
                         + ' riferimento" sia valorizzato con il campo passato alla chiamata.')
        self.assertEqual(ordine.riferimento_cliente, riferimento_cliente, 'Verifico che il campo "Riferimento cliente"'
                         + ' sia valorizzato con il campo passato alla chiamata.')
        
        # import pdb; pdb.set_trace()
        articolo = Articolo.objects.first()
        riga1_prezzo = 10
        riga1_quantita = 20
        riga1_sconto_percentuale = 0
        dati_riga = {
            'ordine': str(id_ordine),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_prezzo': riga1_prezzo,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga1_sconto_percentuale,
            'quantita': riga1_quantita
        }

        url_riga_ordine_cliente_list = reverse('rigaordinecliente-list')
        response = client.post(url_riga_ordine_cliente_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga1 = response.data['id']
        totale_riga1_aspettato = riga1_prezzo * riga1_quantita * (100 - riga1_sconto_percentuale) / 100
        
        riga2_prezzo = 100
        riga2_quantita = 3
        riga2_sconto_percentuale = 10
        dati_riga = {
            'ordine': str(id_ordine),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_prezzo': riga2_prezzo,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga2_sconto_percentuale,
            'quantita': riga2_quantita
        }

        response = client.post(url_riga_ordine_cliente_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga2 = response.data['id']
        totale_riga2_aspettato = riga2_prezzo * riga2_quantita * (100 - riga2_sconto_percentuale) / 100
        
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertEqual(ordine.totale, totale_riga1_aspettato + totale_riga2_aspettato, 'Totale ordine aggiornato')

        ################################################################################################################
        # Verifica delle API delle fatture
        ################################################################################################################
        dati_righe_ordini = {
            'riga_ordine_cliente[]': [id_riga1, id_riga2]
        }
        
        # la creazione della fattura deve fallire perché l'ordine
        # non ha l'iva
        url_crea_fattura_da_righe_ordine = reverse("fatturacliente-crea-fattura-da-righe-ordine")
        response = client.post(url_crea_fattura_da_righe_ordine, dati_righe_ordini)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Fattura non creata perché manca l'iva "
                         + "all'ordine.")
        aliquota_iva = AliquotaIVA.objects.get(percentuale=10)
        ordine.aliquota_IVA = aliquota_iva
        ordine.save()
        ordine.aggiorna_totale()
                
        response = client.post(url_crea_fattura_da_righe_ordine, dati_righe_ordini)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Fattura creata.")
        id_fattura = response.data['id']
        fattura = FatturaCliente.objects.get(pk=id_fattura)
        totale_fattura_aspettato = (totale_riga1_aspettato + totale_riga2_aspettato) * ((100 + 10) / 100)
        self.assertEqual(fattura.totale, totale_fattura_aspettato, 'Totale fattura uguale a totale ordine (con iva).')
        self.assertEqual(fattura.cliente_id, id_cliente)
        self.assertEqual(fattura.persona_di_riferimento, persona_di_riferimento, 'Fattura deve ereditare la persona '
                         + 'di riferimento dall\'ordine')
        self.assertEqual(fattura.riferimento_cliente, riferimento_cliente, 'Fattura deve ereditare il riferimento '
                         + 'cliente dall\'ordine')
        
        righe_ordine = ordine.righe.all()
        for riga in righe_ordine:
            self.assertTrue(riga.fatturata, "Riga ordine risulta fatturata.")
        # va refreshato dopo la creazione della fattura:
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertTrue(ordine.fatturato, "Ordine risulta fatturato.")
        self.assertFalse(ordine.bollettato, "Ordine non deve risultare bollettato.")

        ################################################################################################################
        # Verifica delle API delle bolle
        ################################################################################################################
        # creo una bolla partendo dalle righe di un ordine già fatturato!
        # Devo verificare che la righe della bolla risultino già fatturate
        # import pdb; pdb.set_trace()
        url_crea_bolla_da_righe_ordine = reverse('bollacliente-crea-bolla-da-righe-ordine')
        response = client.post(url_crea_bolla_da_righe_ordine, dati_righe_ordini)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Bolla creata.")
        
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertTrue(ordine.fatturato, "Ordine risulta fatturato.")
        self.assertTrue(ordine.bollettato, "Ordine deve risultare bollettato.")

        id_bolla = response.data['id']
        self.assertEqual(response.data['cliente'], id_cliente)
        bolla = BollaCliente.objects.get(pk=id_bolla)
        self.assertEqual(bolla.righe.count(), ordine.righe.count(), "Verifica che la bolla erediti tutte le righe "
                         + "dell'ordine.")
        self.assertEqual(bolla.persona_di_riferimento, ordine.persona_di_riferimento, "Verifica che la bolla erediti "
                         + "la persona di riferimento dall'ordine.")
        self.assertEqual(bolla.riferimento_cliente, ordine.riferimento_cliente, "Verifica che la bolla erediti "
                         + "il 'riferimento cliente' dall'ordine.")
        for riga_ordine in ordine.righe.all():
            riga_bolla = bolla.righe.get(riga_ordine=riga_ordine) 
            self.assertEqual(riga_bolla.quantita, riga_ordine.quantita)
            self.assertEqual(riga_bolla.articolo, riga_ordine.articolo)
            self.assertEqual(riga_bolla.articolo_descrizione, riga_ordine.articolo_descrizione)
            self.assertEqual(riga_bolla.articolo_unita_di_misura, riga_ordine.articolo_unita_di_misura)
            self.assertTrue(riga_bolla.fatturata)
            self.assertEqual(riga_ordine.riga_fattura, riga_bolla.riga_fattura)
        self.assertTrue(bolla.fatturata)

    def test_crea_bollaCliente_da_ordineCliente(self):
        """
        Crea un ordine con due righe, poi crea la bolla dall'ordine. 
        A differenza del test precedente, la bolla appena creata non deve
        risultare fatturata.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        cliente = Entita.objects.get(ragione_sociale='Marlegno S.r.l.')
        id_cliente = cliente.id
        commessa = Commessa.objects.filter(cliente=cliente).first()
        dati_ordine = {
            'cliente': str(cliente.id),
            'commessa': str(commessa.id),
            'data': datetime.now().strftime('%Y-%m-%d')
        }
        url_ordine_cliente_list = reverse('ordinecliente-list')
        response = client.post(url_ordine_cliente_list, dati_ordine)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_ordine = response.data['id']
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertEqual(ordine.cliente_id, id_cliente)
        
        articolo = Articolo.objects.first()
        riga1_prezzo = 10
        riga1_quantita = 20
        riga1_sconto_percentuale = 0
        dati_riga = {
            'ordine': str(id_ordine),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_prezzo': riga1_prezzo,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga1_sconto_percentuale,
            'quantita': riga1_quantita
        }

        url_riga_ordine_cliente_list = reverse('rigaordinecliente-list')
        response = client.post(url_riga_ordine_cliente_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga1 = response.data['id']
        totale_riga1_aspettato = riga1_prezzo * riga1_quantita * (100 - riga1_sconto_percentuale) / 100
        
        riga2_prezzo = 100
        riga2_quantita = 3
        riga2_sconto_percentuale = 10
        dati_riga = {
            'ordine': str(id_ordine),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_prezzo': riga2_prezzo,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga2_sconto_percentuale,
            'quantita': riga2_quantita
        }

        response = client.post(url_riga_ordine_cliente_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga2 = response.data['id']
        totale_riga2_aspettato = riga2_prezzo * riga2_quantita * (100 - riga2_sconto_percentuale) / 100
        
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertEqual(ordine.totale, totale_riga1_aspettato + totale_riga2_aspettato, 'Totale ordine aggiornato')

        ################################################################################################################
        # Verifica delle API delle bolle
        ################################################################################################################
        # creo una bolla partendo dalle righe di un ordine NON fatturato!
        dati_righe_ordini = {
            'riga_ordine_cliente[]': [id_riga1, id_riga2]
        }
        url_crea_bolla_da_righe_ordine = reverse('bollacliente-crea-bolla-da-righe-ordine')
        response = client.post(url_crea_bolla_da_righe_ordine, dati_righe_ordini)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Bolla creata.")
        
        ordine = OrdineCliente.objects.get(pk=id_ordine)
        self.assertFalse(ordine.fatturato, "Ordine non deve risultare fatturato.")
        self.assertTrue(ordine.bollettato, "Ordine deve risultare bollettato.")

        id_bolla = response.data['id']
        self.assertEqual(response.data['cliente'], id_cliente)
        bolla = BollaCliente.objects.get(pk=id_bolla)
        self.assertEqual(bolla.righe.count(), ordine.righe.count(), "Verifica che la bolla erediti tutte le righe "
                         + "dell'ordine.")
        for riga_ordine in ordine.righe.all():
            riga_bolla = bolla.righe.get(riga_ordine=riga_ordine) 
            self.assertEqual(riga_bolla.quantita, riga_ordine.quantita)
            self.assertEqual(riga_bolla.articolo, riga_ordine.articolo)
            self.assertEqual(riga_bolla.articolo_descrizione, riga_ordine.articolo_descrizione)
            self.assertEqual(riga_bolla.articolo_unita_di_misura, riga_ordine.articolo_unita_di_misura)
            self.assertFalse(riga_bolla.fatturata)
        self.assertFalse(bolla.fatturata)

    def test_crea_fatturaCliente_da_bollaCliente(self):
        """
        Crea una bolla con due righe, poi crea la fattura dalla bolla.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        cliente = Entita.objects.get(ragione_sociale='Marlegno S.r.l.')
        id_cliente = cliente.id
        commessa = Commessa.objects.filter(cliente=cliente).first()
        trasporto_a_cura = TipoTrasportoACura.objects.first()
        causale_trasporto = TipoCausaleTrasporto.objects.first()
        persona_di_riferimento = 'Paperon de Paperoni'
        riferimento_cliente = 'Ordine 12345'
        dati_bolla = {
            'cliente': str(cliente.id),
            'commessa': str(commessa.id),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'trasporto_a_cura': str(trasporto_a_cura.id),
            'causale_trasporto': str(causale_trasporto.id),
            'persona_di_riferimento': persona_di_riferimento,
            'riferimento_cliente': riferimento_cliente
        }
        url_bolla_cliente_list = reverse('bollacliente-list')
        response = client.post(url_bolla_cliente_list, dati_bolla)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_bolla = response.data['id']
        bolla = BollaCliente.objects.get(pk=id_bolla)
        self.assertEqual(bolla.cliente_id, id_cliente)
        self.assertEqual(bolla.persona_di_riferimento, persona_di_riferimento)
        
        articolo = Articolo.objects.first()
        riga1_quantita = 20
        dati_riga = {
            'bolla': str(id_bolla),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dalla bolla
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'quantita': riga1_quantita
        }
        url_riga_bolla_cliente_list = reverse('rigabollacliente-list')
        response = client.post(url_riga_bolla_cliente_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga1 = response.data['id']
        # nelle bolle i prezzi non ci sono
        
        riga2_quantita = 3
        dati_riga = {
            'bolla': str(id_bolla),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dalla bolla
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'quantita': riga2_quantita
        }
        response = client.post(url_riga_bolla_cliente_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga2 = response.data['id']

        ################################################################################################################
        # Verifica delle API delle fatture
        ################################################################################################################
        # creo una fattura partendo dalle righe di una bolla NON fatturata!
        dati_righe_bolle = {
            'riga_bolla_cliente[]': [id_riga1, id_riga2]
        }
        url_crea_fattura_cliente_da_righe_bolla = reverse('fatturacliente-crea-fattura-da-righe-bolla')
        response = client.post(url_crea_fattura_cliente_da_righe_bolla, dati_righe_bolle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Fattura creata.")
        
        bolla = BollaCliente.objects.get(pk=id_bolla)
        self.assertTrue(bolla.fatturata, "Bolla deve risultare fatturata.")

        id_fattura = response.data['id']
        self.assertEqual(response.data['cliente'], id_cliente)
        fattura = FatturaCliente.objects.get(pk=id_fattura)
        self.assertEqual(fattura.righe.count(), bolla.righe.count(), "Verifica che la fattura erediti tutte le righe "
                         + "della bolla.")
        for riga_bolla in bolla.righe.all():
            riga_fattura = fattura.righe.get(riga_bolla=riga_bolla) 
            self.assertEqual(riga_fattura.quantita, riga_bolla.quantita)
            self.assertEqual(riga_fattura.articolo, riga_bolla.articolo)
            self.assertEqual(riga_fattura.articolo_descrizione, riga_bolla.articolo_descrizione)
            self.assertEqual(riga_fattura.articolo_unita_di_misura, riga_bolla.articolo_unita_di_misura)

        self.assertEqual(fattura.totale, 0, 'Totale fattura uguale a 0 perché la bolla è stata creata da 0, senza '
                         + 'ordine.')
        self.assertTrue(fattura.da_confermare, 'La fattura è da confermare perché i prezzi degli articoli non sono '
                        + 'ricavabili dalla bolla.')
        self.assertEqual(fattura.aliquota_IVA, AliquotaIVA.objects.get_aliquota_default(), 'La fattura ha l\'aliquota'
                         + ' IVA di default perché la fattura è da confermare')
        self.assertEqual(fattura.pagamento, cliente.pagamento, 'Il pagamento nella fattura deve essere uguale al '
                         + 'pagamento di default del cliente della bolla (ma solo perché la bolla è stata creata '
                         + 'senza ordine).')
        self.assertEqual(fattura.sconto_euro, 0, 'Lo sconto in euro deve essere uguale a 0 perché la fattura è da '
                         + 'confermare.')
        self.assertEqual(fattura.sconto_percentuale, 0, 'Lo sconto percentuale deve essere uguale a 0 perché la '
                         + 'fattura è da confermare.')
        self.assertEqual(fattura.persona_di_riferimento, bolla.persona_di_riferimento, 'La persona di riferimento '
                         + 'della fattura deve essere uguale alla persona di riferimento della bolla.')
        self.assertEqual(fattura.riferimento_cliente, bolla.riferimento_cliente, 'Il riferimento cliente della '
                         + 'fattura deve essere uguale al riferimento cliente nella bolla.')

    # #### Bisognerebbe testare la creazione di una fattura partendo da una bolla
    # #### generata a sua volta da un ordine e controllare che i prezzi della
    # #### fattura sono quelli estratti dall'ordine.

    def test_dissocia_bolle_da_fattura(self):
        """
        Crea una fattura da una bolla; dissocia la bolla dalla fattura e poi usa la stessa bolla per creare
        un'altra fattura.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')

        # Verifica che il metodo 'dissocia' funzioni anche su fatture NON create da bolle.
        fattura = FatturaCliente.objects.last()
        id_fattura = int(fattura.id)
        url_dissocia = reverse('fatturacliente-dissocia-bolle', args=(id_fattura,))
        response = client.post(url_dissocia, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verifica che dissociando di nuovo la fattura non ci siano problemi:
        response = client.post(url_dissocia, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ################################################################################################################
        # Creazione fattura da bolla:
        ################################################################################################################

        bb = BollaCliente.objects.filter(fatturata=False).first()
        id_righe_bolla = bb.righe.all().values_list('id', flat=True)
        dati_righe_bolle = {
            'riga_bolla_cliente[]': id_righe_bolla
        }
        url_dropdown = reverse('fatturacliente-crea-fattura-da-righe-bolla')
        response = client.post(url_dropdown, dati_righe_bolle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Fattura creata.")
        id_fattura = response.data['id']
        fattura = FatturaCliente.objects.get(pk=id_fattura)

        bolla = BollaCliente.objects.get(pk=bb.id)
        self.assertTrue(bolla.fatturata, "Bolla deve risultare fatturata.")
        for riga_bolla in bolla.righe.non_cancellati():
            self.assertTrue(riga_bolla.fatturata, "La riga bolla deve risultare fatturata.")
            self.assertEqual(riga_bolla.riga_fattura.fattura, fattura)

        ################################################################################################################
        # Dissociazione della fattura dalla bolla
        ################################################################################################################

        url_dissocia = reverse('fatturacliente-dissocia-bolle', args=(id_fattura,))
        response = client.post(url_dissocia, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bolla = BollaCliente.objects.get(pk=bb.id)
        self.assertFalse(bolla.fatturata, "Bolla deve risultare NON fatturata.")
        for riga_bolla in bolla.righe.non_cancellati():
            self.assertFalse(riga_bolla.fatturata, "La riga bolla deve risultare NON fatturata.")
            # Nel caso di relazione OneToOne si può usare None nei check solo da fattura verso bolla e non viceversa.
            self.assertFalse(hasattr(riga_bolla, 'riga_fattura'))

    def test_dissocia_bolle_e_ordini_da_fattura(self):
        """
        E' come il test precedente, ma in questo caso la bolla è creata tramite drop da un ordine.
        Creo una bolla partendo da un ordine, poi creo la fattura usando la bolla.
        Poi dissocia la bolla e l'ordine dalla fattura e poi usa la stessa bolla per creare
        un'altra fattura.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')

        ################################################################################################################
        # Creazione bolla da ordine
        ################################################################################################################
        ordine = OrdineCliente.objects.filter(bollettato=False, fatturato=False).first()
        id_righe_ordine = ordine.righe.all().values_list('id', flat=True)
        dati_righe_ordine = {
            'riga_ordine_cliente[]': id_righe_ordine
        }
        url_dropdown = reverse('bollacliente-crea-bolla-da-righe-ordine')
        response = client.post(url_dropdown, dati_righe_ordine)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Bolla creata.")
        id_bolla = response.data['id']
        bolla = BollaCliente.objects.get(pk=id_bolla)

        ################################################################################################################
        # Creazione fattura da bolla:
        ################################################################################################################

        id_righe_bolla = bolla.righe.all().values_list('id', flat=True)
        dati_righe_bolle = {
            'riga_bolla_cliente[]': id_righe_bolla
        }
        url_dropdown = reverse('fatturacliente-crea-fattura-da-righe-bolla')
        response = client.post(url_dropdown, dati_righe_bolle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Fattura creata.")
        id_fattura = response.data['id']
        fattura = FatturaCliente.objects.get(pk=id_fattura)

        bolla = BollaCliente.objects.get(pk=bolla.id)
        self.assertTrue(bolla.fatturata, "Bolla deve risultare fatturata.")
        for riga_bolla in bolla.righe.non_cancellati():
            self.assertTrue(riga_bolla.fatturata, "La riga bolla deve risultare fatturata.")
            self.assertEqual(riga_bolla.riga_fattura.fattura, fattura)
        ordine = OrdineCliente.objects.get(pk=ordine.id)
        self.assertTrue(ordine.fatturato, "Ordine deve risultare fatturato.")
        for riga_ordine in ordine.righe.non_cancellati():
            self.assertTrue(riga_ordine.fatturata, "La riga ordine deve risultare fatturato.")
            self.assertEqual(riga_ordine.riga_fattura.fattura, fattura)

        ################################################################################################################
        # Dissociazione della fattura dalla bolla
        ################################################################################################################

        url_dissocia = reverse('fatturacliente-dissocia-bolle', args=(id_fattura,))
        response = client.post(url_dissocia, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bolla = BollaCliente.objects.get(pk=bolla.id)
        self.assertFalse(bolla.fatturata, "Bolla deve risultare NON fatturata.")
        for riga_bolla in bolla.righe.non_cancellati():
            self.assertFalse(riga_bolla.fatturata, "La riga bolla deve risultare NON fatturata.")
            # Nel caso di relazione OneToOne si può usare None nei check solo da fattura verso bolla e non viceversa.
            self.assertFalse(hasattr(riga_bolla, 'riga_fattura'))

        ordine = OrdineCliente.objects.get(pk=ordine.id)
        self.assertFalse(ordine.fatturato, "Ordine deve risultare NON fatturato.")
        for riga_ordine in ordine.righe.non_cancellati():
            self.assertFalse(riga_ordine.fatturata, "La riga ordine deve risultare NON fatturato.")
            # Nel caso di relazione OneToOne si può usare None nei check solo da fattura verso ordine e non viceversa.
            self.assertFalse(hasattr(riga_ordine, 'riga_fattura'))

        ################################################################################################################
        # Ora posso creare un'altra fattura usando gli stessi dati della bolla associata e poi dissociata.
        ################################################################################################################

        response = client.post(url_dropdown, dati_righe_bolle)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Fattura creata.")
        id_fattura_2 = response.data['id']
        fattura_2 = FatturaCliente.objects.get(pk=id_fattura_2)

        bolla = BollaCliente.objects.get(pk=bolla.id)
        self.assertTrue(bolla.fatturata, "Bolla deve risultare fatturata.")
        for riga_bolla in bolla.righe.non_cancellati():
            self.assertTrue(riga_bolla.fatturata, "La riga bolla deve risultare fatturata.")
            self.assertEqual(riga_bolla.riga_fattura.fattura, fattura_2)
        ordine = OrdineCliente.objects.get(pk=ordine.id)
        self.assertTrue(ordine.fatturato, "Ordine deve risultare fatturato.")
        for riga_ordine in ordine.righe.non_cancellati():
            self.assertTrue(riga_ordine.fatturata, "La riga ordine deve risultare fatturato.")
            self.assertEqual(riga_ordine.riga_fattura.fattura, fattura_2)

    def test_creazione_fattura_con_e_senza_commessa(self):
        """
        Crea una fattura senza commessa e poi una fattura clienti con commessa.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')

        url_creazione_fattura = reverse('fatturacliente-list')
        cliente = Entita.objects.clienti().first()
        oggi = datetime.today().strftime('%Y-%m-%d')
        aliquota_iva = AliquotaIVA.objects.first()
        dati_fattura = {
            'cliente': str(cliente.id),
            'data': oggi,
            # 'commessa': commessa,
            'aliquota_IVA': str(aliquota_iva.id)
        }
        response = client.post(url_creazione_fattura, dati_fattura)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # ##############################################################################################################
        # Crea una fattura CON commessa:
        # ##############################################################################################################
        commessa = Commessa.objects.filter(cliente=cliente).first()
        dati_fattura = {
            'cliente': str(cliente.id),
            'data': oggi,
            'commessa': str(commessa.id),
            'aliquota_IVA': str(aliquota_iva.id)
        }
        response = client.post(url_creazione_fattura, dati_fattura)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_fattura = response.data['id']
        fattura = FatturaCliente.objects.get(pk=id_fattura)
        self.assertEqual(fattura.commessa, commessa)
        self.assertFalse(fattura.persona_di_riferimento)

        # ##############################################################################################################
        # Modifico la fattura senza passare il campo 'commessa'.
        # ##############################################################################################################
        url_modifica_fattura = reverse('fatturacliente-detail', args=(id_fattura,))
        dati_fattura = {
            'cliente': str(cliente.id),
            'data': oggi,
            'persona_di_riferimento': 'Topolino'
        }
        response = client.put(url_modifica_fattura, dati_fattura)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fattura = FatturaCliente.objects.get(pk=id_fattura)
        # Solitamente se non si passa un campo durante l'update di un modello, questo campo rimane invariato. Quindi in
        # questo caso la commessa non dovrebbe essere resettata. La UI attualmente funziona proprio in questo modo: se
        # non si seleziona una commessa, il campo non viene passato uguale a null, ma non viene proprio passato al
        # server.
        # Quindi per forzare la cancellazione della commessa ho modificato la perform_create del modello FatturaCliente.
        self.assertIsNone(fattura.commessa)

        # ##############################################################################################################
        # Modifico la fattura passando il campo 'commessa' uguale a "".
        # Questo sarebbe la chiamata corretta che la UI dovrebbe mandare al server...
        # ##############################################################################################################
        dati_fattura = {
            'cliente': str(cliente.id),
            'data': oggi,
            'persona_di_riferimento': 'Topolino2',
            'commessa': ""
        }
        response = client.put(url_modifica_fattura, dati_fattura)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fattura = FatturaCliente.objects.get(pk=id_fattura)
        self.assertIsNone(fattura.commessa)
