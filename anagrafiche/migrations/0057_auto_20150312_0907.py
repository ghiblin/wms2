# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0056_auto_20150312_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articolo',
            name='unita_di_misura',
            field=models.CharField(choices=[('PZ', 'pezzi'), ('ME', 'metri'), ('M2', 'metri quadrati'), ('CM', 'centimetri'), ('KG', 'chili'), ('HG', 'etti'), ('LI', 'litri'), ('SC', 'scatole')], max_length=2),
        ),
    ]
