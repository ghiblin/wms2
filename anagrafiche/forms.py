#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from anagrafiche.models import *

class DateField(forms.DateField):
    input_type = 'date'


class ContoCorrenteForm(forms.ModelForm):
    """
    Tabella da utilizzare per creare o modificare un conto corrente di Mr Ferro
    """

    # aggiungo un campo in più alla model form in modo che questa form possa 
    # essere usata sia per la creazione che per la modifica di un record del 
    # modello Dipendente
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    class Meta:
        model = ContoCorrente
        fields = ['nome_banca', 'iban', 'straniero', 'predefinito', 'intestatario', 'filiale']


class CommessaForm(forms.ModelForm):
    """
    Tabella da utilizzare per creare o modificare una commessa
    """

    # aggiungo un campo in più alla model form in modo che questa form possa 
    # essere usata sia per la creazione che per la modifica di un record del 
    # modello Cliente
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super (CommessaForm,self ).__init__(*args,**kwargs)
        self.fields['cliente'].queryset = Cliente.objects.tutti()

    class Meta:
        model = Commessa
        fields = ['codice', 'cliente', 'data_apertura', 'prodotto']
        widgets = {
          'prodotto': forms.Textarea(attrs={'rows':1}),
        }


class DipendenteForm(forms.ModelForm):
    """
    Tabella da utilizzare per creare o modificare un dipendente
    """

    # aggiungo un campo in più alla model form in modo che questa form possa 
    # essere usata sia per la creazione che per la modifica di un record del 
    # modello Dipendente
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    class Meta:
        model = Dipendente
        fields = ['nome', 'cognome', 'matricola', 'costo_orario']


class ConsuntiviFilterForm(forms.Form):
    """
    Tabella da utilizzare per filtrare i consuntivi
    """

    da = DateField(required=False)
    a = DateField(required=False)
    """
    commessa = forms.ModelChoiceField(queryset=Commessa.objects.all(), \
        required=False)
    dipendente = forms.ModelChoiceField(queryset=Dipendente.objects.all() \
        , required=False)
    tipo_lavoro = forms.ModelChoiceField(queryset=TipoLavoro.objects.all() \
        , required=False)
    """


class ConsuntivoForm(forms.ModelForm):
    """
    Tabella da utilizzare per creare o modificare un consuntivo
    """

    # aggiungo un campo in più alla model form in modo che questa form possa 
    # essere usata sia per la creazione che per la modifica di un record del 
    # modello Consuntivo
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super (ConsuntivoForm,self ).__init__(*args,**kwargs)
        self.fields['commessa'].queryset = Commessa.objects.tutti()

    class Meta:
        model = Consuntivo
        fields = ['data', 'ore', 'tipo_lavoro', 'dipendente', 'commessa', 'note']
        widgets = {'dipendente': forms.HiddenInput()}

