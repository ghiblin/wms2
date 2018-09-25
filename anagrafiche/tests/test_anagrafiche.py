from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from anagrafiche.models import *

saltaQuestoTest = True


class AnagraficheTestCase(APITestCase):
    """
    Testa che sia possibile accedere ai dati dei dizionari.
    """

    fixtures = ['wms_data']

    def test_creazione_indirizzo(self):
        """
        Prendi un cliente a caso e usa le API per aggiungergli un indirizzo.
        """
        client = APIClient()
        client.login(username='admin', password='nimda')
        cliente = Entita.objects.filter(is_client=True).first()
        url_cliente_detail = reverse('cliente-detail', args=(cliente.id,))
        response = client.get(url_cliente_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        indirizzi_prima = len(response.data['indirizzi'])

        ################################################################################################################
        # Verifica i campi obbligatori
        ################################################################################################################
        dati_indirizzo = {}
        response = client.post('/api/v1/indirizzo/', dati_indirizzo)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = eval(response.content)
        self.assertTrue(type(errors) is dict)
        self.assertTrue('cap' in errors.keys())
        self.assertIn('obbligatorio', errors['cap'][0])
        self.assertTrue('via1' in errors.keys())
        self.assertIn('obbligatorio', errors['via1'][0])
        self.assertTrue('citta' in errors.keys())
        self.assertIn('obbligatorio', errors['citta'][0])
        self.assertTrue('provincia' in errors.keys())
        self.assertIn('obbligatorio', errors['provincia'][0])
        self.assertTrue('nazione' in errors.keys())
        self.assertIn('obbligatorio', errors['nazione'][0])
        self.assertTrue('entita' in errors.keys())
        self.assertIn('obbligatorio', errors['entita'][0])

        ################################################################################################################
        # Verifica che il campo 'via1' non possa essere una stringa vuota.
        ################################################################################################################
        dati_indirizzo = {
            'via1': ''
        }
        response = client.post('/api/v1/indirizzo/', dati_indirizzo)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = eval(response.content)
        self.assertTrue(type(errors) is dict)
        self.assertTrue('via1' in errors.keys())
        self.assertIn('essere omesso', errors['via1'][0])

        ################################################################################################################
        # Verifica che il campo 'cap' sia di 5 cifre e la provincia di 2 caratteri.
        ################################################################################################################
        dati_indirizzo = {
            'provincia': 'M',
            'cap': '1234'
        }
        response = client.post('/api/v1/indirizzo/', dati_indirizzo)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = eval(response.content)
        self.assertTrue(type(errors) is dict)
        self.assertTrue('cap' in errors.keys())
        self.assertIn('deve essere composto da 5 cifre', errors['cap'][0])
        self.assertTrue('provincia' in errors.keys())
        self.assertIn('deve contenere 2 lettere', errors['provincia'][0])
        
        dati_indirizzo = {
            'provincia': '1£',
            'cap': 'asdfg'
        }
        response = client.post('/api/v1/indirizzo/', dati_indirizzo)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = eval(response.content)
        self.assertTrue(type(errors) is dict)
        self.assertTrue('cap' in errors.keys())
        self.assertIn('deve essere composto da 5 cifre', errors['cap'][0])
        self.assertTrue('provincia' in errors.keys())
        self.assertIn('deve contenere 2 lettere', errors['provincia'][0])
        ################################################################################################################
        #  Verifica che l'indirizzo sia creato correttamente.
        ################################################################################################################
        dati_indirizzo = {
            'provincia': 'BG',
            'cap': '24126',
            'nazione': 'Italia',
            'entita': str(cliente.id),
            'citta': 'asdf',
            'via1': 'via roma xx',
            'tipo': SEDE_LEGALE
        }
        
        response = client.post('/api/v1/indirizzo/', dati_indirizzo)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        id_indirizzo = response.data['id']
        indirizzo = Indirizzo.objects.get(pk=id_indirizzo)
        indirizzo.cliente = cliente
        indirizzo.provincia = 'BG'
        indirizzo.cap = 24126
        indirizzo.citta = 'asdf'
        indirizzo.tipo = SEDE_LEGALE

        response = client.get(url_cliente_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        indirizzi_dopo = len(response.data['indirizzi'])
        self.assertEqual(indirizzi_prima + 1, indirizzi_dopo)
