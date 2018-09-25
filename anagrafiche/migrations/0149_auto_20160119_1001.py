# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0148_auto_20151204_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollacliente',
            name='persona_di_riferimento',
            field=models.CharField(blank=True, max_length=150, default=''),
        ),
        migrations.AddField(
            model_name='bollafornitore',
            name='persona_di_riferimento',
            field=models.CharField(blank=True, max_length=150, default=''),
        ),
        migrations.AddField(
            model_name='fatturacliente',
            name='persona_di_riferimento',
            field=models.CharField(blank=True, max_length=150, default=''),
        ),
        migrations.AddField(
            model_name='fatturafornitore',
            name='persona_di_riferimento',
            field=models.CharField(blank=True, max_length=150, default=''),
        ),
        migrations.AlterField(
            model_name='ordinecliente',
            name='persona_di_riferimento',
            field=models.CharField(blank=True, max_length=150, default=''),
        ),
        migrations.AlterField(
            model_name='ordinefornitore',
            name='persona_di_riferimento',
            field=models.CharField(blank=True, max_length=150, default=''),
        ),
    ]
