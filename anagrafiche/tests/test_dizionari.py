from rest_framework import status
from rest_framework.test import APITestCase  # , APIRequestFactory

from rest_framework.test import APIClient
from anagrafiche.models import *
from django.core.urlresolvers import reverse

saltaQuestoTest = True


class DizionariTestCase(APITestCase):
    """
    Testa che sia possibile accedere ai dati dei dizionari.
    """
    fixtures = ['wms_data']

    def test_get_tipoPagamento(self):
        # verifico che ci sia almeno un tipo pagamento perché così so
        # che le fixtures sono state caricate correttamente.
        client = APIClient()
        response = client.get('/api/v1/tipoPagamento/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_lista_tipo_movimento(self):
        """
        Verifica che funzioni l'api che restituisce l'elenco dei tipi movimento.        
        """
        tipi_movimenti = TipoMovimento.objects.all()        
        client = APIClient()
        # client.login(username='admin', password='nimda')
        response = client.get(reverse('tipomovimento-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_record_api = len(response.data)
        self.assertNotEqual(numero_record_api, 0, "Tabella TipoMovimento è vuota!")
        self.assertEqual(len(tipi_movimenti), numero_record_api, "Numero dei record restituiti dall'API non è uguale "
                         + "al numero di record nel database.")
