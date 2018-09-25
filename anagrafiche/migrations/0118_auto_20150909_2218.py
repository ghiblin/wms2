# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0117_auto_20150818_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipopagamento',
            name='descrizione',
            field=models.CharField(max_length=200),
        ),
    ]
