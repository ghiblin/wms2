# -*- coding: utf-8 -*-


# Test creato con Selenium IDE. 
# Aprire firefox e poi dal menù Tools aprire Selenium IDE.
# Registrare un nuovo test ed esportarlo con "Export Test Case as..." e selezionare "Python 2 Web Driver".

# Per lanciare lo script bisogna prima caricare il VirtualEnv appropriato e poi lanciare il comando "python nome-script.py". Se si richiama lo script senza mettere 'python' davanti lo script non va.

# Nel virtual env, l'unica libreria installata è selenium:
# pip install selenium
# In ubuntu 14.04 c'è una versione bacata di pyvenv, vedere ~/virtualEnv/readme.txt

# Se si lancia lo script e si ottengono degli errori tipo 
# ResourceWarning: unclosed <socket.socket     o 
# selenium.common.exceptions.WebDriverException: Message: Can't load the profile.
# si può provare ad aggiornare la versione di selenium: quando l'ambiente virtuale
# è attivo lanciare   pip install -U selenium

# Il test generato da Selenium è scritto per python 2.x. Per farlo funzionare con 
# python 3.x effettuare le seguenti correzioni:
#
# Exception, e: return     deve essere corretto in:
# Exception: return
#
# Le correzioni sono da fare solo nei test nuovi, questo file è già a posto
#




from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class Test_UI(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(20)
        self.base_url = "http://localhost:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_preventivi(self):
        driver = self.driver
        driver.get(self.base_url + "#home")
        driver.find_element_by_xpath("(//a[contains(text(),'Mr. Ferro')])[2]").click()
        
        
        # Non so perché ma le istruzioni generate da selenium non funzionano
        # nel caso dello username. Devo quindi usare xpath. Per la password
        # invece non ci sono problemi... boh!!!
        #driver.find_element_by_name("username").clear()
        #driver.find_element_by_name("username").send_keys("admin")
        driver.find_element_by_xpath("//input[@name='username']").clear()
        driver.find_element_by_xpath("//input[@name='username']").send_keys("admin")

        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("nimda")
        driver.find_element_by_name("login").click()
        driver.find_element_by_link_text("Clienti").click()
        driver.find_element_by_link_text("Preventivi").click()

        ### Pagina preventivi aperta. verifica che non ci siano righe
        ### nella tabella delle righe del preventivo

        # import pdb; pdb.set_trace()

        n_righe_preventivo = len(driver.find_elements_by_xpath("//div[@id='rows-region']/table/tbody/tr"))
        assert n_righe_preventivo == 0, "Righe preventivo non sono vuote."

        driver.find_element_by_name("from").clear()
        # la data è stata scelta arbitrariamente. L'importante è selezionare un range
        # di date in modo di essere sicuri che ci sia almeno un preventivo:
        driver.find_element_by_name("from").send_keys("01 01 2000")
        driver.find_element_by_name("search").click()

        n_preventivi = len(driver.find_elements_by_xpath("//div[@id='master-region']/table/tbody/tr"))
        assert n_preventivi > 0, "Preventivi non trovati."

        ### seleziona il primo preventivo
        driver.find_element_by_xpath("//div[@id='master-region']/table/tbody/tr/td[2]").click()

        ### verificha che ci sia almeno una riga
        n_righe_preventivo = len(driver.find_elements_by_xpath("//div[@id='rows-region']/table/tbody/tr"))
        assert n_righe_preventivo > 0, "Righe preventivo non trovate."

        ### Verifica che il campo 'codice' sia valorizzato:
        # codice = driver.find_element_by_xpath("//input[@name='code']")
        codice = driver.find_element_by_xpath("//div[@id='details-region']//input[@name='code']")
        assert codice.get_attribute("value").startswith("PC"), "Campo 'codice' non valido."

        ### Verifica che il campo 'data' sia valorizzato e nella forma aaaa-mm-dd:
        data = driver.find_element_by_xpath("//div[@id='details-region']//input[@name='date']")
        data = data.get_attribute("value")
        assert re.match('\d{4}-\d{2}-\d{2}', data) != None, "Campo 'data' non valido."

        # logout
        driver.find_element_by_xpath("//ul[@id='login-region']/li/a").click()

    def test_ordini(self):
        driver = self.driver
        driver.get(self.base_url + "#home")
        driver.find_element_by_xpath("(//a[contains(text(),'Mr. Ferro')])[2]").click()
        
        
        # Non so perché ma le istruzioni generate da selenium non funzionano
        # nel caso dello username. Devo quindi usare xpath. Per la password
        # invece non ci sono problemi... boh!!!
        #driver.find_element_by_name("username").clear()
        #driver.find_element_by_name("username").send_keys("admin")
        driver.find_element_by_xpath("//input[@name='username']").clear()
        driver.find_element_by_xpath("//input[@name='username']").send_keys("admin")

        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("nimda")
        driver.find_element_by_name("login").click()
        driver.find_element_by_link_text("Clienti").click()
        driver.find_element_by_link_text("Ordini").click()

        ### Pagina ordini aperta. verifica che non ci siano righe
        ### nella tabella delle righe dell'ordine

        # import pdb; pdb.set_trace()

        n_righe_ordine = len(driver.find_elements_by_xpath("//div[@id='rows-region']/table/tbody/tr"))
        assert n_righe_ordine == 0, "Righe ordine non sono vuote."

        driver.find_element_by_name("from").clear()
        # la data è stata scelta arbitrariamente. L'importante è selezionare un range
        # di date in modo di essere sicuri che ci sia almeno un ordine:
        driver.find_element_by_name("from").send_keys("01 01 2000")
        driver.find_element_by_name("search").click()

        n_ordini = len(driver.find_elements_by_xpath("//div[@id='master-region']/table/tbody/tr"))
        assert n_ordini > 0, "Ordini non trovati."

        ### seleziona il primo ordine
        driver.find_element_by_xpath("//div[@id='master-region']/table/tbody/tr/td[2]").click()

        ### verificha che ci sia almeno una riga
        n_righe_ordine = len(driver.find_elements_by_xpath("//div[@id='rows-region']/table/tbody/tr"))
        assert n_righe_ordine > 0, "Righe ordine non trovate."

        ### Verifica che il campo 'codice' sia valorizzato:
        # codice = driver.find_element_by_xpath("//input[@name='code']")
        codice = driver.find_element_by_xpath("//div[@id='details-region']//input[@name='code']")
        assert codice.get_attribute("value").startswith("OC"), "Campo 'codice' non valido."

        ### Verifica che il campo 'data' sia valorizzato e nella forma aaaa-mm-dd:
        data = driver.find_element_by_xpath("//div[@id='details-region']//input[@name='date']")
        data = data.get_attribute("value")
        assert re.match('\d{4}-\d{2}-\d{2}', data) != None, "Campo 'data' non valido."

        # logout
        driver.find_element_by_xpath("//ul[@id='login-region']/li/a").click()
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
