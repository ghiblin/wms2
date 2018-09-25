# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafiche', '0104_bollacliente_rigabollacliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='bollacliente',
            name='persona_di_riferimento',
            field=models.CharField(default='', max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='rigabollacliente',
            name='riga_ordine',
            field=models.OneToOneField(null=True, blank=True, related_name='riga_bolla', to='anagrafiche.RigaOrdineCliente'),
        ),
    ]
