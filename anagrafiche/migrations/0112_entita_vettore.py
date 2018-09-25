# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0111_auto_20150714_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='entita',
            name='vettore',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
