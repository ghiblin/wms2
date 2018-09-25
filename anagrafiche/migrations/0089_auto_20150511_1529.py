# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0088_rigaordinecliente_riga_preventivo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='persona_di_riferimento',
            field=models.CharField(null=True, max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='persona_di_riferimento',
            field=models.CharField(null=True, max_length=100, blank=True),
            preserve_default=True,
        ),
    ]
