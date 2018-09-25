# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0082_commessa_destinazione'),
    ]

    operations = [
        migrations.AddField(
            model_name='dipendente',
            name='diretto',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dipendente',
            name='interno',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
