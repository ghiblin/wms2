# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0059_auto_20150312_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rigapreventivocliente',
            name='note',
            field=models.CharField(max_length=200, default='', blank=True),
        ),
    ]
