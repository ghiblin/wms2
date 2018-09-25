# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0029_auto_20150302_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contocorrente',
            name='entita',
            field=models.ForeignKey(to='anagrafiche.Entita', related_name='conti_correnti'),
        ),
    ]
