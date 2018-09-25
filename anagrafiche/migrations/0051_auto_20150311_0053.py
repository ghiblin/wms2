# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0050_rigapreventivocliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articolo',
            name='unita_di_misura',
            field=models.CharField(choices=[('PZ', 'pezzi'), ('ME', 'metri'), ('CM', 'centimetri'), ('KG', 'chili'), ('HG', 'etti'), ('LI', 'litri'), ('SC', 'scatole')], max_length=2),
        ),
    ]
