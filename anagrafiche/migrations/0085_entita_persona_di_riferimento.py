# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0084_auto_20150427_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='entita',
            name='persona_di_riferimento',
            field=models.CharField(max_length=100, blank=True, null=True),
            preserve_default=True,
        ),
    ]
