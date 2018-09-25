# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0026_entita'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entita',
            name='ragione_sociale',
            field=models.CharField(null=True, max_length=60, blank=True),
        ),
    ]
