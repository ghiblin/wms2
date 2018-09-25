# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0123_rigafatturacliente_riga_bolla'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aliquotaiva',
            name='descrizione',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='aliquotaiva',
            name='percentuale',
            field=models.DecimalField(max_digits=5, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='articolo',
            name='descrizione',
            field=models.CharField(max_length=70),
        ),
        migrations.AlterField(
            model_name='articolo',
            name='prezzo_di_listino',
            field=models.DecimalField(max_digits=13, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='articolo',
            name='ss',
            field=models.DecimalField(null=True, max_digits=12, blank=True, decimal_places=2, help_text='scorta di sicurezza'),
        ),
        migrations.AlterField(
            model_name='classearticolo',
            name='descrizione',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='consuntivo',
            name='ore',
            field=models.DecimalField(validators=[django.core.validators.MaxValueValidator(12), django.core.validators.MinValueValidator(0.5)], max_digits=7, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='contatto',
            name='custom_label',
            field=models.CharField(null=True, blank=True, max_length=40, help_text='Etichetta da usare se tipo contatto = personalizzato'),
        ),
        migrations.AlterField(
            model_name='contatto',
            name='valore',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='contocorrente',
            name='filiale',
            field=models.CharField(null=True, blank=True, max_length=80),
        ),
        migrations.AlterField(
            model_name='contocorrente',
            name='intestatario',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='contocorrente',
            name='nome_banca',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='dipendente',
            name='costo_orario',
            field=models.DecimalField(max_digits=6, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='dipendente',
            name='nome',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='entita',
            name='costo_riba',
            field=models.DecimalField(max_digits=6, decimal_places=2, default=0),
        ),
        migrations.AlterField(
            model_name='entita',
            name='persona_di_riferimento',
            field=models.CharField(null=True, blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='fatturacliente',
            name='totale',
            field=models.DecimalField(max_digits=15, decimal_places=2, default=0),
        ),
        migrations.AlterField(
            model_name='indirizzo',
            name='citta',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='indirizzo',
            name='via1',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='indirizzo',
            name='via2',
            field=models.CharField(null=True, blank=True, max_length=80),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='classe_di_esecuzione',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='oggetto',
            field=models.CharField(null=True, blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='sconto_euro',
            field=models.DecimalField(max_digits=12, decimal_places=2, default=0),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='sconto_percentuale',
            field=models.DecimalField(max_digits=6, decimal_places=2, default=0),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='spessori',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='tipo_di_acciaio',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='totale',
            field=models.DecimalField(max_digits=15, decimal_places=2, default=0),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='verniciatura',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='wps',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='zincatura',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='classe_di_esecuzione',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='oggetto',
            field=models.CharField(null=True, blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='persona_di_riferimento',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='spessori',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='tipo_di_acciaio',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='totale',
            field=models.DecimalField(max_digits=15, decimal_places=2, default=0),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='verniciatura',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='wps',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='zincatura',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='rigabollacliente',
            name='note',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='rigabollacliente',
            name='quantita',
            field=models.DecimalField(max_digits=15, verbose_name='quantità', decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigafatturacliente',
            name='articolo_prezzo',
            field=models.DecimalField(max_digits=13, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigafatturacliente',
            name='quantita',
            field=models.DecimalField(max_digits=15, verbose_name='quantità', decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigafatturacliente',
            name='totale',
            field=models.DecimalField(max_digits=15, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='articolo_prezzo',
            field=models.DecimalField(max_digits=13, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='note',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='quantita',
            field=models.DecimalField(max_digits=15, verbose_name='quantità', decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='totale',
            field=models.DecimalField(max_digits=15, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='articolo_prezzo',
            field=models.DecimalField(max_digits=13, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='note',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='quantita',
            field=models.DecimalField(max_digits=15, verbose_name='quantità', decimal_places=2),
        ),
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='totale',
            field=models.DecimalField(max_digits=15, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='tipopagamento',
            name='descrizione',
            field=models.CharField(max_length=250),
        ),
    ]
