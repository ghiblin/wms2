# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0102_auto_20150604_0353'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventivocliente',
            name='commessa',
            field=models.ForeignKey(related_name='preventivi', null=True, to='anagrafiche.Commessa', blank=True),
            preserve_default=True,
        ),
    ]
