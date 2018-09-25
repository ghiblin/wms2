# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0097_auto_20150519_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordinecliente',
            name='disegni_costruttivi',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordinecliente',
            name='relazione_di_calcolo',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
