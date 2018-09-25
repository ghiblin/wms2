from rest_framework import status
from rest_framework.test import APITestCase  # , APIRequestFactory
from rest_framework.test import APIClient
# from rest_framework.exceptions import APIException

from django.core.urlresolvers import reverse
from datetime import timedelta
from anagrafiche.models import *
# import unittest

saltaQuestoTest = True


class FornitoriTestCase(APITestCase):
    """
    Testa che le API dei fornitori funzionino per gli utenti di tipo admin.
    """
    fixtures = ['wms_data']

    def test_get_commessa_magazzino(self):
        """
        Recupera la commessa 'MAGAZZINO'. Questo test non riguarda le api.
        """
        commessa = Commessa.objects.get_magazzino()
        proprietario = Entita.objects.proprietario()
        self.assertEqual(commessa.codice, 'MAGAZZINO')
        self.assertEqual(commessa.cliente, proprietario)
        self.assertEqual(commessa.prodotto, 'MAGAZZINO')

    def test_crea_preventivoFornitore(self):
        """
        Creazione preventivo fornitore (senza righe).
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        numero_preventivi_fornitori_prima = PreventivoFornitore.objects.count()
        # print ("numero preventivi fornitori esistenti: {}".format(numero_preventivi_fornitori_prima))
        fornitore = Entita.objects.fornitori().first()
        # commessa = Commessa.objects.filter(fornitore=fornitore).first()
        dati_preventivo = {
            'fornitore': str(fornitore.id),
            # 'commessa': str(commessa.id),
            'data': datetime.now().strftime('%Y-%m-%d')
        }
        response = client.post('/api/v1/preventivoFornitore/', dati_preventivo)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_preventivo = response.data['id']
        pf = PreventivoFornitore.objects.get(pk=id_preventivo)
        self.assertEqual(pf.totale, 0)
        self.assertIsNone(pf.destinazione)
        self.assertIsNone(pf.commessa)
        self.assertTrue(pf.totale_su_stampa)

        numero_preventivi_fornitori_dopo = PreventivoFornitore.objects.count()
        # print ("numero preventivi fornitori esistenti dopo: {}".format(numero_preventivi_fornitori_dopo))
        self.assertEqual(numero_preventivi_fornitori_prima+1, numero_preventivi_fornitori_dopo)

    def test_get_lista_preventivi_fornitori(self):
        """
        Chiama l'API per ottenere la lista dei preventivi fornitori.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        numero_preventivi_fornitori_prima = PreventivoFornitore.objects.count()
        # print ("numero preventivi fornitori esistenti: {}".format(numero_preventivi_fornitori_prima))
        response = client.get('/api/v1/preventivoFornitore/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # import pdb; pdb.set_trace()
        preventivi = response.data
        self.assertEqual(numero_preventivi_fornitori_prima, len(preventivi))

    def test_duplicaPreventivoFornitore(self):
        id_preventivo_origine = 1
        preventivo_origine = PreventivoFornitore.objects.get(pk=id_preventivo_origine)
        numero_preventivi_fornitore_prima = PreventivoFornitore.objects.count()
        client = APIClient()
        client.login(username='admin', password='nimda')
        indirizzo_chiamata = reverse('preventivofornitore-duplica', args=(id_preventivo_origine,))
        response = client.post(indirizzo_chiamata, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_preventivo_nuovo = response.data['id']
        self.assertNotEqual(id_preventivo_origine, id_preventivo_nuovo, "L'id del preventivo fornitore restituito "
                            + "deve essere diverso dall'id del preventivo da clonare.")
        preventivo_nuovo = PreventivoFornitore.objects.get(pk=id_preventivo_nuovo)

        numero_preventivi_fornitore_dopo = PreventivoFornitore.objects.count()
        self.assertEqual(numero_preventivi_fornitore_prima + 1, numero_preventivi_fornitore_dopo, "Creato 1 preventivo "
                         + "fornitore")

        self.assertEqual(preventivo_origine.righe.non_cancellati().count(), preventivo_nuovo.righe.count(), "Numero "
                         + "righe preventivo nuovo deve essere uguale al numero di righe del preventivo di origine "
                         + "(senza le righe cancellate).")
        
        self.assertEqual(preventivo_nuovo.righe.non_cancellati().count(), preventivo_nuovo.righe.count(), "Il "
                         + "preventivo nuovo non deve contenere righe cancellate, anche se c'erano nel preventivo "
                         + "d'origine.")

        self.assertFalse(preventivo_nuovo.accettato, "Il nuovo preventivo deve sempre avere accettato=False")

        for nome_campo in ['aliquota_IVA_id', 'fornitore_id', 'commessa_id', 'destinazione_id', 'note', 'oggetto',
                           'pagamento_id', 'persona_di_riferimento', 'totale', 'totale_su_stampa']:

            self.assertEqual(preventivo_origine.__getattribute__(nome_campo),
                             preventivo_nuovo.__getattribute__(nome_campo), "Il valore del campo '{}' non coincide "
                             + "nei due preventivi.".format(nome_campo))
        # codice preventivo 
        # self.assertEqual(preventivo_nuovo.data, today...)

    def test_get_lista_ordini_fornitori(self):
        """
        Chiama l'API per ottenere la lista degli ordini fornitori.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        numero_ordini_fornitori_prima = OrdineFornitore.objects.count()
        # print ("numero ordini fornitori esistenti: {}".format(numero_ordini_fornitori_prima))
        response = client.get('/api/v1/ordineFornitore/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ordini = response.data
        self.assertEqual(numero_ordini_fornitori_prima, len(ordini))

    def test_crea_ordineFornitore_da_preventivoFornitore(self):
        """
        Chiama le API per creare un preventivo fornitore con due righe, poi crea 
        l'ordine con drop down del preventivo. Usa la commessa 'magazzino' per 
        creare l'ordine.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        fornitore = Entita.objects.fornitori().first()
        dati_preventivo = {
            'fornitore': str(fornitore.id),
            'data': datetime.now().strftime('%Y-%m-%d')
        }
        response = client.post('/api/v1/preventivoFornitore/', dati_preventivo)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_preventivo = response.data['id']
        # pf = PreventivoFornitore.objects.get(pk=id_preventivo)

        articolo = Articolo.objects.first()
        riga1_prezzo = 10
        riga1_quantita = 20
        riga1_sconto_percentuale = 0
        dati_riga = {
            'preventivo': str(id_preventivo),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_prezzo': riga1_prezzo,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga1_sconto_percentuale,
            'quantita': riga1_quantita
        }

        response = client.post('/api/v1/rigaPreventivoFornitore/', dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga1 = response.data['id']
        totale_riga1_aspettato = riga1_prezzo * riga1_quantita * (100 - riga1_sconto_percentuale) / 100
        
        riga2_prezzo = 100
        riga2_quantita = 3
        riga2_sconto_percentuale = 10
        dati_riga = {
            'preventivo': str(id_preventivo),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo.id),
            'articolo_descrizione': articolo.descrizione,
            'articolo_prezzo': riga2_prezzo,
            'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga2_sconto_percentuale,
            'quantita': riga2_quantita
        }

        response = client.post('/api/v1/rigaPreventivoFornitore/', dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga2 = response.data['id']
        totale_riga2_aspettato = riga2_prezzo * riga2_quantita * (100 - riga2_sconto_percentuale) / 100
        
        pf = PreventivoFornitore.objects.get(pk=id_preventivo)
        self.assertEqual(pf.totale, totale_riga1_aspettato + totale_riga2_aspettato, 'Totale preventivo fornitore '
                         + 'aggiornato')
        self.assertFalse(pf.accettato, "Preventivo non deve risultare accettato.")

        ################################################################################################################
        #  Verifica delle API dell'ordine.
        ################################################################################################################
        # creo un ordine partendo dalle righe di un preventivo.
        commessa = Commessa.objects.get_magazzino()

        dati_righe_preventivi = {
            'riga_preventivo_fornitore[]': [id_riga1, id_riga2],
            'commessa': str(commessa.id)
        }
        response = client.post('/api/v1/ordineFornitore/crea_ordine_da_righe_preventivo/', dati_righe_preventivi)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Ordine fornitore creato.")
        
        pf = PreventivoFornitore.objects.get(pk=id_preventivo)
        self.assertTrue(pf.accettato, "Preventivo fornitore deve risultare accettato.")
        
        id_ordine = response.data['id']
        self.assertEqual(response.data['fornitore'], fornitore.id)
        of = OrdineFornitore.objects.get(pk=id_ordine)
        self.assertEqual(pf.righe.count(), of.righe.count(),
                         "Verifica che preventivo e ordine abbiano lo stesso numero di righe.")
        for riga_preventivo in pf.righe.all():
            riga_ordine = of.righe.get(riga_preventivo=riga_preventivo) 
            self.assertEqual(riga_ordine.quantita, riga_preventivo.quantita)
            self.assertEqual(riga_ordine.articolo, riga_preventivo.articolo)
            self.assertEqual(riga_ordine.articolo_descrizione, riga_preventivo.articolo_descrizione)
            self.assertEqual(riga_ordine.articolo_unita_di_misura, riga_preventivo.articolo_unita_di_misura)
            self.assertFalse(riga_ordine.bollettata)
            self.assertFalse(riga_ordine.fatturata)
        self.assertFalse(of.bollettato)
        self.assertFalse(of.fatturato)

    def test_creazione_bolla(self):
        """
        Creata una bolla fornitori con una riga, verifica che il movimento relativo sia creato in automatico.
        """
        n_movimenti_prima = Movimento.objects.non_cancellati().count()
        n_bollefornitori_prima = BollaFornitore.objects.non_cancellati().count()

        client = APIClient()
        client.login(username='admin', password='nimda')
        url_bolla_list = reverse('bollafornitore-list')
        # response = client.post(url_bolla_list)
        client.post(url_bolla_list)

        fornitore = Entita.objects.fornitori().first()
        causale_trasporto = TipoCausaleTrasporto.objects.first()
        commessa = Commessa.objects.get_magazzino()
        trasporto_a_cura = TipoTrasportoACura.objects.first()
        dati_bolla = {
            'data': datetime.now().strftime('%Y-%m-%d'),
            'fornitore': str(fornitore.id), 
            'causale_trasporto': str(causale_trasporto.id),
            'commessa': str(commessa.id),
            'trasporto_a_cura': str(trasporto_a_cura.id)
        }
        response = client.post(url_bolla_list, dati_bolla)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_bolla = response.data['id']
        bolla = BollaFornitore.objects.get(pk=id_bolla)
        self.assertEqual(bolla.fornitore, fornitore)
        self.assertEqual(bolla.causale_trasporto, causale_trasporto)
        self.assertEqual(bolla.commessa, commessa)
        self.assertEqual(bolla.trasporto_a_cura, trasporto_a_cura)

        n_bollefornitori_dopo = BollaFornitore.objects.non_cancellati().count()
        self.assertEqual(n_bollefornitori_prima+1, n_bollefornitori_dopo)

        url_rigabolla_list = reverse('rigabollafornitore-list')
        articolo1 = Articolo.objects.non_cancellati()[0]
        scorta_articolo1 = articolo1.scorta
        quantita_carico1 = 300

        dati_riga = {
            'articolo': str(articolo1.id),
            'quantita': quantita_carico1,
            'bolla': str(id_bolla),
            'articolo_descrizione': articolo1.descrizione
        }
        response = client.post(url_rigabolla_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga1 = response.data['id']
        riga1 = RigaBollaFornitore.objects.get(pk=id_riga1)

        self.assertEqual(riga1.quantita, quantita_carico1)
        self.assertEqual(riga1.articolo, articolo1)
        self.assertEqual(riga1.articolo_descrizione, articolo1.descrizione)

        bolla = BollaFornitore.objects.get(pk=id_bolla)
        self.assertTrue(len(bolla.righe.all()), 1)

        # avendo creato una riga, un movimento dovrebbe essere creato in automatico
        n_movimenti_dopo = Movimento.objects.non_cancellati().count()
        self.assertEqual(n_movimenti_prima+1, n_movimenti_dopo)

        # I movimenti relativi al lotto/bolla utilizzata devono essere solo 1
        movimenti_lotto = Movimento.objects.filter(lotto=bolla)
        self.assertEqual(len(movimenti_lotto), 1)
        movimento_lotto = movimenti_lotto[0]
        self.assertEqual(movimento_lotto.articolo, articolo1)
        self.assertEqual(movimento_lotto.quantita, quantita_carico1)

        # la scorta dell'articolo deve essere aumentata della quantità della riga bolla
        articolo1 = Articolo.objects.non_cancellati()[0]
        self.assertEqual(articolo1.scorta, scorta_articolo1 + quantita_carico1)

        # import pdb; pdb.set_trace()
        # deve esistere una giacenza relativa al lotto (bolla) e all'articolo.
        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=articolo1)
        self.assertEqual(giacenza1.quantita, quantita_carico1)

    def test_crea_bollaFornitore_da_ordineFornitore(self):
        """
        Chiama le API per creare un ordine fornitore con due righe, poi crea 
        la bolla con drop down dell'ordine. Usa la commessa 'magazzino' per 
        creare l'ordine.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        fornitore = Entita.objects.fornitori().first()
        commessa = Commessa.objects.get_magazzino()
        dati_ordine = {
            'fornitore': str(fornitore.id),
            'data': datetime.now().strftime('%Y-%m-%d'),
            'commessa': str(commessa.id)
        }
        url_ordine_list = reverse('ordinefornitore-list')
        response = client.post(url_ordine_list, dati_ordine)
        ################################################################################################################
        #  Verifica delle API dell'ordine.
        ################################################################################################################
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_ordine = response.data['id']
        # of = OrdineFornitore.objects.get(pk=id_ordine)

        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        articolo1_scorta_prima = articolo1.scorta

        riga1_prezzo = 10
        riga1_quantita = 20
        riga1_sconto_percentuale = 0
        dati_riga = {
            'ordine': str(id_ordine),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo1.id),
            'articolo_descrizione': articolo1.descrizione,
            'articolo_prezzo': riga1_prezzo,
            # 'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga1_sconto_percentuale,
            'quantita': riga1_quantita
        }
        
        url_rigaordine_list = reverse('rigaordinefornitore-list')
        response = client.post(url_rigaordine_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga1 = response.data['id']
        totale_riga1_aspettato = riga1_prezzo * riga1_quantita * (100 - riga1_sconto_percentuale) / 100
        
        articolo2 = articoli[1]
        articolo2_scorta_prima = articolo2.scorta
        
        riga2_prezzo = 100
        riga2_quantita = 3
        riga2_sconto_percentuale = 10
        dati_riga = {
            'ordine': str(id_ordine),
            # 'commessa': str(commessa.id),   la commessa non va passata perché viene dedotta dall'ordine
            'articolo': str(articolo2.id),
            'articolo_descrizione': articolo2.descrizione,
            'articolo_prezzo': riga2_prezzo,
            # 'articolo_unita_di_misura': UNITA_MISURA_PEZZI,
            'sconto_percentuale': riga2_sconto_percentuale,
            'quantita': riga2_quantita
        }
        
        response = client.post(url_rigaordine_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga2 = response.data['id']
        totale_riga2_aspettato = riga2_prezzo * riga2_quantita * (100 - riga2_sconto_percentuale) / 100
        
        of = OrdineFornitore.objects.get(pk=id_ordine)
        self.assertEqual(of.totale, totale_riga1_aspettato + totale_riga2_aspettato,
                         'Totale ordine fornitore aggiornato')
        self.assertFalse(of.bollettato, "Ordine non deve risultare bollettato.")
        self.assertFalse(of.fatturato, "Ordine non deve risultare fatturato.")

        ################################################################################################################
        #  Verifica delle API della bolla.
        ################################################################################################################
        # creo una bolla partendo dalle righe di un ordine.

        dati_righe_ordine = {
            'riga_ordine_fornitore[]': [id_riga1, id_riga2],
            # 'commessa': str(commessa.id)
        }
        indirizzo_chiamata = reverse('bollafornitore-crea-bolla-da-righe-ordine')
        response = client.post(indirizzo_chiamata, dati_righe_ordine)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Bolla fornitore creata.")
        
        of = OrdineFornitore.objects.get(pk=id_ordine)
        self.assertTrue(of.bollettato, "Ordine fornitore deve risultare bollettato.")
        self.assertFalse(of.fatturato, "Ordine fornitore non deve risultare fatturato.")
        
        id_bolla = response.data['id']
        self.assertEqual(response.data['fornitore'], fornitore.id)
        bolla = BollaFornitore.objects.get(pk=id_bolla)
        self.assertEqual(of.righe.count(), bolla.righe.count(),
                         "Verifica che ordine e bolla abbiano lo stesso numero di righe.")
        for riga_ordine in of.righe.all():
            riga_bolla = bolla.righe.get(riga_ordine=riga_ordine) 
            self.assertEqual(riga_bolla.quantita, riga_ordine.quantita)
            self.assertEqual(riga_bolla.articolo, riga_ordine.articolo)
            self.assertEqual(riga_bolla.articolo_descrizione, riga_ordine.articolo_descrizione)
            self.assertEqual(riga_bolla.articolo_unita_di_misura, riga_ordine.articolo_unita_di_misura)
            self.assertFalse(riga_bolla.fatturata)
            self.assertIsNotNone(riga_bolla.carico)
        self.assertFalse(bolla.fatturata)

        # verifica movimenti di carico
        carico = TipoMovimento.objects.get_carico()
        carico1 = Movimento.objects.get(lotto=bolla, articolo=articolo1, quantita=riga1_quantita)
        self.assertEqual(carico1.destinazione, commessa)
        self.assertEqual(carico1.tipo_movimento, carico)
        carico2 = Movimento.objects.get(lotto=bolla, articolo=articolo2, quantita=riga2_quantita)
        self.assertEqual(carico2.destinazione, commessa)
        self.assertEqual(carico2.tipo_movimento, carico)

        # verifica giacenze
        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=articolo1)
        self.assertEqual(giacenza1.quantita, riga1_quantita)
        giacenza2 = Giacenza.objects.get(lotto=bolla, articolo=articolo2)
        self.assertEqual(giacenza2.quantita, riga2_quantita)

        # verifica scorte
        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        articolo1_scorta_dopo = articolo1.scorta
        self.assertEqual(articolo1_scorta_prima + riga1_quantita, articolo1_scorta_dopo)
        articolo2 = articoli[1]
        articolo2_scorta_dopo = articolo2.scorta
        self.assertEqual(articolo2_scorta_prima + riga2_quantita, articolo2_scorta_dopo)

    def test_aggiungi_righe_ordine_a_bolla_fornitori(self):
        """
        Chiama le API per fare il dropdown delle righe di un ordine e aggiungerle 
        ad una bolla fornitore.
        I movimenti, le giacenze e le scorte sono create/aggiornate di conseguenza.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        ordine = OrdineFornitore.objects.get(pk=1)
        righe_ordine = ordine.righe.all()
        riga_ordine1 = righe_ordine[0]
        riga_ordine2 = righe_ordine[1]

        articolo1_scorta_prima = riga_ordine1.articolo.scorta
        articolo2_scorta_prima = riga_ordine2.articolo.scorta
        magazzino = Commessa.objects.get_magazzino()

        bolla = BollaFornitore()
        bolla.fornitore = ordine.fornitore
        bolla.oggetto = ordine.oggetto
        bolla.commessa = ordine.commessa
        bolla.causale_trasporto = TipoCausaleTrasporto.objects.first()
        bolla.trasporto_a_cura = TipoTrasportoACura.objects.first()
        bolla.data = datetime.now()
        bolla.save()
        dati_righe_ordine = {
            'riga_ordine_fornitore[]': [riga_ordine1.id, riga_ordine2.id],
        }
        indirizzo_chiamata = reverse('bollafornitore-crea-righe-da-ordine', args=(bolla.id,))
        response = client.post(indirizzo_chiamata, dati_righe_ordine)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Righe bolla create.")
        
        # verifica movimenti di carico
        carico = TipoMovimento.objects.get_carico()
        carico1 = Movimento.objects.get(lotto=bolla, articolo=riga_ordine1.articolo, quantita=riga_ordine1.quantita)
        self.assertEqual(carico1.destinazione, magazzino)
        self.assertEqual(carico1.tipo_movimento, carico)
        carico2 = Movimento.objects.get(lotto=bolla, articolo=riga_ordine2.articolo, quantita=riga_ordine2.quantita)
        self.assertEqual(carico2.destinazione, magazzino)
        self.assertEqual(carico2.tipo_movimento, carico)

        # verifica giacenze
        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=riga_ordine1.articolo)
        self.assertEqual(giacenza1.quantita, riga_ordine1.quantita)
        giacenza2 = Giacenza.objects.get(lotto=bolla, articolo=riga_ordine2.articolo)
        self.assertEqual(giacenza2.quantita, riga_ordine2.quantita)

        # verifica scorte
        articolo1 = Articolo.objects.get(pk=riga_ordine1.articolo.id)
        articolo1_scorta_dopo = articolo1.scorta
        self.assertEqual(articolo1_scorta_prima + riga_ordine1.quantita, articolo1_scorta_dopo)
        articolo2 = Articolo.objects.get(pk=riga_ordine2.articolo.id)
        articolo2_scorta_dopo = articolo2.scorta
        self.assertEqual(articolo2_scorta_prima + riga_ordine2.quantita, articolo2_scorta_dopo)

    def test_modifica_bolla_fornitore(self):
        """
        Crea una bolla con due righe. Fai uno scarico dell'articolo della prima riga. 
        Modificare la prima riga della bolla aumentando la quantità. Verificare la giacenza e la scorta
        dell'articolo.
        Modificare la prima riga della bolla diminuendo la quantità. Verificare che l'operazione non 
        vada a buon fine.
        Cancellare la prima riga della bolla e verificare che l'operazione non vada a buon fine.
        Cancellare la seconda riga della bolla e verificare che l'operazione vada a buon fine.
        Cancellare lo scarico e poi la prima riga della bolla.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_bolla_list = reverse('bollafornitore-list')
        # response = client.post(url_bolla_list)
        client.post(url_bolla_list)

        fornitore = Entita.objects.fornitori().first()
        causale_trasporto = TipoCausaleTrasporto.objects.first()
        commessa = Commessa.objects.get_magazzino()
        trasporto_a_cura = TipoTrasportoACura.objects.first()
        dati_bolla = {
            'data': datetime.now().strftime('%Y-%m-%d'),
            'data_bolla_fornitore': (datetime.now() + timedelta(days=-2)).strftime('%Y-%m-%d'),
            'fornitore': str(fornitore.id), 
            'causale_trasporto': str(causale_trasporto.id),
            'commessa': str(commessa.id),
            'trasporto_a_cura': str(trasporto_a_cura.id)
        }
        response = client.post(url_bolla_list, dati_bolla)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_bolla = response.data['id']
        bolla = BollaFornitore.objects.get(pk=id_bolla)
        self.assertIsNotNone(bolla.data_bolla_fornitore,
                             'Data bolla fornitore è null anche se era stato passato un valore durante la creazione.')

        url_rigabolla_list = reverse('rigabollafornitore-list')
        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        articolo1_scorta_iniziale = articolo1.scorta
        quantita_carico1 = 300

        articolo2 = articoli[1]
        quantita_carico2 = 500
        
        dati_riga = {
            'articolo': str(articolo1.id),
            'quantita': quantita_carico1,
            'bolla': str(id_bolla),
            'articolo_descrizione': articolo1.descrizione
        }
        response = client.post(url_rigabolla_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga1 = response.data['id']
        # riga1 = RigaBollaFornitore.objects.get(pk=id_riga1)

        dati_riga = {
            'articolo': str(articolo2.id),
            'quantita': quantita_carico2,
            'bolla': str(id_bolla),
            'articolo_descrizione': articolo2.descrizione
        }
        response = client.post(url_rigabolla_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_riga2 = response.data['id']

        bolla = BollaFornitore.objects.get(pk=id_bolla)
        self.assertTrue(len(bolla.righe.all()), 2)

        # deve esistere una giacenza relativa al lotto (bolla) e all'articolo.
        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=articolo1)
        self.assertEqual(giacenza1.quantita, quantita_carico1)
        giacenza2 = Giacenza.objects.get(lotto=bolla, articolo=articolo2)
        self.assertEqual(giacenza2.quantita, quantita_carico2)
        destinazione = Commessa.objects.filter(id__gt=0).first()

        scarico = TipoMovimento.objects.get_scarico()
        quantita_scarico1 = 200
        dati_movimento = {
            'articolo': str(articolo1.id),
            'lotto': str(bolla.id), 
            'destinazione': str(destinazione.id),
            'quantita': quantita_scarico1,
            'tipo_movimento': str(scarico.id),
        }
        
        url_movimento_list = reverse('movimento-list')
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_movimento_scarico = response.data['id']

        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=articolo1)
        self.assertEqual(giacenza1.quantita, 100)

        ################################################################################################################
        # Modifico la prima riga della bolla. La giacenza deve aumentare di conseguenza.
        ################################################################################################################
        url_riga_bolla_details = reverse('rigabollafornitore-detail', args=(id_riga1, ))
        dati_riga1 = {
            'articolo': str(articolo1.id),
            'quantita': quantita_carico1 + 500,
            'bolla': str(id_bolla),
            'articolo_descrizione': articolo1.descrizione
        }
        response = client.put(url_riga_bolla_details, dati_riga1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=articolo1)
        # import pdb; pdb.set_trace()
        self.assertEqual(giacenza1.quantita, quantita_carico1 + 500 - quantita_scarico1)

        riga1 = RigaBollaFornitore.objects.get(pk=id_riga1)
        self.assertEqual(quantita_carico1 + 500, riga1.carico.quantita)

        ################################################################################################################
        # Modifico di nuovo la prima riga della bolla settando una quantità inferiore allo scarico già avvenuto. La
        # modifica deve fallire.
        ################################################################################################################
        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        scorta_articolo1_prima = articolo1.scorta
        # articolo2 = articoli[1]
        # scorta_articolo2_prima = articolo2.scorta

        dati_riga1 = {
            'articolo': str(articolo1.id),
            'quantita': 50,
            'bolla': str(id_bolla),
            'articolo_descrizione': articolo1.descrizione
        }
        response = client.put(url_riga_bolla_details, dati_riga1)
        self.assertEqual(response.status_code, WmsValidationError.status_code)
        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=articolo1)
        # import pdb; pdb.set_trace()
        self.assertEqual(giacenza1.quantita, quantita_carico1 + 500 - quantita_scarico1)

        riga1 = RigaBollaFornitore.objects.get(pk=id_riga1)
        # il movimento non deve essere cambiato
        self.assertEqual(quantita_carico1 + 500, riga1.carico.quantita)

        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        scorta_articolo1_dopo = articolo1.scorta
        articolo2 = articoli[1]
        # scorta_articolo2_dopo = articolo2.scorta
        self.assertEqual(scorta_articolo1_prima, scorta_articolo1_dopo, "Visto che la modifica alla bolla è fallita, "
                         + "la scorta dell'articolo non deve essere cambiata.")
        # self.assertEqual(scorta_articolo2_prima, scorta_articolo2_dopo)
        
        ################################################################################################################
        # Cancello la prima riga della bolla. Visto che è stato fatto uno scarico la cancellazione deve fallire.
        ################################################################################################################
        response = client.delete(url_riga_bolla_details)
        self.assertEqual(response.status_code, WmsValidationError.status_code)
        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=articolo1)
        # import pdb; pdb.set_trace()
        self.assertEqual(giacenza1.quantita, quantita_carico1 + 500 - quantita_scarico1)

        riga1 = RigaBollaFornitore.objects.get(pk=id_riga1)
        # il movimento non deve essere cambiato
        self.assertEqual(quantita_carico1 + 500, riga1.carico.quantita)

        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        scorta_articolo1_dopo = articolo1.scorta
        self.assertEqual(scorta_articolo1_prima, scorta_articolo1_dopo,
                         "Visto che la cancellazione della riga è fallita, la scorta dell'articolo non deve essere "
                         + "cambiata.")

        ################################################################################################################
        # Cancello la seconda riga della bolla. Deve andare bene.
        ################################################################################################################

        riga2 = RigaBollaFornitore.objects.get(pk=id_riga2)
        carico2 = riga2.carico
        self.assertFalse(carico2.cancellato)
        self.assertTrue(Giacenza.objects.filter(lotto=bolla, articolo=articolo2).exists())
        articolo2 = Articolo.objects.get(pk=riga2.articolo.id)
        articolo2_scorta_prima = articolo2.scorta

        url_riga_bolla_details = reverse('rigabollafornitore-detail', args=(id_riga2, ))
        response = client.delete(url_riga_bolla_details)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        riga2 = RigaBollaFornitore.objects.get(pk=id_riga2)
        carico2 = riga2.carico
        self.assertTrue(carico2.cancellato, "Il movimento di carico deve essere cancellato.")

        self.assertFalse(Giacenza.objects.filter(lotto=bolla, articolo=articolo2).exists(),
                         "La giacenza non deve più esistere dopo la cancellazione della riga bolla.")

        articolo2 = Articolo.objects.get(pk=riga2.articolo.id)
        articolo2_scorta_dopo = articolo2.scorta
        self.assertEqual(articolo2_scorta_prima - quantita_carico2, articolo2_scorta_dopo,
                         "La scorta dell'articolo non si è aggiornata come avrebbe dovuto.")

        ################################################################################################################
        # Cancello lo scarico dell'articolo della prima riga e poi cancello la prima riga della bolla.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_scarico,))
        response = client.delete(url_movimento_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        riga1 = RigaBollaFornitore.objects.get(pk=id_riga1)
        carico1 = riga1.carico
        self.assertFalse(carico1.cancellato)
        self.assertTrue(Giacenza.objects.filter(lotto=bolla, articolo=articolo1).exists())
        articolo1 = Articolo.objects.get(pk=riga1.articolo.id)
        
        url_riga_bolla_details = reverse('rigabollafornitore-detail', args=(id_riga1, ))
        response = client.delete(url_riga_bolla_details)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        riga1 = RigaBollaFornitore.objects.get(pk=id_riga1)
        carico1 = riga1.carico
        self.assertTrue(carico1.cancellato, "Il movimento di carico deve essere cancellato.")

        self.assertFalse(Giacenza.objects.filter(lotto=bolla, articolo=articolo1).exists(),
                         "La giacenza non deve più esistere dopo la cancellazione della prima riga bolla.")

        articolo1 = Articolo.objects.get(pk=riga1.articolo.id)
        articolo1_scorta_dopo = articolo1.scorta
        self.assertEqual(articolo1_scorta_dopo, articolo1_scorta_iniziale,
                         "La scorta dell'articolo 1 deve tornare ad essere uguale alla scorta all'inizio dei test.")

    def test_cancellazione_bolla_fornitore(self):
        """
        Crea una bolla con due righe. 
        Fai uno scarico dell'articolo della seconda riga. 
        Cancella la bolla; dovrebbe fallire
        Cancellare lo scarico.
        Cancellare la bolla; questa volta dovrebbe finire bene.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_bolla_list = reverse('bollafornitore-list')
        # response = client.post(url_bolla_list)
        client.post(url_bolla_list)

        fornitore = Entita.objects.fornitori().first()
        causale_trasporto = TipoCausaleTrasporto.objects.first()
        commessa = Commessa.objects.get_magazzino()
        trasporto_a_cura = TipoTrasportoACura.objects.first()
        dati_bolla = {
            'data': datetime.now().strftime('%Y-%m-%d'),
            'fornitore': str(fornitore.id), 
            'causale_trasporto': str(causale_trasporto.id),
            'commessa': str(commessa.id),
            'trasporto_a_cura': str(trasporto_a_cura.id)
        }
        response = client.post(url_bolla_list, dati_bolla)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_bolla = response.data['id']
        # bolla = BollaFornitore.objects.get(pk=id_bolla)

        url_rigabolla_list = reverse('rigabollafornitore-list')
        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        articolo1_scorta_iniziale = articolo1.scorta
        quantita_carico1 = 300

        articolo2 = articoli[1]
        articolo2_scorta_iniziale = articolo2.scorta
        quantita_carico2 = 500
        
        dati_riga = {
            'articolo': str(articolo1.id),
            'quantita': quantita_carico1,
            'bolla': str(id_bolla),
            'articolo_descrizione': articolo1.descrizione
        }
        response = client.post(url_rigabolla_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # id_riga1 = response.data['id']
        # riga1 = RigaBollaFornitore.objects.get(pk=id_riga1)

        dati_riga = {
            'articolo': str(articolo2.id),
            'quantita': quantita_carico2,
            'bolla': str(id_bolla),
            'articolo_descrizione': articolo2.descrizione
        }
        response = client.post(url_rigabolla_list, dati_riga)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # id_riga2 = response.data['id']

        bolla = BollaFornitore.objects.get(pk=id_bolla)
        self.assertTrue(len(bolla.righe.all()), 2)

        # devono esistere le giacenze dei due articoli e la loro scorta deve essere aumentata
        giacenza1 = Giacenza.objects.get(lotto=bolla, articolo=articolo1)
        self.assertEqual(giacenza1.quantita, quantita_carico1)
        giacenza2 = Giacenza.objects.get(lotto=bolla, articolo=articolo2)
        self.assertEqual(giacenza2.quantita, quantita_carico2)

        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        articolo1_scorta_dopo_carico = articolo1.scorta

        articolo2 = articoli[1]
        articolo2_scorta_dopo_carico = articolo2.scorta

        self.assertEqual(articolo1_scorta_iniziale + quantita_carico1, articolo1_scorta_dopo_carico,
                         "Scorta articolo 1 non aggiornata come mi aspettavo")
        self.assertEqual(articolo2_scorta_iniziale + quantita_carico2, articolo2_scorta_dopo_carico,
                         "Scorta articolo 2 non aggiornata come mi aspettavo")

        # creo scarico del secondo articolo
        destinazione = Commessa.objects.filter(id__gt=0).first()
        scarico = TipoMovimento.objects.get_scarico()
        quantita_scarico = 100
        dati_movimento = {
            'articolo': str(articolo2.id),
            'lotto': str(bolla.id), 
            'destinazione': str(destinazione.id),
            'quantita': quantita_scarico,
            'tipo_movimento': str(scarico.id),
        }
        
        url_movimento_list = reverse('movimento-list')
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id_movimento_scarico = response.data['id']

        giacenza2 = Giacenza.objects.get(lotto=bolla, articolo=articolo2)
        self.assertEqual(giacenza2.quantita, quantita_carico2 - quantita_scarico)

        ################################################################################################################
        #  Cancello la bolla; deve fallire.
        ################################################################################################################

        url_bolla_details = reverse('bollafornitore-detail', args=(id_bolla, ))
        response = client.delete(url_bolla_details)
        self.assertEqual(response.status_code, WmsValidationError.status_code)

        ################################################################################################################
        # Cancello lo scarico, deve andare bene.
        ################################################################################################################

        url_scarico_details = reverse('movimento-detail', args=(id_movimento_scarico, ))
        response = client.delete(url_scarico_details)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # ripeto i test fatti dopo la creazione delle righe, le quantità dovrebbero essere ancora quelle
        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        articolo1_scorta_dopo_carico = articolo1.scorta

        articolo2 = articoli[1]
        articolo2_scorta_dopo_carico = articolo2.scorta

        self.assertEqual(articolo1_scorta_iniziale + quantita_carico1, articolo1_scorta_dopo_carico,
                         "Scorta articolo 1 non aggiornata come mi aspettavo.")
        self.assertEqual(articolo2_scorta_iniziale + quantita_carico2, articolo2_scorta_dopo_carico,
                         "Scorta articolo 2 non aggiornata come mi aspettavo.")

        ################################################################################################################
        # Cancello la bolla; deve andare bene.
        ################################################################################################################

        url_bolla_details = reverse('bollafornitore-detail', args=(id_bolla,))
        response = client.delete(url_bolla_details)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # le giacenze non devono più esistere:
        self.assertFalse(Giacenza.objects.filter(lotto=bolla, articolo=articolo1).exists())
        self.assertFalse(Giacenza.objects.filter(lotto=bolla, articolo=articolo2).exists())

        # le scorte devono essere uguali a quelle iniziali
        articoli = Articolo.objects.non_cancellati()
        articolo1 = articoli[0]
        articolo1_scorta_dopo_cancellazione = articolo1.scorta

        articolo2 = articoli[1]
        articolo2_scorta_dopo_cancellazione = articolo2.scorta

        self.assertEqual(articolo1_scorta_iniziale, articolo1_scorta_dopo_cancellazione,
                         "Scorta articolo 1 non aggiornata come mi aspettavo.")
        self.assertEqual(articolo2_scorta_iniziale, articolo2_scorta_dopo_cancellazione,
                         "Scorta articolo 2 non aggiornata come mi aspettavo.")
