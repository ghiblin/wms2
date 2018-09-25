# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0041_auto_20150304_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contocorrente',
            name='iban',
            field=models.CharField(max_length=32),
        ),
    ]
