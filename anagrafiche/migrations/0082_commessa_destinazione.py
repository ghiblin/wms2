# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0081_auto_20150409_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='commessa',
            name='destinazione',
            field=models.ForeignKey(to='anagrafiche.Indirizzo', null=True, blank=True),
            preserve_default=True,
        ),
    ]
