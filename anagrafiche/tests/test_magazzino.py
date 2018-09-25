from rest_framework import status
from rest_framework.test import APITestCase  # , APIRequestFactory
from rest_framework.test import APIClient
# from rest_framework.exceptions import APIException

from anagrafiche.models import *
from django.core.urlresolvers import reverse

saltaQuestoTest = True


class MagazzinoTestCase(APITestCase):
    """
    Test riguardanti gli articoli ed il magazzino.
    """

    fixtures = ['wms_data']

    def test_lista_articoli(self):
        """
        Verifica che le API degli articoli rispondano correttamente.
        """
        client = APIClient()
        response = client.get(reverse('articolo-list'))
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        client.login(username='admin', password='nimda')
        response = client.get(reverse('articolo-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_articoli_da_api = len(response.data)
        numero_articoli_da_db = Articolo.objects.all().count()
        self.assertNotEqual(numero_articoli_da_api, numero_articoli_da_db,
                            "Il numero degli articoli ottenuto dalle API è uguale al numero degli articoli nel db (ma"
                            + " nel db ci sono anche articoli cancellati).")
        numero_articoli_non_cancellati_da_db = Articolo.objects.non_cancellati().count()
        self.assertEqual(numero_articoli_da_api, numero_articoli_non_cancellati_da_db,
                         "Il numero degli articoli ottenuto dalle API è diverso dal numero di articoli estratti dal "
                         + "database.")

    def test_giacenze(self):
        """
        Verifica che le API delle giacenze restituiscano correttamente i record messi 
        nelle fixtures.
        """
        client = APIClient()
        response = client.get(reverse('giacenza-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # import pdb; pdb.set_trace()

        client.login(username='admin', password='nimda')
        url_giacenze = reverse('giacenza-list')
        response = client.get(url_giacenze)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_giacenze_da_api = len(response.data)
        numero_giacenze_da_db = Giacenza.objects.all().count()

        self.assertEqual(numero_giacenze_da_api, numero_giacenze_da_db,
                         "Il numero delle giacenze ottenute dalle API è diverso dal numero di giacenze estratte dal "
                         + "database.")

        response = client.get("{}?lotto=1".format(url_giacenze))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_giacenze_da_api = len(response.data)
        numero_giacenze_da_db = Giacenza.objects.filter(lotto=1).count()
        self.assertEqual(numero_giacenze_da_api, numero_giacenze_da_db,
                         "Il numero delle giacenze filtrate per lotto dalle API è diverso dal numero di giacenze "
                         + "estratte dal database.")

        response = client.get("{}?lotto__codice=BF15002".format(url_giacenze))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_giacenze_da_api = len(response.data)
        numero_giacenze_da_db = Giacenza.objects.filter(lotto__codice='BF15002').count()
        self.assertEqual(numero_giacenze_da_api, numero_giacenze_da_db,
                         "Il numero delle giacenze filtrate per codice lotto dalle API è diverso dal numero di "
                         + "giacenze estratte dal database.")

        response = client.get("{}?articolo=1".format(url_giacenze))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_giacenze_da_api = len(response.data)
        numero_giacenze_da_db = Giacenza.objects.filter(articolo=1).count()
        self.assertEqual(numero_giacenze_da_api, numero_giacenze_da_db,
                         "Il numero delle giacenze filtrate per articolo dalle API è diverso dal numero di giacenze "
                         + "estratte dal database.")

        response = client.get("{}?lotto__commessa=0".format(url_giacenze))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_giacenze_da_api = len(response.data)
        numero_giacenze_da_db = Giacenza.objects.filter(lotto__commessa=0).count()
        self.assertEqual(numero_giacenze_da_api, numero_giacenze_da_db,
                         "Il numero delle giacenze filtrate per id commessa dalle API è diverso dal numero di giacenze"
                         + " estratte dal database.")

        response = client.get("{}?lotto__commessa__codice=MAGAZZINO".format(url_giacenze))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_giacenze_da_api = len(response.data)
        numero_giacenze_da_db = Giacenza.objects.filter(lotto__commessa__codice="MAGAZZINO").count()
        self.assertEqual(numero_giacenze_da_api, numero_giacenze_da_db,
                         "Il numero delle giacenze filtrate per codice commessa dalle API è diverso dal numero di "
                         + "giacenze estratte dal database.")

        client.login(username='ut', password='ut')
        response = client.get(url_giacenze)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         'Utente UT non riesce ad accedere alle API delle giacenze.')

    def test_creazione_movimento_magazzino(self):
        """
        Verifica che l'API per la creazione, la modifica e il recupero dei 
        dettagli di un movimento funzionino.
        """
        client = APIClient()
        
        url_movimento_list = reverse('movimento-list')
        response = client.post(url_movimento_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         "API creazione movimento non dovrebbe essere accessibile a tutti.")

        client.login(username='admin', password='nimda')
        response = client.post(url_movimento_list)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         "API creazione movimento deve fallire se non riceve parametri.")

        lotto = BollaFornitore.objects.first()
        articolo = Articolo.objects.first()
        quantita_negativa = -123
        quantita_positiva = quantita_negativa * -1
        scarico = TipoMovimento.objects.get_scarico()
        autore = User.objects.get(username='admin')
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita_negativa, 
            'tipo_movimento': str(scarico.id),
        }
        
        # import pdb; pdb.set_trace()
        response = client.post(url_movimento_list, dati_movimento)
        errore_aspettato = "La quantità deve sempre essere positiva"
        self.assertContains(response, errore_aspettato, status_code=status.HTTP_400_BAD_REQUEST)
        
        dati_movimento['quantita'] = quantita_positiva
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         'Movimento magazzino non creato quando invece me l\'aspettavo.')
        id_movimento = response.data['id']

        movimento_creato = Movimento.objects.get(id=id_movimento)

        self.assertEqual(movimento_creato.autore, autore,
                         "Nel database l\'autore del movimento non è l\'utente che ha creato il movimento.")

        self.assertEqual(movimento_creato.unita_di_misura, articolo.get_unita_di_misura_display(),
                         "Nel database l\'unità di misura dell\'articolo del movimento non è la stessa unità di "
                         "misura dell\'articolo.")

        self.assertEqual(movimento_creato.quantita, quantita_negativa,
                         "Nel database la quantità non è negativa (come dovrebbe essere) anche se il tipo movimento"
                         " è 'scarico'.")

        url_movimento_detail = reverse('movimento-detail', args=(id_movimento, ))
        response = client.get(url_movimento_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "Errore durante il recupero dei dati di un movimento magazzino.")
        self.assertEqual(response.data['quantita'], quantita_negativa,
                         "La quantità restituita dalle API è diversa dalla quantità usata per creare il movimento.")
        self.assertEqual(response.data['abs_quantita'], quantita_positiva,
                         "abs_quantita contiene il valore assoluto della quantità di un movimento.")

        ################################################################################################################
        # Ripeto il test facendo un carico al posto di uno scarico.
        ################################################################################################################
        carico = TipoMovimento.objects.get(descrizione='Carico')
        dati_movimento['tipo_movimento'] = str(carico.id)
        # la quantità è già settata a 123
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'Movimento magazzino non creato.')
        id_movimento = response.data['id']

        movimento_creato = Movimento.objects.get(id=id_movimento)
        self.assertEqual(movimento_creato.quantita, quantita_positiva,
                         "Nel database la quantità dovrebbe essere positiva.")

        url_movimento_detail = reverse('movimento-detail', args=(id_movimento, ))
        response = client.get(url_movimento_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "Errore durante il recupero dei dati di un movimento magazzino.")
        self.assertEqual(response.data['quantita'], quantita_positiva,
                         "La quantità restituita dalle API è diversa dalla quantità usata per creare il movimento.")
        self.assertEqual(response.data['abs_quantita'], response.data['quantita'],
                         "Visto che l'operazione è un carico, quantita e abs_quantita dovrebbero coincidere.")

        ################################################################################################################
        # Ora modifico il movimento creato mettendo 'scarico' come tipo movimento.
        ################################################################################################################
        dati_movimento['tipo_movimento'] = str(scarico.id)
        # prima del movimento che sto per modificare la giacenza era 0.05. Se il carico lo faccio diventare
        # uno scarico, non posso scaricare più di 0.05 se non voglio avere un errore.
        dati_movimento['quantita'] = 0.04
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "Errore durante l'aggiornamento di un movimento magazzino.")

        movimento_aggiornato = Movimento.objects.get(id=id_movimento)
        self.assertEqual(movimento_aggiornato.tipo_movimento, scarico,
                         "Nel database il tipo movimento ora dovrebbe essere 'scarico'.")
        self.assertTrue(movimento_aggiornato.quantita < 0,
                        "Nel database la quantità dovrebbe essere negativa perché ora il tipo movimento è uno scarico.")

    def test_verifiche_movimenti(self):
        """
        Verifiche aggiuntive sui dati dei movimenti.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        lotto = BollaFornitore.objects.first()
        articolo = Articolo.objects.get(pk=6)
        quantita = 10
        carico = TipoMovimento.objects.get(descrizione='Carico')
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        # import pdb; pdb.set_trace()
        # L'errore completo è "L'articolo x non fa parte del lotto y."
        errore_aspettato = " non fa parte del lotto "
        self.assertContains(response, errore_aspettato, status_code=status.HTTP_400_BAD_REQUEST)

        # questo articolo so che è presente nel lotto...
        dati_movimento['articolo'] = "2"
        response = client.post(url_movimento_list, dati_movimento)
        self.assertTrue(response.status_code, status.HTTP_201_CREATED)

    def test_cancellazione_movimento_magazzino(self):
        """
        Verifica che funzioni l'API della cancellazione dei movimenti.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        movimenti_non_cancellati = Movimento.objects.filter(cancellato=False)
        n_movimenti_esistenti = len(movimenti_non_cancellati)
        # Devo prendere un movimento che sia possibile cancellare senza avere problemi 
        # di giacenze negative. Prendo il movimento con id=6 che è uno scarico.
        movimento = Movimento.objects.get(pk=6)
        url_movimento_detail = reverse('movimento-detail', args=(movimento.id,))
        response = client.delete(url_movimento_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         "API della cancellazione dei movimenti non funziona.")

        # ricarica il movimento dal db e verifica che risulti cancellato:
        movimento = Movimento.objects.get(pk=movimento.id)
        self.assertTrue(movimento.cancellato,
                        "Record del movimento non risulta cancellato logicamente.")
        
        url_movimento_list = reverse('movimento-list')
        response = client.get(url_movimento_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "API dell'elenco movimenti non funziona.")
        self.assertEqual(len(response.data), n_movimenti_esistenti-1,
                         "Dopo una cancellazione il numero di movimenti restituito dalle API non è corretto.")

    def test_movimenti_magazzino(self):
        """
        Verifica che l'API dell'elenco dei movimenti di magazzino funzionino (filtri inclusi).
        Usa 5 record dei movimenti inseriti nelle fixtures, da id 4 a id 8.
        """
        client = APIClient()
        url_movimento_list = reverse('movimento-list')
        response = client.get(url_movimento_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         "API che restituisce elenco dei movimenti non dovrebbe essere accessibile a tutti.")

        client.login(username='admin', password='nimda')
        response = client.get(url_movimento_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.all().count()
        self.assertNotEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                            "Il numero dei movimenti restituiti dalle API deve essere diverso dal numero di movimenti "
                            + "estratti dal database se non si considerano i movimenti cancellati.")

        numero_movimenti_da_db = Movimento.objects.non_cancellati().count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API deve essere uguale al numero di movimenti "
                         + "estratti dal database.")

        # filtro per id articolo
        parametro = 1
        response = client.get("{}?articolo={}".format(url_movimento_list, parametro))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(articolo=parametro).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per id articolo) deve essere uguale "
                         + "al numero di movimenti estratti dal database.")

        # filtro per codice articolo
        parametro = "GN0001"
        response = client.get("{}?articolo__codice={}".format(url_movimento_list, parametro))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(articolo__codice=parametro).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per codice articolo) deve essere "
                         + "uguale al numero di movimenti estratti dal database.")

        # filtro per id lotto
        parametro = "1"
        response = client.get("{}?lotto={}".format(url_movimento_list, parametro))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(lotto=parametro).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per id lotto) deve essere uguale "
                         + "al numero di movimenti estratti dal database.")

        # filtro per codice lotto
        parametro = "BF150001"
        response = client.get("{}?lotto__codice={}".format(url_movimento_list, parametro))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(lotto__codice=parametro).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per codice lotto) deve essere uguale "
                         + "al numero di movimenti estratti dal database.")

        # filtro per data da
        data_iniziale_str = "2016-03-08"
        response = client.get("{}?data_da={}".format(url_movimento_list, data_iniziale_str))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        data_iniziale = datetime(2016, 3, 8, 0, 0, 0)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(data__gte=data_iniziale).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per data iniziale) deve essere uguale"
                         + " al numero di movimenti estratti dal database.")

        # filtro per data a
        data_finale_str = "2016-03-08"
        response = client.get("{}?data_a={}".format(url_movimento_list, data_finale_str))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        data_finale = datetime(2016, 3, 8, 23, 59, 59)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(data__lte=data_finale).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per data finale) deve essere uguale "
                         + "al numero di movimenti estratti dal database.")

        # filtro per tipo movimento 
        parametro = "1"  # carico
        response = client.get("{}?tipo_movimento={}".format(url_movimento_list, parametro))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(tipo_movimento=parametro).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per tipo movimento) deve essere "
                         + "uguale al numero di movimenti estratti dal database.")

        # filtro per autore
        parametro = "1"  # admin
        response = client.get("{}?autore={}".format(url_movimento_list, parametro))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(autore=parametro).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per autore) deve essere uguale al "
                         + "numero di movimenti estratti dal database.")

        # filtro per id destinazione
        parametro = "0"
        response = client.get("{}?destinazione={}".format(url_movimento_list, parametro))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(destinazione=parametro).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per id destinazione) deve essere "
                         + "uguale al numero di movimenti estratti dal database.")

        # filtro per codice destinazione
        parametro = "15/0069"
        response = client.get("{}?destinazione__codice={}".format(url_movimento_list, parametro))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_movimenti_da_api = len(response.data)
        numero_movimenti_da_db = Movimento.objects.non_cancellati().filter(destinazione__codice=parametro).count()
        self.assertEqual(numero_movimenti_da_api, numero_movimenti_da_db,
                         "Il numero dei movimenti restituiti dalle API (filtrati per codice destinazione) deve essere"
                         + " uguale al numero di movimenti estratti dal database.")

        client.login(username='ut', password='ut')
        response = client.get(url_movimento_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Utente UT deve poter accedere alla API dei "
                         + "movimenti.")

    ####################################################################################################################
    # Test per controllare giacenze e scorte dopo la creazione di movimenti.
    ####################################################################################################################

    def test_movimenti_e_giacenze_01(self):
        """
        Scarico di 100 di un articolo (nessuna giacenza esistente).
        Deve segnalare errore perché non si può creare una giacenza con quantità negativa.
        Cambio il tipo di movimento e lo faccio diventare un carico.
        Rifaccio il movimento.
        La giacenza ora deve esistere.
        Ora faccio uno scarico di 30.
        La giacenza si deve aggiornare correttamente.
        Faccio un altro scarico di 70.
        La giacenza va cancellata.

        Tento di cancellare il carico, verificare di non avere errori durante la modifica della 
        giacenza (che è stata cancellata dal db perché dopo gli scarichi la quantità era 0).
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        lotto = BollaFornitore.objects.first()
        id_articolo = 2
        articolo = Articolo.objects.get(id=id_articolo)
        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 0, "Esiste già una giacenza per il lotto che voglio usare nei test e ciò non "
                         + "mi va bene.")
        self.assertEqual(articolo.scorta, 0), "All'inizio del test voglio che la scorta dell'articolo sia 0."
        
        n_movimenti_prima = Movimento.objects.all().count()
        # import pdb; pdb.set_trace()
        quantita = 100
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id),
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita,
            'tipo_movimento': str(scarico.id),
        }

        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, WmsValidationError.status_code, "La creazione di una giacenza dopo un "
                         + "movimento di scarico dovrebbe risultare in un errore.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 0, "Visto che la chiamata precedente è terminata con un errore, la giacenza "
                         + "dell\'articolo non dovrebbe esistere.")

        n_movimenti_dopo = Movimento.objects.all().count()
        self.assertEqual(n_movimenti_prima, n_movimenti_dopo, "Visto che la chiamata precedente è terminata "
                         + "con un errore, nemmeno il movimento dovrebbe essere stato creato.")

        ################################################################################################################
        # Carico al posto dello scarico.
        ################################################################################################################
        carico = TipoMovimento.objects.get(descrizione='Carico')
        dati_movimento['tipo_movimento'] = str(carico.id)

        response = client.post(url_movimento_list, dati_movimento)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Movimento non creato quando invece me lo "
                         + "aspettavo.")
        id_movimento_carico = response.data['id']

        n_movimenti_dopo = Movimento.objects.all().count()
        self.assertEqual(n_movimenti_prima+1, n_movimenti_dopo, "Visto che la chiamata precedente è terminata "
                         + "correttamente, ora mi aspetto di avere un movimento in più.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 1, "Giacenza non trovata.")
        self.assertEqual(giacenza[0].quantita, quantita, "Quantità della giacenza diversa da quella che mi aspettavo.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita, "Dopo il primo carico la scorta dell'articolo non è quella che mi "
                         + "aspettavo.")

        ################################################################################################################
        # Scarico di 30 pezzi.
        ################################################################################################################
        
        dati_movimento['tipo_movimento'] = str(scarico.id)
        dati_movimento['quantita'] = 30

        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Movimento non creato quando invece me lo "
                         + "aspettavo.")

        n_movimenti_dopo = Movimento.objects.all().count()
        self.assertEqual(n_movimenti_prima+2, n_movimenti_dopo, "Visto che la chiamata precedente è terminata "
                         + "correttamente, ora mi aspetto di avere 2 movimenti in più rispetto all'inizio.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 1, "Giacenza non trovata.")
        self.assertEqual(giacenza[0].quantita, quantita-30, "Quantità della giacenza diversa da quella che mi "
                         + "aspettavo.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita-30, "Dopo il secondo movimento la scorta dell'articolo non è "
                         + "quella che mi aspettavo.")

        ################################################################################################################
        # Scarico di 80 pezzi (deve fallire perché la giacenza è di 70).
        ################################################################################################################
        dati_movimento['quantita'] = 80
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, WmsValidationError.status_code,
                         "Lo scarico di una quantità maggiore rispetto alla giacenza disponibile deve fallire.")

        n_movimenti_dopo = Movimento.objects.all().count()
        self.assertEqual(n_movimenti_prima+2, n_movimenti_dopo,
                         "Visto che la chiamata precedente è terminata con un errore, ora mi aspetto di avere 2 "
                         "movimenti in più rispetto all'inizio.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 1, "Giacenza non trovata.")
        self.assertEqual(giacenza[0].quantita, quantita-30,
                         "Quantità della giacenza diversa da quella che mi aspettavo.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita-30, "Dopo il terzo movimento (che è fallito) la scorta dell'articolo"
                         + " deve essere uguale alla scorta dopo il secondo movimento.")

        ################################################################################################################
        # Scarico di 70 pezzi.
        ################################################################################################################
        
        dati_movimento['quantita'] = 70
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Movimento non creato quando invece me lo "
                         + "aspettavo.")

        n_movimenti_dopo = Movimento.objects.all().count()
        self.assertEqual(n_movimenti_prima+3, n_movimenti_dopo, "Visto che la chiamata precedente è terminata "
                         + "correttamente, ora mi aspetto di avere 3 movimenti in più rispetto all'inizio.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 0, "La giacenza a questo punto doveva essere cancellata.")
        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, 0, "Alla fine la scorta dell'articolo deve essere 0.")

        ################################################################################################################
        # Tentativo di cancellazione del carico.
        ################################################################################################################
        # Test aggiunto perché c'era un baco: nel controllo della giacenza a seguito della cancellazione
        # del carico, non si trovava il record visto che la giacenza è stata cancellata dopo gli scarichi.
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_carico,))
        response = client.delete(url_movimento_detail)
        self.assertEqual(response.status_code, WmsValidationError.status_code,
                         "La cancellazione del carico dovrebbe fallire perché genererebbe una giacenza negativa.")

    def test_movimenti_e_giacenze_02(self):
        """
        Carico di 300 di un articolo del lotto 1.
        Giacenza dell'articolo (lotto 1) deve essere 300.
        Scorta articolo deve essere 300.
        Carico di 100 di un articolo del lotto 2.
        Giacenza dell'articolo (lotto 1) deve essere 300.
        Giacenza dell'articolo (lotto 2) deve essere 100.
        Scorta articolo deve essere 400.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto1 = BollaFornitore.objects.first()
        # BF150002 - Gatti Precorvi:
        lotto2 = BollaFornitore.objects.get(id=3)
        id_articolo = 2
        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, 0), "All'inizio del test voglio che la scorta dell'articolo sia 0."

        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo)
        self.assertEqual(len(giacenza), 0, "Esiste già una giacenza per il lotto1 che voglio usare nei test e ciò non "
                         + "mi va bene.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto2, articolo=articolo)
        self.assertEqual(len(giacenza), 0, "Esiste già una giacenza per il lotto2 che voglio usare nei test e ciò non "
                         + "mi va bene.")

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 100
        carico = TipoMovimento.objects.get(descrizione='Carico')

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto1.id),
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1,
            'tipo_movimento': str(carico.id),
        }
        client.post(url_movimento_list, dati_movimento)

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1, "Dopo il primo movimento mi aspetto di avere una giacenza pari"
                         + " a quantita1.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1, "Dopo il primo carico la scorta dell'articolo non è quella che "
                         + "mi aspettavo.")

        ################################################################################################################
        # Secondo carico.
        ################################################################################################################
        dati_movimento['lotto'] = str(lotto2.id)
        dati_movimento['destinazione'] = str(lotto2.commessa.id)
        dati_movimento['quantita'] = quantita2
        client.post(url_movimento_list, dati_movimento)

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1, "Dopo il secondo carico mi aspetto che la quantita di giacenza1 "
                                                       "non sia cambiata.")

        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita2, "Quantità della giacenza relativa al secondo lotto diversa da "
                                                       "quella che mi aspettavo.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1+quantita2, "Dopo i due carichi la scorta dell'articolo è diversa "
                                                               "da quella che mi aspettavo.")

    def test_movimenti_e_giacenze_03(self):
        """
        Carico di 300
        La giacenza deve essere 300.
        La scorta dell'articolo deve essere 300.
        Scarico di 300
        La giacenza deve essere 0.
        La scorta dell'articolo deve essere 0.
        Modifica del primo carico in 290.
        Deve essere segnalato un errore.
        Giacenza e scorta devono quindi rimanere invariate.
        L'operaio si accorge che in magazzino ci sono ancora 10 pezzi e ci si rende conto che andava fatto un carico
        di 310.
        Modifica della quantità del primo carico.
        La giacenza deve essere 10.
        La scorta dell'articolo deve essere 10.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto = BollaFornitore.objects.first()
        id_articolo = 2
        articolo = Articolo.objects.get(id=id_articolo)
        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo siano uguali a 0, non lo faccio
        # anche qui...

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 300
        quantita1b = 290
        quantita1c = 310
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id),
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita1,
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_carico = response.data['id']

        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1, "Dopo il primo carico mi aspettavo di avere una giacenza pari a "
                                                       "quantita1.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1, "Dopo il primo carico la scorta dell'articolo non è quella che mi "
                                                     "aspettavo.")

        ################################################################################################################
        # Scarico.
        ################################################################################################################
        dati_movimento['tipo_movimento'] = str(scarico.id)
        dati_movimento['quantita'] = quantita2
        # non so se avrebbe più senso cambiare anche la destinazione dello scarico, ma per i test non cambia nulla...
        client.post(url_movimento_list, dati_movimento)

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), quantita1-quantita2, "Dopo lo scarico mi aspetto che la giacenza non ci sia "
                                                             "più.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1-quantita2, "Dopo lo scarico la scorta dell'articolo dovrebbe essere"
                                                               " 0.")

        ################################################################################################################
        # Modifica del carico che deve fallire.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_carico, ))
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita1b, 
            'tipo_movimento': str(carico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, WmsValidationError.status_code,
                         "La modifica del carico deve fallire perché ho già fatto uno scarico di una quantità "
                         "maggiore di quella che sto impostando.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 0, "Visto che la modifica del carico è fallita mi aspetto che la giacenza non "
                                           "ci sia nemmeno adesso.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita2-quantita1, "Visto che la modifica del carico è fallita mi aspetto "
                                                               "che la scorta sia ancora 0.")

        ################################################################################################################
        # Modifica del carico che deve andare bene.
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita1c, 
            'tipo_movimento': str(carico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "Errore durante l'aggiornamento di un movimento magazzino.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 1, "Dopo la modifica del carico mi aspetto che la giacenza ci sia.")
        self.assertEqual(giacenza[0].quantita, quantita1c-quantita2,
                         "Dopo la modifica del carico la giacenza del lotto dovrebbe essere 10.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1c-quantita2,
                         "Dopo la modifica del carico la scorta dell'articolo dovrebbe essere 10.")

    def test_movimenti_e_giacenze_04(self):
        """
        Carico di 300
        Scarico di 300
        La giacenza deve essere 0.
        La scorta dell'articolo deve essere 0.
        Modifico lo scarico e setto quantita = 400 --> deve essere segnalato l'errore.
        L'operaio si accorge che in magazzino ci sono ancora 20 pezzi e ci si rende conto che andava fatto uno scarico
        di 280 invece di 300.
        Modifica della quantità dello scarico.
        La giacenza deve essere 20.
        La scorta dell'articolo deve essere 20.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto = BollaFornitore.objects.first()
        id_articolo = 2
        articolo = Articolo.objects.get(id=id_articolo)
        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo siano uguali a 0, non lo faccio
        # anche qui...

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 400
        quantita3 = 280
        quantita4 = quantita1-quantita3
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        client.post(url_movimento_list, dati_movimento)

        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1, "Dopo il primo carico mi aspettavo di avere una giacenza pari "
                                                       "a quantita1.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1, "Dopo il primo carico la scorta dell'articolo non è quella che mi"
                                                     " aspettavo.")

        ################################################################################################################
        # Scarico.
        ################################################################################################################
        dati_movimento['tipo_movimento'] = str(scarico.id)
        # non so se avrebbe più senso cambiare anche la destinazione dello scarico, ma per i test non cambia nulla...
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_scarico = response.data['id']

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 0, "Dopo lo scarico mi aspetto che la giacenza non ci sia più.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, 0, "Dopo lo scarico la scorta dell'articolo dovrebbe essere 0.")

        ################################################################################################################
        # Modifica dello scarico che dovrebbe fallire.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_scarico, ))
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita2, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, WmsValidationError.status_code,
                         "La modifica dello scarico passando una quantità maggiore del carico dovrebbe fallire.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 0,
                         "Dopo la modifica FALLITA dello scarico mi aspetto che la giacenza non ci sia.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, 0,
                         "Dopo la modifica FALLITA dello scarico la scorta dell'articolo dovrebbe essere 0.")

        ################################################################################################################
        # Modifica dello scarico che dovrebbe andare bene.
        ################################################################################################################
        dati_movimento['quantita'] = quantita3 
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "La modifica dello scarico doveva andare bene in questo caso.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 1, "Dopo la modifica dello scarico mi aspetto che la giacenza sia stata creata"
                                           " di nuovo.")
        self.assertEqual(giacenza[0].quantita, quantita4, "Dopo la modifica dello scarico, la quantità della giacenza "
                                                          "deve essere uguale a {}.".format(quantita4))

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita4, "Dopo la modifica dello scarico, la quantità della giacenza deve "
                                                     "essere uguale a {}.".format(quantita4))

    def test_movimenti_e_giacenze_05(self):
        """
        Carico di 500
        Carico di 300
        Scorta deve essere 800
        Modifica del primo carico, quantita = 400 (meno del carico originale)
        Scorta deve essere 700.
        Modifica del primo carico, quantita = 600 (più del carico originale)
        Scorta deve essere 900.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto1 = BollaFornitore.objects.first()
        # BF150002 - Gatti Precorvi:
        lotto2 = BollaFornitore.objects.get(id=3)
        id_articolo = 2
        articolo = Articolo.objects.get(id=id_articolo)
        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo siano uguali a 0, non lo
        # faccio anche qui...

        # import pdb; pdb.set_trace()
        quantita1 = 500
        quantita2 = 300
        quantita1b = 400
        quantita1c = 600
        
        carico = TipoMovimento.objects.get(descrizione='Carico')
        # import pdb; pdb.set_trace()
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_carico1 = response.data['id']

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto2.id), 
            'destinazione': str(lotto2.commessa.id),
            'quantita': quantita2, 
            'tipo_movimento': str(carico.id),
        }
        client.post(url_movimento_list, dati_movimento)

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1+quantita2, "Dopo il secondo carico la scorta dell'articolo deve "
                                                               "essere la somma dei due carichi.")

        ################################################################################################################
        # Modifica del primo carico.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_carico1, ))
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1b, 
            'tipo_movimento': str(carico.id),
        }
        client.put(url_movimento_detail, dati_movimento)
        
        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1b+quantita2, "Dopo la modifica del primo carico la scorta "
                                                                "dell'articolo è diversa da quella che mi aspettavo.")

        ################################################################################################################
        # Modifica del primo carico con una quantità diversa.
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1c, 
            'tipo_movimento': str(carico.id),
        }
        client.put(url_movimento_detail, dati_movimento)

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1c+quantita2, "Dopo la modifica del primo carico la scorta "
                                                                "dell'articolo è diversa da quella che mi aspettavo.")

    ####################################################################################################################
    # Finora ho modificato carichi e scarichi. Ora testo la cancellazione di carichi e scarichi.
    ####################################################################################################################

    def test_movimenti_e_giacenze_06(self):
        """
        Carico di 300
        Scarico di 200
        Tento di cancellare il carico --> devo avere un errore
        Giacenza deve essere ancora 100.
        Scorta deve essere ancora 100.
        Cancello lo scarico
        Giacenza deve essere 300
        Scorta deve essere 300
        Cancello il carico.
        Giacenza non deve esistere.
        Scorta deve essere 0.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto = BollaFornitore.objects.first()
        id_articolo = 2
        articolo = Articolo.objects.get(id=id_articolo)
        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo siano uguali a 0, non lo
        # faccio anche qui...

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 200
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_carico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),   # dovrebbe essere diversa dal carico ma fa niente...
            'quantita': quantita2, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_scarico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ################################################################################################################
        # Tento di cancellare il carico.
        ################################################################################################################
        n_movimenti_prima = Movimento.objects.non_cancellati().count()
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_carico,))
        response = client.delete(url_movimento_detail)
        self.assertEqual(response.status_code, WmsValidationError.status_code,
                         "La cancellazione del carico dovrebbe fallire perché genererebbe una giacenza negativa")
        n_movimenti_dopo = Movimento.objects.non_cancellati().count()
        self.assertEqual(n_movimenti_prima, n_movimenti_dopo, "Il numero di moviementi non cancellati dovrebbe essere"
                                                              " lo stesso di prima.")
        self.assertFalse(Movimento.objects.get(pk=id_movimento_carico).cancellato, "Il movimento non dovrebbe "
                                                                                   "risultare cancellato.")

        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1-quantita2, "Visto che il carico non è stato cancellato, la "
                                                                 "giacenza dovrebbe essere invariata.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1-quantita2, "Visto che il carico non è stato cancellato, la scorta"
                                                               " dell'articolo dovrebbe essere invariata.")

        ################################################################################################################
        # Cancello lo scarico.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_scarico,))
        response = client.delete(url_movimento_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         "API della cancellazione dei movimenti non funziona.")
        n_movimenti_dopo = Movimento.objects.non_cancellati().count()
        self.assertEqual(n_movimenti_prima-1, n_movimenti_dopo, "Il movimento dello scarico non è stato cancellato.")
        self.assertTrue(Movimento.objects.get(pk=id_movimento_scarico).cancellato, "Il movimento dello scarico "
                                                                                   "dovrebbe risultare cancellato.")

        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1, "Visto che lo scarico è stato cancellato, la giacenza dovrebbe "
                                                       "essere uguale alla quantità del carico.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1, "Visto che lo scarico è stato cancellato, la scorta dell'articolo"
                                                     " dovrebbe essere uguale alla quantità del carico.")

        ################################################################################################################
        # Cancello il carico.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_carico,))
        response = client.delete(url_movimento_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         "Cancellazione movimento carico non effettuata.")
        n_movimenti_dopo = Movimento.objects.non_cancellati().count()
        self.assertEqual(n_movimenti_prima-2, n_movimenti_dopo, "Il movimento del carico non è stato cancellato.")
        self.assertTrue(Movimento.objects.get(pk=id_movimento_carico).cancellato, "Il movimento del carico dovrebbe"
                                                                                  " risultare cancellato.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo)
        self.assertEqual(len(giacenza), 0, "Visto che anche il carico è stato cancellato, la giacenza non dovrebbe"
                                           " esistere.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, 0, "Visto che anche il carico è stato cancellato, la scorta dell'articolo"
                                             " dovrebbe essere uguale a 0.")

    ####################################################################################################################
    # Test per verificare cosa succede quando si modifica l'articolo di un movimento.
    ####################################################################################################################

    def test_movimenti_e_giacenze_07(self):
        """
        Carico di 300 dell'articolo A.
        Giacenza di A deve essere 300.
        Scorta di A deve essere 300.
        Giacenza di B non deve esistere.
        Scorta di B uguale a 0.
        Modifico l'articolo A nel movimento e diventa B.
        Giacenza di A deve essere 0.
        Scorta di A deve essere 0.
        Giacenza di B deve essere 300.
        Scorta di B deve essere uguale a 300.
        Scarico di B di 200 pezzi.
        Giacenza di B deve essere 100.
        Scorta di B deve essere uguale a 100.
        Modifico il carico e setto articolo C al posto di B.
        La modifica deve fallire perché la giacenza di B diventerebbe negativa.
        Carico 500 pezzi di B con il lotto 2.
        Giacenza di B diventa 600.
        Scorta di B diventa 600.
        Tento di nuovo la modifica del primo carico settando C al posto di B.
        La modifica deve fallire di nuovo perché la giacenza del lotto 1, articolo B diventerebbe comunque negativa.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto1 = BollaFornitore.objects.first()
        lotto2 = BollaFornitore.objects.get(pk=4)
        id_articolo_a = 2
        id_articolo_b = 5
        id_articolo_c = 4
        articolo_a = Articolo.objects.get(id=id_articolo_a)
        articolo_b = Articolo.objects.get(id=id_articolo_b)
        articolo_c = Articolo.objects.get(id=id_articolo_c)

        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo A siano uguali a 0, non lo
        #  faccio anche qui...
        self.assertEqual(articolo_b.scorta, 0, "La scorta iniziale dell'articolo B deve essere uguale a 0.")
        self.assertFalse(Giacenza.objects.filter(articolo=articolo_b, lotto=lotto1).exists(),
                         "Non deve esistere una giacenza dell'articolo B per lotto1.")
        self.assertFalse(Giacenza.objects.filter(articolo=articolo_c, lotto=lotto1).exists(),
                         "Non deve esistere una giacenza dell'articolo C per lotto1.")
        self.assertFalse(Giacenza.objects.filter(lotto=lotto2).exists(), "Non devono esistere giacenze per lotto 2.")

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 200
        quantita3 = 500
        quantita_iniziale_articolo_c = articolo_c.scorta
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo_a.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_carico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_a)
        self.assertEqual(giacenza.quantita, quantita1, "La quantità relativa all'articolo A è diversa da quella che "
                                                       "mi aspettavo.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, quantita1,
                         "La scorta dell'articolo A è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_b)
        self.assertFalse(giacenza.exists(), "La giacenza di B non deve esistere.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, 0, "La scorta dell'articolo B deve essere ancora 0.")

        ################################################################################################################
        # Modifico l'articolo del carico.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_carico,))
        dati_movimento = {
            'articolo': str(articolo_b.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Errore durante la modifica dell'articolo del "
                                                                   "movimento di carico.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_a)
        self.assertFalse(giacenza.exists(), "La giacenza di A non deve esistere.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, 0, "La scorta dell'articolo A deve essere 0.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita1, "La quantità relativa all'articolo B è diversa da quella che "
                                                       "mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita1,
                         "La scorta dell'articolo B è diversa da quella che mi aspettavo.")

        ################################################################################################################
        # Scarico 200 pezzi dell'articolo B.
        ################################################################################################################
        
        dati_movimento = {
            'articolo': str(articolo_b.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),   # teoricamente dovrebbe cambiare ma non fa niente...
            'quantita': quantita2, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        # id_movimento_scarico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Scarico dell'articolo B non creato.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_a)
        self.assertFalse(giacenza.exists(), "La giacenza di A non deve esistere.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, 0, "La scorta dell'articolo A deve essere ancora 0.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita1-quantita2, "La quantità relativa all'articolo B deve essere "
                                                                 "diminuita perché ho fatto uno scarico.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita1-quantita2,
                         "La scorta dell'articolo B deve diminuire perché ho fatto uno scarico.")

        ################################################################################################################
        # Modifico di nuovo l'articolo del carico settando articolo C (deve fallire).
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo_c.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, WmsValidationError.status_code, "La modifica del carico deve fallire "
                                                                               "perché genera una giacenza negativa.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_a)
        self.assertFalse(giacenza.exists(), "La giacenza di A non deve esistere.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, 0, "La scorta dell'articolo A deve essere ancora 0.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita1-quantita2, "La quantità relativa all'articolo B è diversa da"
                                                                 " quella che mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita1-quantita2,
                         "La scorta dell'articolo B è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_c)
        self.assertFalse(giacenza.exists(), "La giacenza di C non deve esistere.")

        articolo_c = Articolo.objects.get(id=id_articolo_c)
        self.assertEqual(articolo_c.scorta, quantita_iniziale_articolo_c,
                         "La scorta dell'articolo C deve essere ancora 0.")

        ################################################################################################################
        # Carico altri 500 pezzi dell'Articolo B.
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo_b.id),
            'lotto': str(lotto2.id), 
            'destinazione': str(lotto2.commessa.id),
            'quantita': quantita3, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # id_movimento_carico = response.data['id']
        
        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_a)
        self.assertFalse(giacenza.exists(), "La giacenza di A non deve esistere.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, 0, "La scorta dell'articolo A deve essere ancora 0.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita1-quantita2, "La quantità relativa all'articolo B (lotto1) è "
                                                                 "diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita3, "La quantità relativa all'articolo B (lotto2) è diversa da"
                                                       " quella che mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita1-quantita2 + quantita3,
                         "La scorta dell'articolo B è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_c)
        self.assertFalse(giacenza.exists(), "La giacenza di C non deve esistere.")

        articolo_c = Articolo.objects.get(id=id_articolo_c)
        self.assertEqual(articolo_c.scorta, quantita_iniziale_articolo_c,
                         "La scorta dell'articolo C deve essere ancora 0.")

        ################################################################################################################
        # Modifico di nuovo l'articolo del carico settando articolo C (deve fallire di nuovo perché conta la giacenza,
        # non la scorta).
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo_c.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, WmsValidationError.status_code, "La modifica del carico deve fallire "
                                                                               "perché genera una giacenza negativa.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_a)
        self.assertFalse(giacenza.exists(), "La giacenza di A non deve esistere.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, 0, "La scorta dell'articolo A deve essere ancora 0.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita1-quantita2, "La quantità relativa all'articolo B (lotto1) è "
                                                                 "diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita3, "La quantità relativa all'articolo B (lotto2) è diversa da "
                                                       "quella che mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita1-quantita2 + quantita3,
                         "La scorta dell'articolo B è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_c)
        self.assertFalse(giacenza.exists(), "La giacenza di C non deve esistere.")

        articolo_c = Articolo.objects.get(id=id_articolo_c)
        self.assertEqual(articolo_c.scorta, quantita_iniziale_articolo_c,
                         "La scorta dell'articolo C deve essere ancora 0.")

    def test_movimenti_e_giacenze_08(self):
        """
        Carico di 300 dell'articolo A.
        Giacenza di A deve essere 300.
        Scorta di A deve essere 300.
        Carico di 1000 dell'articolo B.
        Giacenza di B deve essere 1000.
        Scorta di B deve essere 1000.
        
        Scarico di 100 dell'articolo A
        Giacenza di A deve essere 200.
        Scorta di A deve essere 200.
        Giacenza di B deve essere 1000.
        Scorta di B deve essere 1000.

        Modifico l'articolo A nel movimento di scarico e lo faccio diventare B.
        Giacenza di A deve essere 300.
        Scorta di A deve essere 300.
        Giacenza di B deve essere 900.
        Scorta di B deve essere 900.

        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto = BollaFornitore.objects.first()
        id_articolo_a = 2
        id_articolo_b = 3
        articolo_a = Articolo.objects.get(id=id_articolo_a)
        articolo_b = Articolo.objects.get(id=id_articolo_b)

        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo A siano uguali a 0, non lo
        #  faccio anche qui...
        # nel test 07 ho già controllato che la giacenza e la scorta di B sono pari a 0, non lo faccio anche qui...

        quantita1 = 300
        quantita2 = 1000
        quantita3 = 100
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo_a.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo_a)
        self.assertEqual(giacenza.quantita, quantita1, "La quantità relativa all'articolo A è diversa da quella che"
                                                       " mi aspettavo.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, quantita1,
                         "La scorta dell'articolo A è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.filter(lotto=lotto, articolo=articolo_b)
        self.assertFalse(giacenza.exists(), "La giacenza di B non deve esistere.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, 0, "La scorta dell'articolo B deve essere ancora 0.")

        ################################################################################################################
        # Carico l'articolo B.
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo_b.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita2, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo_a)
        self.assertEqual(giacenza.quantita, quantita1, "La quantità relativa all'articolo A è diversa da quella che"
                                                       " mi aspettavo.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, quantita1,
                         "La scorta dell'articolo A è diversa da quella che mi aspettavo.")
        
        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita2, "La quantità relativa all'articolo B è diversa da quella "
                                                       "che mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita2,
                         "La scorta dell'articolo B è diversa da quella che mi aspettavo.")

        ################################################################################################################
        # Scarico 100 pezzi dell'articolo A.
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo_a.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),   # teoricamente dovrebbe cambiare ma non fa niente...
            'quantita': quantita3, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_scarico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Scarico dell'articolo A non creato.")
        
        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo_a)
        self.assertEqual(giacenza.quantita, quantita1-quantita3, "La quantità relativa all'articolo A è diversa da "
                                                                 "quella che mi aspettavo.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, quantita1-quantita3,
                         "La scorta dell'articolo A è diversa da quella che mi aspettavo.")
        
        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita2, "La quantità relativa all'articolo B è diversa da quella che"
                                                       " mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita2,
                         "La scorta dell'articolo B è diversa da quella che mi aspettavo.")

        ################################################################################################################
        # Modifico l'articolo dello scarico settando articolo B.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_scarico,))
        dati_movimento = {
            'articolo': str(articolo_b.id),
            'lotto': str(lotto.id), 
            'destinazione': str(lotto.commessa.id),
            'quantita': quantita3, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Errore durante la modifica dell'articolo"
                                                                   " dello scarico.")
        
        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo_a)
        self.assertEqual(giacenza.quantita, quantita1, "La quantità relativa all'articolo A è diversa da quella "
                                                       "che mi aspettavo.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, quantita1,
                         "La scorta dell'articolo A è diversa da quella che mi aspettavo.")
        
        giacenza = Giacenza.objects.get(lotto=lotto, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita2-quantita3, "La quantità relativa all'articolo B è diversa "
                                                                 "da quella che mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita2-quantita3,
                         "La scorta dell'articolo B è diversa da quella che mi aspettavo.")

    ####################################################################################################################
    # Test per verificare cosa succede quando si modifica il lotto di un movimento.
    ####################################################################################################################

    def test_movimenti_e_giacenze_09(self):
        """
        Carico di 300 su lotto 1.
        Giacenza di articolo per lotto 1 deve essere 300.
        Scorta dell'articolo deve essere 300.
        Modifico carico settando lotto 2.
        Giacenza di articolo per lotto 1 non deve più esistere.
        Giacenza di articolo per lotto 2 deve essere uguale a 300.
        Scorta di Articolo deve essere ancora 300.
        Scarico 100 da lotto 2.
        Giacenza per lotto 2 deve diventare 200.
        Scorta articolo deve diventare 200.
        Modifico lotto del carico e setto lotto1 --> deve fallire perché la giacenza di lotto 2 diventerebbe negativa.
        Giacenza per lotto 1 non deve esistere perché la modifica del carico è fallita.
        Giacenza per lotto 2 deve essere uguale ancora a 200.
        Scorta dell'articolo deve essere uguale ancora a 200.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto1 = BollaFornitore.objects.first()
        lotto2 = BollaFornitore.objects.get(pk=4)
        commessa_per_scarichi = Commessa.objects.get(pk=2)
        id_articolo = 2
        articolo = Articolo.objects.get(id=id_articolo)

        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo A siano uguali a 0, non
        # lo faccio anche qui...
        self.assertFalse(Giacenza.objects.filter(articolo=articolo, lotto=lotto1).exists(),
                         "Non deve esistere una giacenza dell'articolo per lotto1.")
        self.assertFalse(Giacenza.objects.filter(articolo=articolo, lotto=lotto2).exists(),
                         "Non deve esistere una giacenza dell'articolo per lotto2.")

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 100
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_carico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1, "La quantità relativa all'articolo A (lotto 1) è diversa da "
                                                       "quella che mi aspettavo.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1, "La scorta dell'articolo A è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.filter(lotto=lotto2, articolo=articolo)
        self.assertFalse(giacenza.exists(), "La giacenza dell'articolo (lotto 2) non deve esistere.")

        ################################################################################################################
        # Modifico il lotto del carico.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_carico,))
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto2.id), 
            'destinazione': str(lotto2.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Errore durante la modifica del lotto del "
                                                                   "movimento di carico.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo)
        self.assertFalse(giacenza.exists(), "La giacenza di articolo (lotto1) non deve più esistere.")

        # articolo_a = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1, "La scorta dell'articolo deve rimanere uguale a prima.")

        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1, "La giacenza dell'articolo (lotto 2) deve essere uguale a "
                                                       "quella del carico.")

        ################################################################################################################
        # Scarico 100 pezzi da lotto 2.
        ################################################################################################################
        
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto2.id),
            'destinazione': str(commessa_per_scarichi.id),
            'quantita': quantita2,
            'tipo_movimento': str(scarico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Scarico dell'articolo da lotto 2 non creato.")
        
        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1-quantita2, "La quantità relativa al lotto 2 deve essere "
                                                                 "diminuita perché ho fatto uno scarico.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1-quantita2, "La scorta dell'articolo deve diminuire perché ho "
                                                               "fatto uno scarico.")

        ################################################################################################################
        # Modifico di nuovo il lotto del carico settando lotto1 (deve fallire).
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, WmsValidationError.status_code,
                         "La modifica del carico deve fallire perché genererebbe una giacenza negativa di lotto 2.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo)
        self.assertFalse(giacenza.exists(), "La giacenza di A non deve esistere.")

        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1-quantita2,
                         "La quantità relativa all'articolo (lotto2) è diversa da quella che mi aspettavo.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1-quantita2,
                         "La scorta dell'articolo dovrebbe rimanere uguale a prima.")

    def test_movimenti_e_giacenze_10(self):
        """
        Carico di 300 su lotto 1.
        Giacenza di articolo per lotto 1 deve essere 300.
        Scorta dell'articolo deve essere 300.
        Scarico di 100 da lotto1.
        Giacenza di articolo per lotto 1 deve essere 200.
        Scorta dell'articolo deve essere 200.

        Modifico scarico settando lotto 2 --> deve fallire.
        Giacenza di articolo per lotto 1 deve essere 200.
        Giacenza di articolo per lotto 2 non deve esistere.
        Scorta dell'articolo deve essere 200.
        
        Carico di 500 su lotto 2.
        Giacenza di articolo per lotto 1 deve essere 200.
        Giacenza di articolo per lotto 2 deve essere 500.
        Scorta dell'articolo deve essere 700.

        Modifico scarico settando lotto 2.
        Giacenza di articolo per lotto 1 deve essere 300.
        Giacenza di articolo per lotto 2 deve essere 400
        Scorta dell'articolo deve essere 700.

        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto1 = BollaFornitore.objects.first()
        lotto2 = BollaFornitore.objects.get(pk=4)
        commessa_per_scarichi = Commessa.objects.get(pk=2)
        id_articolo = 2
        articolo = Articolo.objects.get(id=id_articolo)

        self.assertFalse(Giacenza.objects.filter(articolo=articolo, lotto=lotto1).exists(),
                         "Non deve esistere una giacenza dell'articolo per lotto1.")
        self.assertFalse(Giacenza.objects.filter(articolo=articolo, lotto=lotto2).exists(),
                         "Non deve esistere una giacenza dell'articolo per lotto2.")

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 100
        quantita3 = 500
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1,
                         "La quantità relativa all'articolo (lotto 1) è diversa da quella che mi aspettavo.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1, "La scorta dell'articolo è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.filter(lotto=lotto2, articolo=articolo)
        self.assertFalse(giacenza.exists(), "La giacenza dell'articolo (lotto 2) non deve esistere.")

        ################################################################################################################
        # Scarico 100 pezzi da lotto 1.
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto1.id),
            'destinazione': str(lotto1.commessa.id),   # teoricamente dovrebbe cambiare ma non fa niente...
            'quantita': quantita2,
            'tipo_movimento': str(scarico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_scarico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Scarico dell'articolo da lotto 1 non creato.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1-quantita2, "La quantità relativa al lotto 1 deve essere"
                                                                 " diminuita perché ho fatto uno scarico.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto2, articolo=articolo)
        self.assertFalse(giacenza.exists(), "La giacenza relativa a lotto 2 non dovrebbe esistere.")
        
        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1-quantita2, "La scorta dell'articolo deve diminuire perché "
                                                               "ho fatto uno scarico.")

        ################################################################################################################
        # Modifico il lotto dello scarico (deve fallire perché non esiste il carico di lotto2).
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_scarico,))
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto2.id), 
            'destinazione': str(commessa_per_scarichi.id),
            'quantita': quantita2, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, WmsValidationError.status_code,
                         "La modifica dello scarico dovrebbe fallire.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1-quantita2,
                         "La giacenza di articolo (lotto1) dovrebbe essere uguale a prima.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto2, articolo=articolo)
        self.assertFalse(giacenza.exists(),
                         "La giacenza dell'articolo (lotto 2) non dovrebbe esistere perché non c'è mai stato "
                         "un carico.")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1-quantita2,
                         "La scorta dell'articolo deve rimanere uguale a prima.")

        ################################################################################################################
        # Carico 500 di articolo su lotto 2.
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto2.id), 
            'destinazione': str(lotto2.commessa.id),
            'quantita': quantita3, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1-quantita2,
                         "La quantità relativa all'articolo (lotto 1) rimane invariata.")

        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita3,
                         "La giacenza dell'articolo (lotto 2) dovrebbe essere uguale a 500")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1-quantita2+quantita3,
                         "La scorta dell'articolo dovrebbe essere uguale alla somma delle due giacenze.")

        ################################################################################################################
        # Modifico di nuovo il lotto dello scarico e questa volta deve andare bene.
        ################################################################################################################
        dati_movimento = {
            'articolo': str(articolo.id),
            'lotto': str(lotto2.id), 
            'destinazione': str(commessa_per_scarichi.id),
            'quantita': quantita2, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "La modifica dello scarico dovrebbe terminare con successo.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita1,
                         "La giacenza di articolo (lotto1) dovrebbe essere uguale al primo carico.")
        
        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo)
        self.assertEqual(giacenza.quantita, quantita3-quantita2,
                         "La giacenza dell'articolo (lotto 2) deve essere uguale al carico (500) - scarico (100).")

        articolo = Articolo.objects.get(id=id_articolo)
        self.assertEqual(articolo.scorta, quantita1 + quantita3-quantita2,
                         "La scorta dell'articolo è diversa da quella che mi aspettavo.")

    ####################################################################################################################
    # Test per verificare cosa succede quando si modificano l'articolo e la quantità di un movimento.
    ####################################################################################################################

    def test_movimenti_e_giacenze_11(self):
        """
        Carico di 300 dell'articolo_a.
        Giacenza di articolo_a deve essere 300.
        Scorta dell'articolo_a deve essere 300.
        Giacenza di articolo_b non deve esistere.
        Scorta articolo_b deve essere 0.
        Modifico carico settando articolo_b e quantità 500.
        Giacenza di articolo_a non deve più esistere.
        Scorta di ArticoloA deve essere 0.
        Giacenza di articolo_b deve essere uguale a 500.
        Scorta di articolo_b deve diventare 500.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto1 = BollaFornitore.objects.first()
        # lotto2 = BollaFornitore.objects.get(pk=4)
        id_articolo_a = 2
        id_articolo_b = 3
        articolo_a = Articolo.objects.get(id=id_articolo_a)
        articolo_b = Articolo.objects.get(id=id_articolo_b)

        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo A siano uguali a 0, non lo
        # faccio anche qui...
        self.assertFalse(Giacenza.objects.filter(articolo=articolo_a, lotto=lotto1).exists(),
                         "Non deve esistere una giacenza dell'articolo A per lotto1.")
        self.assertFalse(Giacenza.objects.filter(articolo=articolo_b, lotto=lotto1).exists(),
                         "Non deve esistere una giacenza dell'articolo B per lotto1.")
        self.assertEqual(articolo_b.scorta, 0, "Non deve esistere una scorta per l'articolo B.")

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 500
        carico = TipoMovimento.objects.get(descrizione='Carico')

        dati_movimento = {
            'articolo': str(articolo_a.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_carico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_a)
        self.assertEqual(giacenza.quantita, quantita1, "La quantità relativa all'articolo A (lotto 1) è diversa da "
                                                       "quella che mi aspettavo.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, quantita1,
                         "La scorta dell'articolo A è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_b)
        self.assertFalse(giacenza.exists(), "La giacenza dell'articolo B (lotto 2) non deve esistere.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, 0, "La scorta dell'articolo B dovrebbe essere 0.")

        ################################################################################################################
        # Modifico l'articolo e la quantità del carico.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_carico,))
        dati_movimento = {
            'articolo': str(articolo_b.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita2, 
            'tipo_movimento': str(carico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "Errore durante la modifica del lotto del movimento di carico.")
        
        giacenza = Giacenza.objects.filter(lotto=lotto1, articolo=articolo_a)
        self.assertFalse(giacenza.exists(), "La giacenza di articolo A (lotto1) non deve più esistere.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, 0, "La scorta dell'articolo A deve diventare 0.")

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita2,
                         "La giacenza dell'articolo B (lotto 1) deve essere uguale a quella del carico modificato.")
        
        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita2,
                         "La scorta dell'articolo B deve diventare uguale a quella del carico modificato.")

    def test_movimenti_e_giacenze_12(self):
        """
        Carico di 300 dell'articolo_a, lotto1.
        Carico di 500 dell'articolo_b, lotto2.
        Scarico di 100 dell'articolo_a da lotto1.
        Giacenza di articolo_a (lotto 1) deve essere 200.
        Scorta di articolo_a deve essere 200.
        Modifica dello scarico: quantità 50, articolo B e lotto 2.
        Giacenza di articolo_a (lotto 1) deve essere 300.
        Scorta dell'articolo_a deve essere 300.
        Giacenza di articolo_b (lotto 2) deve essere 450.
        Scorta articolo_b deve essere 450.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto1 = BollaFornitore.objects.first()
        lotto2 = BollaFornitore.objects.get(pk=4)
        commessa_per_scarichi = Commessa.objects.get(pk=2)
        id_articolo_a = 2
        id_articolo_b = 5
        articolo_a = Articolo.objects.get(id=id_articolo_a)
        articolo_b = Articolo.objects.get(id=id_articolo_b)

        # nei test 01 e 02 ho già controllato che la giacenza e la scorta dell'articolo A siano uguali a 0, non lo
        # faccio anche qui...
        self.assertFalse(Giacenza.objects.filter(articolo=articolo_a, lotto=lotto1).exists(),
                         "Non deve esistere una giacenza dell'articolo A per lotto1.")
        self.assertFalse(Giacenza.objects.filter(articolo=articolo_b, lotto=lotto2).exists(),
                         "Non deve esistere una giacenza dell'articolo B per lotto2.")
        self.assertEqual(articolo_b.scorta, 0, "Non deve esistere una scorta per l'articolo B.")

        # import pdb; pdb.set_trace()
        quantita1 = 300
        quantita2 = 500
        quantita3 = 100
        quantita4 = 50
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo_a.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita1, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        dati_movimento = {
            'articolo': str(articolo_b.id),
            'lotto': str(lotto2.id), 
            'destinazione': str(lotto2.commessa.id),
            'quantita': quantita2, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        dati_movimento = {
            'articolo': str(articolo_a.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita3, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_scarico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_a)
        self.assertEqual(giacenza.quantita, quantita1-quantita3,
                         "La quantità relativa all'articolo A (lotto 1) è diversa da quella che mi aspettavo.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, quantita1-quantita3,
                         "La scorta dell'articolo A è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita2,
                         "La quantità relativa all'articolo B (lotto 2) è diversa da quella che mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita2,
                         "La scorta dell'articolo B dovrebbe essere uguale a quella del suo carico.")

        ################################################################################################################
        # Modifico articolo, quantità e lotto dello scarico.
        ################################################################################################################
        url_movimento_detail = reverse('movimento-detail', args=(id_movimento_scarico,))
        dati_movimento = {
            'articolo': str(articolo_b.id),
            'lotto': str(lotto2.id), 
            'destinazione': str(commessa_per_scarichi.id),
            'quantita': quantita4, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.put(url_movimento_detail, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "Errore durante la modifica del lotto del movimento di scarico.")
        
        giacenza = Giacenza.objects.get(lotto=lotto1, articolo=articolo_a)
        self.assertEqual(giacenza.quantita, quantita1,
                         "La quantità relativa all'articolo A (lotto 1) deve essere uguale a quella del carico di "
                         "articolo A.")

        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, quantita1,
                         "La scorta dell'articolo A è diversa da quella che mi aspettavo.")

        giacenza = Giacenza.objects.get(lotto=lotto2, articolo=articolo_b)
        self.assertEqual(giacenza.quantita, quantita2-quantita4,
                         "La quantità relativa all'articolo B (lotto 2) è diversa da quella che mi aspettavo.")

        articolo_b = Articolo.objects.get(id=id_articolo_b)
        self.assertEqual(articolo_b.scorta, quantita2-quantita4,
                         "La scorta dell'articolo B è diversa da quella che mi aspettavo.")

    def test_movimenti_e_giacenze_13(self):
        """
        Carico di 300 dell'articolo_a, lotto1.
        Scarico di 300 dell'articolo_a, lotto1.
        Cancellazione scarico.
        Giacenza deve tornare ad essere 300.
        Test creato per risolvere issue #248
        E' un test simile a test_movimenti_e_giacenze_04 ma in quel caso non c'era la cancellazione
        dello scarico.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        url_movimento_list = reverse('movimento-list')
        # BF150001 - Gatti Precorvi:
        lotto1 = BollaFornitore.objects.first()
        # commessa_per_scarichi = Commessa.objects.get(pk=2)
        id_articolo_a = 2
        articolo_a = Articolo.objects.get(id=id_articolo_a)
        scorta_iniziale = articolo_a.scorta

        self.assertFalse(Giacenza.objects.filter(articolo=articolo_a, lotto=lotto1).exists(),
                         "Non deve esistere una giacenza dell'articolo A per lotto1.")

        # import pdb; pdb.set_trace()
        quantita = 300
        carico = TipoMovimento.objects.get(descrizione='Carico')
        scarico = TipoMovimento.objects.get(descrizione='Scarico')

        dati_movimento = {
            'articolo': str(articolo_a.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita, 
            'tipo_movimento': str(carico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        dati_movimento = {
            'articolo': str(articolo_a.id),
            'lotto': str(lotto1.id), 
            'destinazione': str(lotto1.commessa.id),
            'quantita': quantita, 
            'tipo_movimento': str(scarico.id),
        }
        response = client.post(url_movimento_list, dati_movimento)
        id_movimento_scarico = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertFalse(Giacenza.objects.filter(articolo=articolo_a, lotto=lotto1).exists(),
                         "La giacenza relativa all'articolo A (lotto 1) non dovrebbe esistere.")
        self.assertEqual(articolo_a.scorta, scorta_iniziale,
                         "La scorta dell'articolo A non deve essere cambiata rispetto all'inizio.")

        ################################################################################################################
        # Cancello lo scarico.
        ################################################################################################################
        movimento = Movimento.objects.get(pk=id_movimento_scarico)
        url_movimento_detail = reverse('movimento-detail', args=(movimento.id,))
        response = client.delete(url_movimento_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         "API della cancellazione dei movimenti non funziona.")

        giacenza_dopo_scarico = Giacenza.objects.get(articolo=articolo_a, lotto=lotto1)
        self.assertEqual(giacenza_dopo_scarico.quantita, quantita, "La giacenza relativa all'articolo A (lotto 1) \
            dovrebbe esistere ed essere pari alla quantità dello scarico cancellato.")
        articolo_a = Articolo.objects.get(id=id_articolo_a)
        self.assertEqual(articolo_a.scorta, scorta_iniziale + quantita,
                         "La scorta dell'articolo A deve essere cresciuta della quantità dello scarico cancellato.")
