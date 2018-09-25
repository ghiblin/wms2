# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0007_auto_20150128_0848'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='partita_iva',
            field=models.CharField(max_length=12, default=''),
            preserve_default=True,
        ),
    ]
