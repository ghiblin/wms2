# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0046_auto_20150306_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preventivocliente',
            name='codice',
            field=models.CharField(max_length=9),
        ),
    ]
