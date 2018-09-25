#!/usr/bin/python
# -*- coding: utf-8 -*-

from casper.tests import CasperTestCase
import os.path

class MyTest(CasperTestCase):
    fixtures = ['wms_data']

    def test_articoli(self):
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                'casper-tests/articoli.js')))

    # creo un secondo test per verificare che tra un test e l'altro 
    # il database è ripulito. va cancellato quando si aggiungono altri test
    # più sensati.
    def test_articoli_2(self):
        self.assertTrue(self.casper(
            os.path.join(os.path.dirname(__file__),
                'casper-tests/articoli.js')))
