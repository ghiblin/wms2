from rest_framework import status
from rest_framework.test import APITestCase  # , APIRequestFactory
from rest_framework.test import APIClient

from anagrafiche.models import *
from django.core.urlresolvers import reverse
from django.db.models import Q

saltaQuestoTest = True


class CommesseTestCase(APITestCase):
    """
    Test riguardanti le commesse.
    """

    fixtures = ['wms_data']

    def test_commesse_e_filtri(self):
        """
        Verifica che le API delle commesse restituiscano correttamente i record messi 
        nelle fixtures.
        """
        client = APIClient()
        url_commessa_list = reverse('commessa-list')
        response = client.get(url_commessa_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # import pdb; pdb.set_trace()

        client.login(username='admin', password='nimda')
        response = client.get(url_commessa_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_commesse_da_api = len(response.data)
        numero_commesse_da_db = Commessa.objects.non_cancellati().count()
        
        self.assertEqual(numero_commesse_da_api, numero_commesse_da_db, "Il numero delle commesse ottenute dalle API "
                         + "è diverso dal numero di commesse estratte dal database.")

        # filtro per id cliente
        response = client.get("{}?cliente=2".format(url_commessa_list))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_commesse_da_api = len(response.data)
        numero_commesse_da_db = Commessa.objects.non_cancellati().filter(cliente=2).count()
        self.assertEqual(numero_commesse_da_api, numero_commesse_da_db, "Il numero delle commesse filtrate per cliente"
                         + " dalle API è diverso dal numero di commesse estratte dal database.")

        # filtro per nome cliente (nei campi 'ragione sociale' e 'cognome')
        parametro_di_ricerca = "legno"   # cerca le commesse del cliente "Marlegno"
        response = client.get("{}?search={}".format(url_commessa_list, parametro_di_ricerca))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_commesse_da_api = len(response.data)
        numero_commesse_da_db = Commessa.objects.filter(Q(cliente__ragione_sociale__icontains=parametro_di_ricerca)
                                                        | Q(cliente__cognome__icontains=parametro_di_ricerca)).count()
        self.assertEqual(numero_commesse_da_api, numero_commesse_da_db, "Il numero delle commesse filtrate per nome "
                         + "cliente dalle API è diverso dal numero di commesse estratte dal database.")

        parametro_di_ricerca = "gasta"   # cerca le commesse del cliente "Martina Gastaldelli"
        response = client.get("{}?search={}".format(url_commessa_list, parametro_di_ricerca))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_commesse_da_api = len(response.data)
        numero_commesse_da_db = Commessa.objects.filter(Q(cliente__ragione_sociale__icontains=parametro_di_ricerca)
                                                        | Q(cliente__cognome__icontains=parametro_di_ricerca)).count()
        self.assertEqual(numero_commesse_da_api, numero_commesse_da_db, "Il numero delle commesse filtrate per nome "
                         + "cliente dalle API è diverso dal numero di commesse estratte dal database.")

        client.login(username='ut', password='ut')
        response = client.get(url_commessa_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Utente UT non riesce ad accedere alle API delle " '
                                                                   '+ "commesse.')
