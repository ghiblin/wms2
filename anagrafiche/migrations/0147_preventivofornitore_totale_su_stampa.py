# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0146_auto_20151127_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventivofornitore',
            name='totale_su_stampa',
            field=models.BooleanField(default=True),
        ),
    ]
