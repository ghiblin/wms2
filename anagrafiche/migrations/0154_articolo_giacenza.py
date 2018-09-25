# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0153_tipomovimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='articolo',
            name='giacenza',
            field=models.IntegerField(default=0),
        ),
    ]
