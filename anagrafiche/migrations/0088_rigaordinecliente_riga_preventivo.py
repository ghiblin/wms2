# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0087_rigaordinecliente_articolo_unita_di_misura'),
    ]

    operations = [
        migrations.AddField(
            model_name='rigaordinecliente',
            name='riga_preventivo',
            field=models.ForeignKey(blank=True, related_name='riga_ordine', to='anagrafiche.RigaPreventivoCliente', null=True),
            preserve_default=True,
        ),
    ]
