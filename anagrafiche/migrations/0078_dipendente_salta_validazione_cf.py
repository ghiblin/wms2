# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0077_auto_20150401_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='dipendente',
            name='salta_validazione_cf',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
