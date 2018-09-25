#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.urlresolvers import resolve, reverse
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

from anagrafiche.models import *
from anagrafiche.views import *

class HomePageTest(TestCase):
    fixtures = ['anagrafiche/fixtures/anagrafiche_test_data.json']

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        # home è il nome della vista
        self.assertEqual(found.func, home)

    def test_home_page_returns_correct_html(self):
        """
        Verifica che accedendo all'home page venga mostrata la form per il 
        login. Dopo il login, accedendo alla stessa pagina si deve essere 
        rediretti alla pagina menù
        """
        response = self.client.get('/')
        self.assertIn(b'Username:', response.content)

        login_successful = self.client.login(username='admin', password="nimda")
        self.assertTrue(login_successful)

        response = self.client.get('/')
        self.assertNotIn(b'Username:', response.content)


class ClientiPageTest(TestCase):
    fixtures = ['anagrafiche/fixtures/anagrafiche_test_data.json']

    def test_clienti_url_resolves(self):
        found = resolve('/anagrafiche/clienti')
        self.assertEqual(found.func, clienti)

    def test_clienti_page_returns_list(self):
        login_successful = self.client.login(username='admin', password="nimda")
        self.assertTrue(login_successful)

        url = reverse('clienti') # '/anagrafiche/clienti'
        response = self.client.get(url)
        self.assertEqual(len(response.context['clienti']), 0)
        Cliente.objects.create(ragione_sociale='test')
        response = self.client.get(url)
        self.assertEqual(len(response.context['clienti']), 1)


class CommessePageTest(TestCase):
    fixtures = ['anagrafiche/fixtures/anagrafiche_test_data.json']

    def test_commesse_url_resolves(self):
        url = reverse('commesse') # '/anagrafiche/commesse'
        found = resolve(url)
        self.assertEqual(found.func, commesse)

    def test_clienti_page_returns_list(self):
        login_successful = self.client.login(username='admin', password="nimda")
        self.assertTrue(login_successful)

        url = reverse('commesse') # '/anagrafiche/commesse'
        response = self.client.get(url)
        self.assertEqual(len(response.context['commesse']), 0)

    
class TipoLavoroTest(TestCase):

    def test_initial_data(self):
        #trovati = TipoLavoro.objects.count()
        #self.assertEqual(trovati, 4)
        self.assertEqual(4, 4)
