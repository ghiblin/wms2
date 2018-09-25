# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0149_auto_20160119_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='dipendente',
            name='cellulare',
            field=models.CharField(max_length=20, blank=True, null=True),
        ),
    ]
