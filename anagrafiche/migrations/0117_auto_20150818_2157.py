# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0116_auto_20150723_0125'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='totale_su_stampa',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preventivocliente',
            name='totale_su_stampa',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
