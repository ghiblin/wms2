# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0150_dipendente_cellulare'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollafornitore',
            name='classe_di_corrosivita',
            field=models.CharField(default='C3', max_length=20),
        ),
    ]
