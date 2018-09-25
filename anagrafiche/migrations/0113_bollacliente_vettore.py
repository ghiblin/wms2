# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0112_entita_vettore'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollacliente',
            name='vettore',
            field=models.ForeignKey(related_name='bolle_trasportate', null=True, to='anagrafiche.Entita', blank=True),
            preserve_default=True,
        ),
    ]
