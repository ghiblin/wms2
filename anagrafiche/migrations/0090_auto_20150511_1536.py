# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0089_auto_20150511_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordinecliente',
            name='persona_di_riferimento',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='preventivocliente',
            name='persona_di_riferimento',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
    ]
