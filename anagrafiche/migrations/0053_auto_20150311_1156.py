# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0052_ordinecliente_rigaordinecliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rigaordinecliente',
            name='preventivo',
            field=models.ForeignKey(to='anagrafiche.PreventivoCliente', null=True, blank=True, related_name='righe_ordine'),
        ),
    ]
