# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0027_auto_20150302_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commessa',
            name='cliente',
            field=models.ForeignKey(to='anagrafiche.Entita'),
        ),
        migrations.AlterField(
            model_name='contocorrente',
            name='cliente',
            field=models.ForeignKey(null=True, related_name='conti_correnti', to='anagrafiche.Entita', blank=True),
        ),
    ]
